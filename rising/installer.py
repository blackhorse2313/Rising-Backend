import subprocess
import os
from config import TESTING

if TESTING:
    os.chdir("D:\easyinstaller")
    os.chdir("..")
if os.getcwd().split(os.sep)[-1] == "easyinstaller":
    os.chdir("..")

ARIA2C = os.path.join(os.getcwd(),"easyinstaller","aria2c.exe")
print("ARIA2C : ",ARIA2C)

ROOT_DIR = os.getcwd()
print("ROOT_DIR : ",ROOT_DIR)
stable_diffusion_webui = os.path.join(ROOT_DIR, "stable_diffusion_webui")
MODELS_DIR = os.path.join(stable_diffusion_webui, "models")
STABLE_DIFFUSION_CHECKPOINT_DIR = os.path.join(MODELS_DIR, "Stable-diffusion")
CONTROLNET_DIR = os.path.join(MODELS_DIR, "ControlNet")
EXTENSIONS_DIR = os.path.join(stable_diffusion_webui, "extensions")
# subprocess.run([aria2c, "-x", "10", model.get("url"), model.get("path")])


def download_model(url,path,redownload=False):
    paths = path.split('/')

    dir = os.path.join(stable_diffusion_webui,*paths[:-1])
    filename = paths[-1]

    if not os.path.exists(dir):
        os.makedirs(dir)
    if os.path.exists(os.path.join(dir,filename)) and not redownload:
        print("File already exists")
        return
    if not os.path.exists(ARIA2C):
        print("ARIAC2 not found")
    subprocess.run([ARIA2C, "-x", "10", "-d",dir,"-o",filename,url])

def model_exists(path):
    path = os.path.join(*path.split('/'))
    return os.path.exists(os.path.join(STABLE_DIFFUSION_CHECKPOINT_DIR,path))
def extension_exists(name):
    return os.path.exists(os.path.join(EXTENSIONS_DIR,name))

def download_extension(repository,name):
    if extension_exists(name):
        print("Extension already exists")
        return
    subprocess.run(["git", "clone", repository, os.path.join(EXTENSIONS_DIR,name)])
