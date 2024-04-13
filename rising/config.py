
from dotenv import load_dotenv
from os import getenv
VER = "1.0"

DEPENDENCIES_SATISFIED = set()

load_dotenv()
SD_BASE_URL = getenv("SD_BASE_URL")

TESTING= eval(getenv("TESTING") or False)
METEX_URL = getenv("METEX_URL")
print("SD_BASE_URL", SD_BASE_URL)
print("METEX_URL", METEX_URL)
if None in [SD_BASE_URL, TESTING, METEX_URL]:
    raise Exception("Environment variables not set")

if TESTING:
    print("Running in testing mode")
else:
    print("Running in production mode")
def debug_call(function):
    if TESTING:
        function()