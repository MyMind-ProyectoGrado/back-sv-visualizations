from fastapi import FastAPI, Request, HTTPException, Depends
from app.routes import transcription
import os
from dotenv import load_dotenv
import socket

# Middleware para verificar la fuente de la solicitud
async def verify_request_from_apisix(request: Request):
    entorno = os.getenv("ENVIRONMENT")

    if entorno == "production":
        expected_url = os.getenv("APISIX_PROD")  # (Tendrás que definirlo para producción también)
        client_ip = request.client.host
        print(f"Client IP (Production): {client_ip}, Expected URL: {expected_url}")

        if not client_ip.startswith("http"):
            if client_ip != expected_url:
                raise HTTPException(status_code=403, detail="Forbidden: Not allowed source")
    else:
        # En local, resolver IP del contenedor 'apisix'
        expected_container_name = "apisix"
        expected_ip = socket.gethostbyname(expected_container_name)
        client_ip = request.client.host

        if client_ip != expected_ip:
            raise HTTPException(status_code=403, detail="Forbidden: Not allowed source")

app = FastAPI(title="MyMind - Visualization Service", dependencies=[Depends(verify_request_from_apisix)])

# Incluye las rutas
app.include_router(transcription.router, tags=["Transcriptions"])
