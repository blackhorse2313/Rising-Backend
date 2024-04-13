import aiohttp
from config import SD_BASE_URL as BASE_URL
from config import DEPENDENCIES_SATISFIED

async def get_sd_models():
    url = f"{BASE_URL}/sdapi/v1/sd-models"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            response = await resp.json()
            if resp.status != 200:
                raise ValueError(response)
            return response

async def get_controlnet_models():
    url = f"{BASE_URL}/controlnet/model_list"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            response = await resp.json()
            if resp.status != 200:
                print("Error Getting ControlNet Models")
                return None
            return response

async def set_downloaded_models():
    sd_models = await get_sd_models()
    for i in sd_models:
        DEPENDENCIES_SATISFIED.add(i.get("title"))
    controlnet_models = await get_controlnet_models()
    if controlnet_models:
        for i in controlnet_models.get("model_list"):
            DEPENDENCIES_SATISFIED.add(i)

