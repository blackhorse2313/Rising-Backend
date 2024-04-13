from apis import metexapi as metex, tasks
import asyncio
from config import VER, DEPENDENCIES_SATISFIED
from util.demo_requests import payload_json_txt2img
from util import exc
import apis
from links import dependencies


class Main:
    def __init__(self):
        self.ready = True

    async def start(self):
        await self.wait_for_sd_server()
        # await set_downloaded_models()
        # await self.download_dependencies()
        try:
            await metex.create_session()
            # await self.check_for_wallet()
            asyncio.get_event_loop().create_task(tasks.ping_online())
        except Exception as E:
            await exc.handle_exceptions(E, "main")
        while True:
            try:
                await self.process()
            except Exception as E:
                await exc.handle_exceptions(E, "main")
                await asyncio.sleep(5)

    async def check_sd_server(self):
        # todo:Create a get config to check the status of the server
        try:
            await apis.txt2img.api_txt_2_img(payload_json_txt2img)
            self.ready = True
            return True
        except Exception as E:
            print("Stable Diffusion is not working. Waiting for it to start/restart...")
            self.ready = False
            return False

    async def wait_for_sd_server(self):
        print("Waiting for Stable Diffusion Server to start...")
        while True:
            if await self.check_sd_server():
                break
            await asyncio.sleep(5)
        print("Stable Diffusion Server is ready.")

    async def process(self):
        await self.wait_for_sd_server()
        if not self.ready:
            print("Failed to start.")
            while True:
                input()
        data = await metex.assign_image()
        print(f"Processing request : {data.get('session_id')}")
        if data.get("request_type") == "upscale":
            image_data = await apis.upscale_image(data)
        elif data.get("request_type") == "txt2img":
            image_data = await apis.txt_2_img(data)
        elif data.get("request_type") == "qr1":
            image_data = await apis.qr1(data)
        else:
            print("Invalid request type")
            print("Waiting before retrying again...")
            await asyncio.sleep(5)
            return
        print(f"Submitting request : {image_data.get('session_id')}")
        await metex.submit_image(image_data)

    async def download_dependencies(self):
        print(DEPENDENCIES_SATISFIED)
        print("Downloading Dependencies...")
        for module in dependencies:
            await self.__download_dependencies(module)

    # async def __download_dependencies(self,module):
    #     if module.get("method") == "clone":
    #         if module.get("type") == "extension" and not (installer.extension_exists(module.get("name"))):
    #             print(f"Downloading {module.get('name')}...")
    #             installer.download_extension(module.get("url"), module.get("name"))
    #             await restart_server()
    #     elif module.get("method") == "download":
    #         hash = module.get("name_hash")
    #         if hash and hash in DEPENDENCIES_SATISFIED:
    #             print(f"{module.get('name')} already downloaded")
    #             return
    #         installer.download_model(module.get("url"), module.get("path"))

    async def check_for_wallet(self):
        response = await metex.get_host()
        if response.get("wallet_id") is None:
            wallet_id = input("Please enter your wallet id :")
            await metex.set_wallet_id(wallet_id)
            await self.check_for_wallet()
        else:
            print(f"Wallet id : {response.get('wallet_id')}")

    async def check_version(self):
        res = await metex.get_status()
        if res.get("current_version") > float(VER):
            print("A New Version is available . Please download that.")
            self.ready = False
        elif not res.get("enable_hosting"):
            print("Maintenance is going on. Please try later.")
            self.ready = False
