import requests
from PIL import Image
import io
import base64
from pprint import pprint
import json
import qrcode

prompts = [("staring up into the infinite maelstrom library, endless books, flying books, spiral staircases, nebula, ominous, cinematic atmosphere, negative dark mode, mc escher, art by senseijaye, matrix atmosphere, digital code swirling, matte painting, laboratory , sharp , raytracing , light tracing , 8k , ultra preset",
            "(worst quality, low quality:1.4), (logo, text, watermask, username), NG_DeepNegative_V1_75T, (bad-hands-5, bad-artist:1.2), human, girl , boy , man , female ,male,(bad-image-v2-39000, bad_prompt_version2, bad-hands-5, EasyNegative, NG_DeepNegative_V1_4T, bad-artist-anime:0.7),(worst quality, low quality:1.3), (depth of field, blurry:1.2), (greyscale, monochrome:1.1), nose, cropped, lowres, text, jpeg artifacts, signature, watermark, username, blurry, artist name, trademark, watermark, title,(tan, muscular, loli, petite, child, infant, toddlers, chibi, sd character:1.1), multiple view, Reference sheet, long neck, unclear lines"),
           ("mecha, robot , war, gundam,1robot, high quality, high resolution. detailed body, detailed, legs , detailed face , detailed metal,8k, ultra realistic, icy background ,explosion in the background, fire  long sword  in right hand, shield in left hand, darker blacks,finely detailed,best quality, extra sharp , 16x anistrophic filtering",
            "noise, haze, low quality, deformed leg, deformed body, extra hands ,extra legs , blurry foot,text, numbers, extra faces in corners, unnecessary objects,deformed fingers, extra fingers"),
           ("clouds with beautiful land scenery, high quality, finely detailed , intricate details,8k , sharp , mountains , snowfall, high resolution, 8k resolution, darker blacks",
            "blur , low quality , low resolution, light colors, sunset, yellow lights rays, haze, sun rays")
           ]

def base64_to_image(base64_string):
    return Image.open(io.BytesIO(base64.b64decode(base64_string.split(",", 1)[0])))


def image_to_base64(image):
    image_string = io.BytesIO()
    image.save(image_string, format="PNG")
    return base64.b64encode(image_string.getvalue()).decode("utf-8")

def txt2img(parameters):
    url = "http://localhost:7860/sdapi/v1/txt2img"
    response = requests.post(url, json=parameters)
    return response.json()

def main():
    parameters = get_prompt()
    response = txt2img(parameters)
    pprint(json.loads(response.get("info")))

    images = response.get("images")
    i = images[0]
    i = base64_to_image(i)
    i.show()
    print("done")

def get_prompt():
    qr = make_qr("https://metex.co")
    # qr = Image.open("metex2.png")
    qr = qr.convert("RGBA")
    parameters = {
        "prompt": prompts[1][0],
        "negative_prompt": prompts[1][1],
        "width": 512,
        "height": 512,
        "steps": 35,
        "sampler_name": "DPM++ 2M Karras",
        "cfg_scale":7,
        "seed": -1,
        "sd_model_name":"revAnimated_v122EOL",
        "clip_skip":2,
        "override_settings":{
            "sd_model_checkpoint":"revAnimated_v122EOL.safetensors [4199bcdd14]",
            "CLIP_stop_at_last_layers":2,
        },
        "alwayson_scripts":{
            "controlnet":{
                "args":[
                    {"input_image":image_to_base64(qr),
                     "module":"inpaint_global_harmonious",
                     "model":"control_v1p_sd15_brightness [5f6aa6ed]",
                     "weight":0.5,
                     "resize_mode":"Resize and Fill",
                     "lowvram":False,
                     "guidance_start":0,
                     "guidance_end":1,
                     "pixel_perfect":False,
                     "control_mode":0,
                     },
                    {"input_image": image_to_base64(qr),
                     "module": "inpaint_global_harmonious",
                     "model": "control_v11f1e_sd15_tile [a371b31b]",
                     "weight": 0.355,
                     "resize_mode": "Resize and Fill",
                     "lowvram": False,
                     "guidance_start": 0.35,
                     "guidance_end": 0.654,
                     "pixel_perfect": False,
                     "control_mode": 0,
                     }
                ]
            }
        }
    }


    return parameters
def make_qr(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=50,
        border=1,
    )
    qr.add_data(url)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

if __name__ == '__main__':
    main()