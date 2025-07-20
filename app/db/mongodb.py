# mongodb.py
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import dotenv_values

config = dotenv_values(".env")

client = AsyncIOMotorClient(config["MONGO_URI"])
db = client[config["DB_NAME"]]

async def get_collection(name: str):
    return db[name]
