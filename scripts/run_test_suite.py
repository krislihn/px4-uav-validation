import asyncio
import csv
import time
from datetime import datetime

from mavsdk import System

import sys


def _quiet_unraisable(unraisable):
    text = f'{unraisable.object!r} {unraisable.exc_value!r}'
    if 'WrappedIterator' in text or 'cannot join current thread' in text:
        return
    sys.__unraisablehook__(unraisable)


sys.unraisablehook = _quiet_unraisable

TS = datetime.now().strftime('%Y-%m-%d_%H%M%S')
SUITE_CSV = f'logs/test_runs/{TS}_suite.csv'
LOG_TXT = f'logs/test_runs/{TS}_suite.log'
STABLE_N = 3

results = []
log_lines = []


def log(msg):
    print(msg, flush=True)
    log_lines.append(f'{time.monotonic():.2f}  {msg}')


async def first(gen, timeout=5.0):
    async def _inner():
        async for item in gen:
            return item
    try:
        return await asyncio.wait_for(_inner(), timeout)
    except asyncio.TimeoutError:
        return None


def add(case_id, name, expected, actual, ok):
    results.append((case_id, name, expected, actual, 'PASS' if ok else 'FAIL'))
    log(f'{case_id} {"PASS" if ok else "FAIL"}  {actual}')


def save():
    with open(SUITE_CSV, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['case_id', 'name', 'expected', 'actual', 'verdict'])
        for row in results:
            w.writerow(row)
    with open(LOG_TXT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log_lines) + '\n')
    passed = sum(1 for r in results if r[4] == 'PASS')
    print(f'{passed}/{len(results)} PASS')
    print(f'saved {SUITE_CSV}')
    print(f'saved {LOG_TXT}')


async def ensure_grounded(drone):
    p = await first(drone.telemetry.position(), 3)
    rel = p.relative_altitude_m if p else None
    in_air = await first(drone.telemetry.in_air(), 3)
    armed = await first(drone.telemetry.armed(), 3)
    log(f'precheck: rel_alt={rel} in_air={in_air} armed={armed}')
    if rel is not None and rel > 0.5:
        log('precheck: landing before test')
        await drone.action.land()
        t0 = time.monotonic()
        while time.monotonic() - t0 < 30:
            p = await first(drone.telemetry.position(), 1)
            if p and p.relative_altitude_m <= 0.2:
                break
    if await first(drone.telemetry.armed(), 2):
        try:
            await drone.action.disarm()
            log('precheck: disarmed')
        except Exception as e:
            log(f'precheck: disarm failed: {e}')


async def safe_finish(drone):
    try:
        p = await first(drone.telemetry.position(), 3)
        if p and p.relative_altitude_m > 0.3:
            log('cleanup: landing')
            await drone.action.land()
            await asyncio.sleep(12)
        if await first(drone.telemetry.armed(), 2):
            await drone.action.disarm()
            log('cleanup: disarmed')
    except Exception as e:
        log(f'cleanup: {e}')


