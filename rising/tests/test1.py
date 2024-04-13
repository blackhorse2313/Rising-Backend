import random

from PIL import Image
from apis.upscale import upscale_image
from apis.txt2img import txt_2_img
import asyncio
import io
import base64

upscale_1 = {  "resize_mode": 1,
  "upscaling_resize_w": 2048,
  "upscaling_resize_h": 2048,
  "upscaling_resize": 4,
  "upscaling_crop": False,
  "upscaler_1": "R-ESRGAN 4x+",
  "upscaler_2": "R-ESRGAN 4x+",
  "extras_upscaler_2_visibility": 1,
  "upscale_first": True,
  "show_extras_results": False,}


async def __unit_test():
    # from util.demo_requests import upscale_1
    from util.demo_requests import txt_2_img_1
    txt_2_img_1["seed"] = int(random.random()*100000)
    print(txt_2_img_1)
    images = await txt_2_img(txt_2_img_1)
    image = images[0]
    # for image in images:
    #     Image.open(io.BytesIO(base64.b64decode(image.split(",", 1)[0]))).show()
    Image.open(io.BytesIO(base64.b64decode(image.split(",", 1)[0]))).show()
    print("Done")
    upscale_1["image"] = image
    image2 = await upscale_image(upscale_1)
    Image.open(io.BytesIO(base64.b64decode(image2.split(",", 1)[0]))).show()
    print(3)

asyncio.run(__unit_test())
