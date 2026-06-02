import asyncio
import json
import websockets


async def receive_messages(websocket):
    try:
        async for message in websocket:
            print("\nReceived:", message)
            print("Type message: ", end="", flush=True)
    except websockets.exceptions.ConnectionClosed:
        print("\nConnection closed by server.")


async def send_messages(websocket):
    while True:
        message = await asyncio.to_thread(input, "Type message: ")

        if message.lower() == "exit":
            print("Closing connection...")
            await websocket.close()
            break

        payload = {
            "type": "chat_message",
            "content": message
        }

        await websocket.send(json.dumps(payload))


async def test_websocket():
    uri = "ws://127.0.0.1:8001/ws/rooms/1"

    async with websockets.connect(uri, ping_interval=None) as websocket:
        print("Connected to room 1")

        await asyncio.gather(
            receive_messages(websocket),
            send_messages(websocket)
        )


asyncio.run(test_websocket())