import asyncio
import csv
import time

from mavsdk import System

OUT = 'logs/test_runs/2026-10-16_alt_probe.csv'


async def one_position(drone):
    async for pos in drone.telemetry.position():
        return pos


async def trace(drone, seconds):
    with open(OUT, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['t_s', 'rel_alt_m', 'abs_alt_m'])
        t0 = time.monotonic()
        while time.monotonic() - t0 < seconds:
            pos = await one_position(drone)
            writer.writerow([round(time.monotonic() - t0, 2),
                             round(pos.relative_altitude_m, 3),
                             round(pos.absolute_altitude_m, 3)])
            f.flush()
            await asyncio.sleep(1)


async def main():
    drone = System()
    await drone.connect(system_address='udp://:14540')

    async for state in drone.core.connection_state():
        if state.is_connected:
            break
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            break

    pos = await one_position(drone)
    home_lat = pos.latitude_deg
    home_lon = pos.longitude_deg
    print('home:', home_lat, home_lon, 'abs_alt=', pos.absolute_altitude_m)

    tracer = asyncio.create_task(trace(drone, 60))

    await drone.action.set_takeoff_altitude(2.5)
    await drone.action.arm()
    print('armed')
    await drone.action.takeoff()
    print('takeoff sent')
    await asyncio.sleep(10)

    pos = await one_position(drone)
    print('after takeoff: rel=', pos.relative_altitude_m, 'abs=', pos.absolute_altitude_m)

    print('goto_location with 10.0 (as absolute altitude)')
    await drone.action.goto_location(home_lat, home_lon, 10.0, 0)
    await asyncio.sleep(15)

    pos = await one_position(drone)
    print('after goto: rel=', pos.relative_altitude_m, 'abs=', pos.absolute_altitude_m)

    await drone.action.land()
    await asyncio.sleep(12)
    await drone.action.disarm()
    tracer.cancel()
    print('done')


if __name__ == '__main__':
    asyncio.run(main())

