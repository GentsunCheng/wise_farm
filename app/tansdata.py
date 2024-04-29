import asyncio
import websockets
import threading
import time
import json

import random

async def handle_client(websocket, path):
    print(f"Client connected: {websocket.remote_address}")
    try:
        while True:
            data = {
                "temperature": random.randint(0, 30),
                "co2": random.randint(0, 30),
                "light": random.randint(0, 30)
            }
            message = json.dumps(data)
            print(f"Sending message: {message}")
            await websocket.send(message)
            await asyncio.sleep(1)  # 每秒发送一次消息
    except websockets.exceptions.ConnectionClosedError:
        print(f"Client disconnected: {websocket.remote_address}")


async def start_server():
    async with websockets.serve(handle_client, None, 8765):
        print("Server started")
        await asyncio.Future()  # Keeps the server running


def start_websocket_server():
    asyncio.run(start_server())


if __name__ == '__main__':
    # 启动WebSocket服务器
    thread = threading.Thread(target=start_websocket_server)
    thread.start()
    while True:
        time.sleep(3)
