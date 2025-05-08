from fastapi import FastAPI, Request, HTTPException, Depends
from app.routes import transcription
import os
from dotenv import load_dotenv
import socket
from motor.motor_asyncio import AsyncIOMotorClient

# Middleware para verificar la fuente de la solicitud
async def verify_request_from_apisix(request: Request):
    entorno = os.getenv("ENVIRONMENT")

    if entorno == "production":
        expected_url = os.getenv("APISIX_PROD")  # (Tendrás que definirlo para producción también)
        client_ip = request.client.host
        print(f"Client IP (Production): {client_ip}, Expected URL: {expected_url}")

        # Si no está en local, validamos la IP con la URL esperada
        if not client_ip.startswith("http"):
            if client_ip != expected_url:
                raise HTTPException(status_code=403, detail="Forbidden: Not allowed source")
    else:
        # En local, solo dejamos pasar todas las solicitudes (sin validación)
        
        # Comentada la parte de validación por IP en entorno local
         expected_container_name = "apisix"
         expected_ip = socket.gethostbyname(expected_container_name)
         client_ip = request.client.host

         if client_ip != expected_ip:
             raise HTTPException(status_code=403, detail="Forbidden: Not allowed source")
        

app = FastAPI(title="MyMind - Visualization Service", dependencies=[Depends(verify_request_from_apisix)])

# Conexión a MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_database("mymind_users")  # Nombre de la BD

# Incluye las rutas
app.include_router(transcription.router, tags=["Transcriptions"])
