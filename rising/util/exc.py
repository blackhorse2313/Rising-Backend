from aiohttp import client_exceptions
from config import TESTING



async def handle_exceptions(exc, ctx):
    # TODO: Add logging and an api to send error messages
    if TESTING:
        print(exc)
        # print(traceback.format_exc())
    if isinstance(exc, client_exceptions.ClientConnectorError):
        print("Cannot Connect to server...")
    elif TESTING:
        print(exc)
        # print(traceback.format_exc())
