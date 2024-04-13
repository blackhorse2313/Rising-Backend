import aiohttp
from config import SD_BASE_URL as BASE_URL
import io
import base64
from PIL import Image
from apis import txt2img
from util import image_to_base64

# A demo payload for upscaling for reference.
payload_json_upscale = {
        "resize_mode": 1,
        "show_extras_results": False,
        "upscaling_resize_w": 2048,
        "upscaling_resize_h": 2048,
        "upscaling_resize": 4,
        "upscaling_crop": False,
        "upscaler_1": "R-ESRGAN 4x+",
        "upscaler_2": "R-ESRGAN 4x+",
        "extras_upscaler_2_visibility": 1,
        "upscale_first": True,
    }

payload2 = {
  "resize_mode": 1,
  "show_extras_results": True,
  "codeformer_visibility": 1,
  "codeformer_weight": 0,
  "upscaling_resize": 2,
  "upscaler_1": "R-ESRGAN 4x+",
  "extras_upscaler_2_visibility": 0,
  "upscale_first": True,
  "image": ""
}
async def upscale_image(data):

    image = await __upscale_image(data.get("parameters"))
    return {"image":image,"session_id":data.get("session_id"),"request_type":data.get("request_type")}


async def __upscale_image(payload):
    """
    This API is used to upscale the image . data.get("image") should be a base64 encoded image and required.
    :param data:
    :return:
"""

    async with aiohttp.ClientSession() as session:
        async with session.post(BASE_URL + '/sdapi/v1/extra-single-image', json=payload) as resp:
            response = await resp.json()
            if resp.status != 200:
                raise ValueError(response)
            return response["image"]


async def __unittest():
    """
    Used for testing the upscaling part.
    :return:
    """
    file_path = r"D:\stable_diffusion_webui\outputs\txt2img-images\2023-10-21\00000-2460053036.png"

    # Open the file in binary mode and read its content
    with open(file_path, "rb") as image_file:
        file_content = image_file.read()

    # Encode the content in base64
    encoded_content = base64.b64encode(file_content)
    encoded_string = encoded_content.decode("utf-8")

    payload = {
    "resize_mode": 0,
  "show_extras_results": True,
  "codeformer_visibility": 1,
  "codeformer_weight": 0,
  "upscaling_resize": 2,
  "upscaler_1": "R-ESRGAN 4x+",
  "extras_upscaler_2_visibility": 0,
  "upscale_first": True,
  "image": encoded_string
}
    # Convert the encoded content to a string (optional)
    encoded_string = encoded_content.decode("utf-8")
    response = await __upscale_image(payload)
    Image.open(io.BytesIO(base64.b64decode(encoded_string.split(",", 1)[0]))).show()


if __name__ == '__main__':
    import asyncio

    asyncio.run(__unittest())
