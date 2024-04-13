import random
from PIL import Image
import io
import base64

def convert_txt_2_img_json_data(data):
    params = data.get("params")
    seed = params.get("seed") or int(random.random() * 100000)
    new_request = {
        "prompt": data.get("prompt"),
        "seed": seed,
        "sampler_name": samplers.get(params.get("sampler")) or params.get("sampler"),
        "batch_size": params.get("num_outputs"),
        "steps": params.get("num_inference_steps"),
        "cfg_scale": 7,
        "width": params.get("width"),
        "height": params.get("height"),
        "negative_prompt": params.get("negative_prompt"),
    }

    return new_request


def base64_to_image(base64_string):
    return Image.open(io.BytesIO(base64.b64decode(base64_string.split(",", 1)[0])))


def image_to_base64(image):
    image_string = io.BytesIO()
    image.save(image_string, format="PNG")
    return base64.b64encode(image_string.getvalue()).decode("utf-8")

samplers = {
    "euler_a": "Euler a",
    "heun": "Heun",
    "dpm2": "DPM2",
}

payload_json_txt2img = {
    "prompt": "Astronaut riding a horse in space",
    "seed": -1,
    "sampler_name": "Euler a",
    "batch_size": 1,
    "steps": 25,
    "cfg_scale": 7,
    "width": 512,
    "height": 512,
    "restore_faces": False,
    "tiling": False,
    "negative_prompt": "",
}