import asyncio
import websockets
import threading
import time
import json
import vf_gpio

gpio = vf_gpio.gpio_mn()


async def handle_client(websocket, path):
    print(f"Client connected: {websocket.remote_address}")
    try:
        while True:
            data = gpio.read()
            if data:
                json_data = {
                    "temperature": data.temp,
                    "co2": data.co2,
                    "light": data.light,
                }
                message = json.dumps(json_data)
                print(f"Sending message: {message}")
                await websocket.send(message)
            else:
                print("gpio server is down")
                message = "down"
                await websocket.send(message)
            await asyncio.sleep(1)  # 每秒发送一次消息
    except websockets.exceptions.ConnectionClosedError:
        print(f"Client disconnected: {websocket.remote_address}")


async def start_server():
    async with websockets.serve(handle_client, None, 18765):
        print("Server started")
        await asyncio.Future()  # Keeps the server running


def start_websocket_server():
    asyncio.run(start_server())


if __name__ == '__main__':
    gpio.gpio_server("start", 10)
    # 启动WebSocket服务器
    thread = threading.Thread(target=start_websocket_server)
    thread.start()
    while True:
        time.sleep(3)