async def main(drone):
    await drone.connect(system_address='udp://:14540')

    st = await first(drone.core.connection_state(), 10)
    ok = st is not None and st.is_connected
    add('TC-01', '连接检查', '10 秒内 is_connected=True',
        'connected' if ok else 'no connection', ok)
    if not ok:
        return

    samples = []
    t0 = time.monotonic()
    async for pv in drone.telemetry.position_velocity_ned():
        samples.append(time.monotonic() - t0)
        if len(samples) >= 8 or time.monotonic() - t0 > 15:
            break
    increasing = all(b > a for a, b in zip(samples, samples[1:]))
    add('TC-02', '遥测连续', '15 秒内 >=8 个样本且时间递增',
        f'samples={len(samples)} increasing={increasing}',
        len(samples) >= 8 and increasing)

    ready = False
    t0 = time.monotonic()
    while time.monotonic() - t0 < 30:
        h = await first(drone.telemetry.health(), 1)
        if h and h.is_global_position_ok and h.is_home_position_ok:
            ready = True
            break
    if not ready:
        add('TC-00', '定位就绪', 'global + home position ok', 'not ready', False)
        return

    await ensure_grounded(drone)

    home = await first(drone.telemetry.position(), 5)
    if home is None:
        add('TC-00', '定位就绪', '能读到位置', 'no position', False)
        return
    home_abs = home.absolute_altitude_m
    log(f'home abs alt = {home_abs:.2f}')

    await drone.action.arm()
    armed = await first(drone.telemetry.armed(), 5)
    add('TC-03', '解锁', '5 秒内 armed=True', f'armed={armed}', bool(armed))

    await drone.action.set_takeoff_altitude(2.5)
    await drone.action.takeoff()
    stable = 0
    rel = None
    t0 = time.monotonic()
    while time.monotonic() - t0 < 20:
        p = await first(drone.telemetry.position(), 1)
        if p:
            rel = p.relative_altitude_m
            if rel >= 2.0:
                stable += 1
                if stable >= STABLE_N:
                    break
            else:
                stable = 0
    add('TC-04', '起飞到 2.5 m', '20 秒内连续 3 次 rel_alt >= 2.0 m',
        f'rel_alt={rel:.2f} m, stable={stable}', stable >= STABLE_N)

    log('TC-05: settling 5 s before window')
    await asyncio.sleep(5)
    alts, norths, easts = [], [], []
    t0 = time.monotonic()
    while time.monotonic() - t0 < 20:
        pv = await first(drone.telemetry.position_velocity_ned(), 1)
        if pv:
            alts.append(-pv.position.down_m)
            norths.append(pv.position.north_m)
            easts.append(pv.position.east_m)
    if len(alts) >= 5:
        drift = max(((n - norths[0]) ** 2 + (e - easts[0]) ** 2) ** 0.5
                    for n, e in zip(norths, easts))
        ok = min(alts) >= 2.0 and max(alts) <= 3.0 and drift <= 0.5
        actual = f'alt {min(alts):.2f}-{max(alts):.2f} m, drift {drift:.2f} m'
    else:
        ok = False
        actual = f'only {len(alts)} samples'
    add('TC-05', '悬停稳定', 'alt 2.0-3.0 m, drift <= 0.5 m', actual, ok)

    base = await first(drone.telemetry.position_velocity_ned(), 3)
    if base is None:
        add('TC-06', '航点到达', '能读到当前位置', 'no position', False)
    else:
        target_north = base.position.north_m + 11.13
        target_east = base.position.east_m
        await drone.action.goto_location(home.latitude_deg + 0.0001,
                                         home.longitude_deg, home_abs + 2.5, 0)
        stable = 0
        actual = 'timeout'
        t0 = time.monotonic()
        while time.monotonic() - t0 < 30:
            pv = await first(drone.telemetry.position_velocity_ned(), 1)
            if pv:
                h_err = ((pv.position.north_m - target_north) ** 2
                         + (pv.position.east_m - target_east) ** 2) ** 0.5
                a_err = abs(-pv.position.down_m - 2.5)
                actual = f'h_err={h_err:.2f} m, alt_err={a_err:.2f} m'
                if h_err <= 1.0 and a_err <= 0.5:
                    stable += 1
                    if stable >= STABLE_N:
                        break
                else:
                    stable = 0
        add('TC-06', '航点到达', '连续 3 次 h_err <= 1.0 m, alt_err <= 0.5 m',
            actual, stable >= STABLE_N)

    await drone.action.land()
    stable = 0
    actual = 'timeout'
    t0 = time.monotonic()
    while time.monotonic() - t0 < 30:
        p = await first(drone.telemetry.position(), 1)
        if p:
            rel = p.relative_altitude_m
            actual = f'rel_alt={rel:.2f} m'
            if rel <= 0.2:
                stable += 1
                if stable >= STABLE_N:
                    break
            else:
                stable = 0
    add('TC-07', '降落', '连续 3 次 rel_alt <= 0.2 m', actual, stable >= STABLE_N)

    try:
        await drone.action.disarm()
    except Exception as e:
        log(f'disarm: {e}')


async def run():
    drone = System()
    try:
        await main(drone)
    except Exception as e:
        log(f'FATAL: {e}')
        await safe_finish(drone)
    finally:
        save()


asyncio.run(run())
