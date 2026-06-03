import asyncio
import json
import websockets


TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb25lczRAZXhhbXBsZS5jb20iLCJ1c2VyX2lkIjoyLCJleHAiOjE3ODA1MzA4ODd9.AXumxX3xcvmwH42bsYpKeHxZMSFZlaAnUc07MPuT_ag"


async def receive_messages(websocket):
    try:
        async for message in websocket:
            print("\nReceived:", message)
            print("Message type (chat/code/exit): ", end="", flush=True)
    except websockets.exceptions.ConnectionClosed:
        print("\nConnection closed by server.")


async def send_messages(websocket):
    while True:
        message_type = await asyncio.to_thread(
            input,
            "Message type (chat/code/exit): "
        )

        if message_type.lower() == "exit":
            print("Closing connection...")
            await websocket.close()
            break

        if message_type.lower() == "chat":
            content = await asyncio.to_thread(input, "Chat message: ")
            payload = {
                "type": "chat_message",
                "content": content
            }

        elif message_type.lower() == "code":
            content = await asyncio.to_thread(input, "Code update: ")
            payload = {
                "type": "code_update",
                "content": content
            }

        else:
            print("Invalid option. Use chat, code, or exit.")
            continue

        await websocket.send(json.dumps(payload))


async def test_websocket():
    uri = f"ws://127.0.0.1:8001/ws/rooms/1?token={TOKEN}"

    async with websockets.connect(uri, ping_interval=None) as websocket:
        print("Connected to room 1")

        await asyncio.gather(
            receive_messages(websocket),
            send_messages(websocket)
        )


asyncio.run(test_websocket())