import asyncio
import csv
import os
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

OUT = f'logs/test_runs/{datetime.now():%Y-%m-%d_%H%M%S}_telemetry.csv'
SECONDS = int(os.environ.get('TELEMETRY_SECONDS', '120'))


async def one_position(drone):
    async for pos in drone.telemetry.position():
        return pos


async def watch_mode(drone, state):
    async for mode in drone.telemetry.flight_mode():
        state['mode'] = str(mode).split('.')[-1]


async def watch_pv(drone, state):
    async for pv in drone.telemetry.position_velocity_ned():
        state['pv'] = pv


async def watch_attitude(drone, state):
    async for att in drone.telemetry.attitude_euler():
        state['roll'] = att.roll_deg
        state['pitch'] = att.pitch_deg
        state['yaw'] = att.yaw_deg


async def watch_armed(drone, state):
    async for armed in drone.telemetry.armed():
        state['armed'] = armed


async def main():
    drone = System()
    await drone.connect(system_address='udp://:14540')

    print('Connecting...', flush=True)
    async for st in drone.core.connection_state():
        if st.is_connected:
            print('Connected', flush=True)
            break

    print('Waiting for GPS...', flush=True)
    async for h in drone.telemetry.health():
        if h.is_global_position_ok and h.is_home_position_ok:
            print('GPS ready', flush=True)
            break

    home = await one_position(drone)
    home_abs = home.absolute_altitude_m
    print('home abs alt =', home_abs, flush=True)

    state = {
        'mode': '',
        'armed': None,
        'roll': None,
        'pitch': None,
        'yaw': None,
        'pv': None,
    }
    tasks = [
        asyncio.create_task(watch_mode(drone, state)),
        asyncio.create_task(watch_pv(drone, state)),
        asyncio.create_task(watch_attitude(drone, state)),
        asyncio.create_task(watch_armed(drone, state)),
    ]

    while (
        not state['mode']
        or state['roll'] is None
        or state['armed'] is None
        or state['pv'] is None
    ):
        await asyncio.sleep(0.1)

    with open(OUT, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['t_s', 'rel_alt_m', 'abs_alt_m', 'north_m', 'east_m',
                         'vn', 've', 'vd', 'roll_deg', 'pitch_deg', 'yaw_deg',
                         'armed', 'mode'])
        t0 = time.monotonic()
        for i in range(SECONDS):
            delay = t0 + i - time.monotonic()
            if delay > 0:
                await asyncio.sleep(delay)

            pv = state['pv']
            rel = -pv.position.down_m
            writer.writerow([
                i,
                round(rel, 3),
                round(home_abs + rel, 3),
                round(pv.position.north_m, 3),
                round(pv.position.east_m, 3),
                round(pv.velocity.north_m_s, 3),
                round(pv.velocity.east_m_s, 3),
                round(pv.velocity.down_m_s, 3),
                round(state['roll'], 3) if state['roll'] is not None else '',
                round(state['pitch'], 3) if state['pitch'] is not None else '',
                round(state['yaw'], 3) if state['yaw'] is not None else '',
                state['armed'] if state['armed'] is not None else '',
                state['mode'],
            ])
            f.flush()
    for t in tasks:
        t.cancel()
    print('saved', OUT, flush=True)


asyncio.run(main())
