import asyncio
import json
import sys
import websockets

from config import SD_BASE_URL as BASE_URL


async def restart_server():
    print("Close both screens and restart start.bat again.")
    input()
    sys.exit()
    # URL = f'ws://{BASE_URL.split("//")[-1]}/queue/join'
    # async with websockets.connect(URL) as websocket:
    #     response = await websocket.recv()
    #     response = json.loads(response)
    #     print(response)
    #     if response != {'msg': 'send_hash'}:
    #         print("Error Restarting Stable Diffusion Server")
    #         return
    #     fn_index = 1392
    #     session_hash = "utr90w1ne4o"
    #     print(f"fn_index : {fn_index}")
    #     await websocket.send(json.dumps({"fn_index": fn_index,
    #                                      "session_hash": session_hash
    #                                      }))
    #     await websocket.recv()
    #     response = await websocket.recv()
    #     response = json.loads(response)
    #     print(response)
    #     if response != {"msg": "send_data"}:
    #         print("Error Restarting Stable Diffusion Server")
    #         return
    #     await websocket.send(json.dumps({"fn_index": fn_index,
    #                                      "session_hash": session_hash,
    #                                      "data": [
    #                                          "[]",
    #                                          "[]",
    #                                          "none"
    #                                      ],
    #                                      "event_data": None,
    #                                      }))
    #     print(await websocket.recv())

async def main():
    await restart_server()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())