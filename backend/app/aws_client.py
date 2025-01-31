import asyncio
import base64
import io
import os
import traceback
from contextlib import nullcontext
from config import config
import aioboto3


from app import schema


ACCESS_KEY = config.AWS_KEY
ACCESS_SECRET = config.AWS_SECRET
session = aioboto3.Session(
    aws_access_key_id=ACCESS_KEY, aws_secret_access_key=ACCESS_SECRET
)


async def upload_file(name, file):
    async with session.resource("s3") as s3:
        bucket = await s3.Bucket("resources-image-ai")  #
        await bucket.upload_fileobj(file, name)


async def upload_submitted_images(data: schema.SubmitImageRequesttxt2img):
    async with session.resource("s3") as s3:
        tasks = []
        for i in enumerate(data.images):
            tasks.append(
                upload_base64_to_aws(i[1], data.session_id + "_" + str(i[0]), s3)
            )
        locations = await asyncio.gather(*tasks)
        grid_location = await upload_base64_to_aws(
            data.grid_image, data.session_id + "_" + "grid", s3
        )
        return locations, grid_location


async def upload_base64_to_aws(base64_string, name, s3=None):
    obj = await s3.Object("resources-image-ai", name + ".png")
    await obj.put(Body=base64.b64decode(base64_string.split(",", 1)[0]))
    return f"s3://resources-image-ai/{name}.png"


async def upload_base64_to_aws2(base64_string, name):
    async with session.resource("s3") as s3:
        obj = await s3.Object("resources-image-ai", name)
        await obj.put(Body=base64.b64decode(base64_string.split(",", 1)[0]))
        return f"s3://resources-image-ai/{name}"


async def delete_file(name: str):
    async with session.resource("s3") as s3:
        bucket = await s3.Bucket("resources-image-ai")  #
        await bucket.delete_objects(Delete={"Objects": [{"Key": name}]})


async def download_file(name: str) -> str:
    async with session.resource("s3") as s3:
        bucket = await s3.Bucket("resources-image-ai")  #
        try:
            file = io.BytesIO()
            await bucket.download_fileobj(name, file)
            print("File successfully downloaded")
            file.seek(0)
            base64_str = base64.b64encode(file.read()).decode("utf-8")
            return base64_str
        except Exception as e:
            print(traceback.print_exc())
            print("AWS File not found")


if __name__ == "__main__":
    pass

    # base64_str = open("../app/testimage.txt", "r").read()
    # asyncio.run(upload_base64_to_aws("testimage.png", base64_str))
    # print("Done")

# server {
#         listen 80;
#         server_name 18.206.126.95;
#         location / {
#               proxy_pass http://127.0.0.1:8000;
#         }
#         }
