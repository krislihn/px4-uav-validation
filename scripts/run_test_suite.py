import asyncio
import csv
import time
from datetime import datetime

from mavsdk import System

TS = datetime.now().strftime('%Y-%m-%d_%H%M%S')
SUITE_CSV = f'logs/test_runs/{TS}_suite.csv'
LOG_TXT = f'logs/test_runs/{TS}_suite.log'

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


async def main():
    drone = System()
    await drone.connect(system_address='udp://:14540')

    st = await first(drone.core.connection_state(), 10)
    ok = st is not None and st.is_connected
    add('TC-01', '连接检查', '10 秒内 is_connected=True',
        'connected' if ok else 'no connection', ok)
    if not ok:
        save()
        return

    samples = []
    t0 = time.monotonic()
    async for pv in drone.telemetry.position_velocity_ned():
        samples.append(time.monotonic() - t0)
        if len(samples) >= 8 or time.monotonic() - t0 > 15:
            break
    increasing = all(b > a for a, b in zip(samples, samples[1:]))
    ok = len(samples) >= 8 and increasing
    add('TC-02', '遥测连续', '15 秒内 >=8 个样本且时间递增',
        f'samples={len(samples)} increasing={increasing}', ok)

    ready = False
    t0 = time.monotonic()
    while time.monotonic() - t0 < 30:
        h = await first(drone.telemetry.health(), 1)
        if h and h.is_global_position_ok and h.is_home_position_ok:
            ready = True
            break
    if not ready:
        add('TC-00', '定位就绪', 'global + home position ok', 'not ready', False)
        save()
        return

    home = await first(drone.telemetry.position(), 5)
    if home is None:
        add('TC-00', '定位就绪', '能读到位置', 'no position', False)
        save()
        return
    home_abs = home.absolute_altitude_m
    log(f'home abs alt = {home_abs:.2f}')

    await drone.action.arm()
    armed = await first(drone.telemetry.armed(), 5)
    add('TC-03', '解锁', '5 秒内 armed=True', f'armed={armed}', bool(armed))

    await drone.action.set_takeoff_altitude(2.5)
    await drone.action.takeoff()
    reached = False
    rel = None
    t0 = time.monotonic()
    while time.monotonic() - t0 < 20:
        p = await first(drone.telemetry.position(), 1)
        if p:
            rel = p.relative_altitude_m
            if rel >= 2.0:
                reached = True
                break
    add('TC-04', '起飞到 2.5 m', '20 秒内 rel_alt >= 2.0 m',
        f'rel_alt={rel:.2f} m' if rel is not None else 'no data', reached)

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

    target_north = 0.0001 * 111320.0
    await drone.action.goto_location(home.latitude_deg + 0.0001,
                                     home.longitude_deg, home_abs + 2.5, 0)
    ok = False
    actual = 'timeout'
    t0 = time.monotonic()
    while time.monotonic() - t0 < 30:
        pv = await first(drone.telemetry.position_velocity_ned(), 1)
        if pv:
            h_err = ((pv.position.north_m - target_north) ** 2
                     + pv.position.east_m ** 2) ** 0.5
            a_err = abs(-pv.position.down_m - 2.5)
            actual = f'h_err={h_err:.2f} m, alt_err={a_err:.2f} m'
            if h_err <= 1.0 and a_err <= 0.5:
                ok = True
                break
    add('TC-06', '航点到达', 'h_err <= 1.0 m, alt_err <= 0.5 m', actual, ok)

    await drone.action.land()
    ok = False
    actual = 'timeout'
    t0 = time.monotonic()
    while time.monotonic() - t0 < 30:
        p = await first(drone.telemetry.position(), 1)
        if p:
            rel = p.relative_altitude_m
            actual = f'rel_alt={rel:.2f} m'
            if rel <= 0.2:
                ok = True
                break
    add('TC-07', '降落', '30 秒内 rel_alt <= 0.2 m', actual, ok)

    try:
        await drone.action.disarm()
    except Exception as e:
        log(f'disarm: {e}')

    save()


asyncio.run(main())
