import asyncio
from os import getenv

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import MongoClient

from config import config

load_dotenv()
client: MongoClient = AsyncIOMotorClient(config.DB_SRV)


# Attaches the client to the same loop
client.get_io_loop = asyncio.get_event_loop
db: AsyncIOMotorDatabase = client.get_database(
    "backend" if not config.TESTING else "backend_test"
)
