import asyncio
import websockets


async def test_websocket():
    uri = "ws://127.0.0.1:8001/ws/rooms/1"

    async with websockets.connect(uri) as websocket:
        await websocket.send("Hello interview room")

        response = await websocket.recv()

        print(response)


asyncio.run(test_websocket())