import asyncio
from mavsdk import System
from mavsdk import telemetry
import csv
import time

async def run():
    drone = System()
    await drone.connect(system_address='udp://:14540')
    print('Connecting to drone...')
    async for state in drone.core.connection_state():
        if state.is_connected:
            print('Drone connected!')
            break

    print('Waiting for GPS...')
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print('GPS ready')
            break

    home_lat = 0
    home_lon = 0
    async for pos in drone.telemetry.position():
        home_lat = pos.latitude_deg
        home_lon = pos.longitude_deg
        home_abs = pos.absolute_altitude_m
        print('Home:', home_lat, home_lon)
        break

    print('-- Arming --')
    await drone.action.arm()
    await asyncio.sleep(2)

    print('-- Taking off --')
    await drone.action.takeoff()
    await asyncio.sleep(8)

    waypoints = [
        (home_lat + 0.0001, home_lon, 10.0),
        (home_lat + 0.0001, home_lon + 0.0001, 10.0),
        (home_lat, home_lon + 0.0001, 10.0),
    ]

    results = []
    for i, (lat, lon, alt) in enumerate(waypoints):
        print(f'Going to waypoint {i+1}')
        await drone.action.goto_location(lat, lon, home_abs + alt, 0)
        await asyncio.sleep(10)
        async for pos in drone.telemetry.position():
            error_lat = abs(pos.latitude_deg - lat)
            error_lon = abs(pos.longitude_deg - lon)
            error_alt = abs(pos.relative_altitude_m - alt)
            results.append({'wp': i+1, 'lat_err': error_lat, 'lon_err': error_lon, 'alt_err': error_alt})
            print(f'WP{i+1} errors: lat={error_lat:.6f} lon={error_lon:.6f} alt={error_alt:.2f}')
            break

    print('-- Returning to launch --')
    await drone.action.return_to_launch()
    await asyncio.sleep(15)

    print('-- Landing --')
    await drone.action.land()
    await asyncio.sleep(10)

    print('-- Disarming --')
    try:
        await drone.action.disarm()
    except Exception as e:
        print("disarm failed:", e)

    with open('flight_results.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['wp', 'lat_err', 'lon_err', 'alt_err'])
        writer.writeheader()
        writer.writerows(results)
    print('Results saved to flight_results.csv')
    print('Mission complete!')

asyncio.run(run())
