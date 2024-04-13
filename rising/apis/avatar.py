import aiohttp
from config import SD_BASE_URL as BASE_URL
import io
import base64
from PIL import Image


async def img2img(data):
    """
    This is used for Image2Image conversion.
    It takes input the data containig the prompt and base64 encoded image and a session_id .
    :param data:
    :return:
    """
    image = await __img2img(data)
    return {"file": image,"session_id": data.get("session_id")}


async def __img2img(data):
    """
    This uses the API to convert the image to image .
    :param data:
    :return:
    """
    payload = {
        "prompt": data.get("prompt"),
        "init_images": [data.get("image")],
        "restore_faces": True,
        "cfg_scale": 7,
        "image_cfg_scale": 1.5,
        "negative_prompt": data.get("negative_prompt"),
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(BASE_URL + '/sdapi/v1/img2img', json=payload) as resp:
            response = await resp.json()
            if resp.status != 200:
                raise ValueError(response)
            return response["images"][0]


async def __unittest():
    """
    For testing.
    :return:
    """
    # from util.demo_requests import upscale_1
    # upscale_1["image"] = open("..\\util\\testimage.txt", "r").read()
    # image = await __img2img({"image": upscale_1["image"]})
    # Image.open(io.BytesIO(base64.b64decode(image.split(",", 1)[0]))).show()
    # print("Done")


if __name__ == '__main__':
    import asyncio

    asyncio.run(__unittest())
