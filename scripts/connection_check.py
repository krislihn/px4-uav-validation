import asyncio
from mavsdk import System

async def run():
    drone = System()
    await drone.connect(system_address='udp://:14540')
    print('Waiting for drone...')
    async for state in drone.core.connection_state():
        if state.is_connected:
            print('Drone connected!')
            break
    async for health in drone.telemetry.health():
        print('GPS ok:', health.is_global_position_ok)
        break
    async for pos in drone.telemetry.position():
        print('Lat:', pos.latitude_deg, 'Lon:', pos.longitude_deg)
        break
    print('Test passed!')

asyncio.run(run())
