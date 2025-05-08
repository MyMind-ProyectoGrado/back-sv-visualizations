import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Leer la URI de MongoDB desde el archivo .env
MONGO_URI = os.getenv("MONGO_URI")  # Cambiado de DATABASE_URL a MONGO_URI

# Depuración: Imprimir la URI para verificar
print(f"MONGO_URI: {MONGO_URI}")

if not MONGO_URI:
    raise ValueError("MONGO_URI no está definida en el archivo .env o en el entorno")

# Conectar con la base de datos en la nube
client = AsyncIOMotorClient(MONGO_URI)
db = client["myMindDB-Users"]
users_collection = db["users"]

# Dependencia para obtener la colección
async def get_mongo_collection():
    return users_collection