import asyncio
from apis import metexapi as metex


async def ping_online():
    while True:
        await metex.ping_online()
        await asyncio.sleep(10)
