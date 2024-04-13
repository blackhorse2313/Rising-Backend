from apis.start import Main
import asyncio
print("Starting Main")
print("\n")
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    client = Main()
    loop.create_task(client.start())
    loop.run_forever()
