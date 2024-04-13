import aiohttp
from PIL import Image
import base64
from config import SD_BASE_URL as BASE_URL
from util import base64_to_image, image_to_base64
from util import converts
from config import debug_call
import io



payload_txt_2_img = {
    "prompt": "No Way",
    "seed": 605118,
    "sampler_name": "Euler a",
    "batch_size": 1,
    "steps": 25,
    "cfg_scale": 7,
    "width": 512,
    "height": 512,
    "tiling": True,
    "negative_prompt": "",
    "restore_faces": True,
    "request_type": "custom", }


async def api_txt_2_img(data):
    payload = data.get("parameters")
    url = f"{BASE_URL}/sdapi/v1/txt2img"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            response = await resp.json()
            if resp.status != 200:
                raise ValueError(response)
            return response["images"], response["parameters"]


async def txt_2_img(data):
    images, info = await api_txt_2_img(data)
    all_images = [base64_to_image(img) for img in images]
    grid_image = __merge_images(all_images)
    debug_call(Image.open(io.BytesIO(base64.b64decode(image_to_base64(grid_image).split(",", 1)[0]))).show)
    return {"images": images,"grid_image": image_to_base64(grid_image),
            "session_id": data.get("session_id"),
            "request_type": data.get("request_type")}

async def qr1(data):
    images, info = await api_txt_2_img(data)
    # debug_call(Image.open(io.BytesIO(base64.b64decode(images[0].split(",", 1)[0]))).show)
    return {"image": images[0],
            "session_id": data.get("session_id"),
            "request_type": data.get("request_type")}


def __merge_images(images):
    if len(images) == 1:
        image = images[0].resize((images[0].width, images[0].height))
        return image
    elif len(images) == 2:
        dst = Image.new("RGB", (images[0].width * 2, images[0].height))
        dst.paste(images[0], (0, 0))
        dst.paste(images[1], (images[0].width, 0))
        return dst
    elif len(images) == 4:
        dst = Image.new("RGB", (images[0].width * 2, images[0].height * 2))
        dst.paste(images[0], (0, 0))
        dst.paste(images[1], (images[0].width, 0))
        dst.paste(images[2], (0, images[0].height))
        dst.paste(images[3], (images[0].width, images[0].height))
        dst = dst.resize((images[0].width, images[0].height))
        return dst


async def __unit_test():
    from util.demo_requests import txt_2_img_2
    response = await txt_2_img(txt_2_img_2)
    img = response.get("file")
    # print(images)
    # for image in images:
    #     Image.open(io.BytesIO(base64.b64decode(image.split(",", 1)[0]))).show()


if __name__ == "__main__":
    import asyncio

    asyncio.run(__unit_test())
