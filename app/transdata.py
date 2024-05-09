import asyncio
import websockets
import threading
import json
import os
import vf_gpio

gpio = vf_gpio.gpio_mn()


async def handle_client(websocket, path):
    print(f"Client connected: {websocket.remote_address}")
    mode = await websocket.recv()
    print(f"Mode: {mode}")
    try:
        if mode == "real":
            while True:
                data = gpio.read()
                if data:
                    message = json.dumps({
                        "temperature": data.temp,
                        "co2": data.co2,
                        "light": data.light,
                    })
                else:
                    message = "down"
                print(f"Sending message: {message}")
                try:
                    await websocket.send(message)
                    await asyncio.sleep(1)  # 每秒发送一次消息
                except websockets.exceptions.ConnectionClosedError:
                    break
                print(f"Client disconnected: {websocket.remote_address}")

        elif mode == "history":
            data = gpio.history("general")
            dic = {}
            i = 0
            for piece in data:
                dic['table' + str(i)] = piece[0]
                i = i + 1
            message = json.dumps(dic)
            await websocket.send(message)

        elif mode[:4] == "data":
            dic = {}
            i = 0
            table = mode
            # data = ((datetime.datetime(2024, 5, 2, 16, 55), 18733.0, 323360.0, 64161.0), ...)
            data = gpio.history("detail", table)
            print(f"after return: {data}")
            for piece in data:
                dic['time' + str(i)] = piece[0].strftime('%Y-%m-%d %H:%M:%S')
                dic['temp' + str(i)] = piece[1]
                dic['co2' + str(i)] = piece[2]
                dic['light' + str(i)] = piece[3]
                i = i + 1
            print(f"dic: {dic}")
            message = json.dumps(dic)
            print(f"Sending message: {message}")
            await websocket.send(message)
            await websocket.close()

        elif mode == "control":
            while True:
                message = await websocket.recv()
                gpio.write(message)

        else:
            print("Invalid mode")

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
    os.system('npm start')
