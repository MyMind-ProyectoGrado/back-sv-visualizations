from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.getenv("DATABASE_URL")

client = AsyncIOMotorClient(MONGO_URL)
mongo_db = client["mymind"]  # Cambia si tu DB tiene otro nombre

# Función equivalente a get_db()
async def get_db():
    return mongo_db
