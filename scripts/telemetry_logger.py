import asyncio
import csv
import time

from mavsdk import System

OUT = 'logs/test_runs/2026-10-21_ground_test.csv'
SECONDS = 60


async def one_position(drone):
    async for pos in drone.telemetry.position():
        return pos


async def one_pv(drone):
    async for s in drone.telemetry.position_velocity_ned():
        return s


async def watch_mode(drone, state):
    async for mode in drone.telemetry.flight_mode():
        state['mode'] = str(mode).split('.')[-1]


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

    state = {'mode': ''}
    mode_task = asyncio.create_task(watch_mode(drone, state))




    while not state['mode']:
        await asyncio.sleep(0.1)

    with open(OUT, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['t_s', 'rel_alt_m', 'abs_alt_m', 'north_m', 'east_m',
                         'vn', 've', 'vd', 'mode'])
        t0 = time.monotonic()
        while time.monotonic() - t0 < SECONDS:
            pv = await one_pv(drone)
            rel = -pv.position.down_m
            writer.writerow([
                round(time.monotonic() - t0, 2),
                round(rel, 3),
                round(home_abs + rel, 3),
                round(pv.position.north_m, 3),
                round(pv.position.east_m, 3),
                round(pv.velocity.north_m_s, 3),
                round(pv.velocity.east_m_s, 3),
                round(pv.velocity.down_m_s, 3),
                state['mode'],
            ])
            f.flush()
            await asyncio.sleep(1)

    mode_task.cancel()
    print('saved', OUT, flush=True)


asyncio.run(main())
