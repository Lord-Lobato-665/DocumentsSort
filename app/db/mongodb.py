# mongodb.py
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import dotenv_values

# Primero intenta cargar desde .env, si no existe usa variables de entorno del sistema
config = dotenv_values(".env") if os.path.exists(".env") else {}

# Usa variables de entorno del sistema con fallback a config
MONGO_URI = os.getenv("MONGO_URI", config.get("MONGO_URI", "mongodb://localhost:27017"))
DB_NAME = os.getenv("DB_NAME", config.get("DB_NAME", "document_classifier"))

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

async def get_collection(name: str):
    return db[name]

# ✅ Esto lo agregas al final
class MongoDB:
    def __init__(self):
        self.client = client
        self.db = db

mongodb = MongoDB()
