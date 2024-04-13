import asyncio
import sys

from aiohttp import request

from config import METEX_URL
from config import VER
from apis.gpu import get_gpu

headers = {
    "version": VER
}


async def test():
    async with request("POST","https://httpbin.org/get") as res:
        print(res.status)


async def create_session():
    global headers
    url = METEX_URL + "/v3/host/create"
    gpu = get_gpu()
    data = {
        "gpu_name": gpu.name,
        "gpu_uuid": gpu.uuid,
        "gpu_total_memory": int(gpu.memoryTotal),
    }
    async with request("POST",url,json=data,headers=headers) as res:
        if res.status!=200:
            print("Error Creating Session")
            print(await res.json())
        response = await res.json()
        host_session_id = response.get("host_session_id")
        headers.update({"host-session-id": host_session_id})
        print(f"Assigned Session : {host_session_id}")

async def get_host():
    url = METEX_URL + "/v2/host"
    async with request("GET",url,headers=headers) as res:
        if res.status!=200:
            raise Exception("Error Getting Host")
        return await res.json()


async def set_wallet_id(wallet_id):
    url = METEX_URL + "/v2/host/set-wallet-id"
    data = {
        "wallet_id": wallet_id
    }
    async with request("POST",url,json=data,headers=headers) as res:
        if res.status!=200:
            raise Exception("Error Setting Wallet Id")
        return await res.json()

async def ping_online():
    url = METEX_URL+"/v3/host/ping"
    async with request("POST",url,headers=headers) as res:
        pass


async def submit_image(data):
    url = METEX_URL + "/v3/host/submit"
    async with request("POST",url,json=data,headers=headers) as res:
        if res.status!=200:
            print("Error Creating Session")
            print(await res.json())
        print("Image submitted successfully")
        return await res.json()


async def assign_image():

    url = METEX_URL + "/v3/host/assign"
    async with request("POST",url,headers=headers) as res:
        if res.status == 404:
            print("No Requests",end="")
            await asyncio.sleep(10)
            sys.stdout.write("\r")
            return await assign_image()
        return await res.json()


async def get_status():
    url = METEX_URL + "/v2/config"
    async with request("POST",url=url,headers=headers) as res:
        # print("/config",res.status)
        return await res.json()