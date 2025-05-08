from fastapi import FastAPI, Request, HTTPException, Depends
from app.routes import transcription  # Asegúrate de que este import sea correcto
import os
from dotenv import load_dotenv
import socket

# Cargar las variables de entorno
load_dotenv()

# Middleware para verificar la fuente de la solicitud
async def verify_request_from_apisix(request: Request):
    entorno = os.getenv("ENVIRONMENT")

    # En producción, verificar la URL de APISIX
    if entorno == "production":
        expected_url = os.getenv("APISIX_PROD")  # Debes definir esta variable para producción
        client_ip = request.client.host
        print(f"Client IP (Production): {client_ip}, Expected URL: {expected_url}")

        # Si la IP del cliente no es la esperada, lanzar error
        if not client_ip.startswith("http") and client_ip != expected_url:
            raise HTTPException(status_code=403, detail="Forbidden: Not allowed source")
    else:
        # En local, resolver IP del contenedor 'apisix'
        expected_container_name = "apisix"
        try:
            expected_ip = socket.gethostbyname(expected_container_name)
            client_ip = request.client.host
            print(f"Client IP (Local): {client_ip}, Expected IP: {expected_ip}")

            if client_ip != expected_ip:
                raise HTTPException(status_code=403, detail="Forbidden: Not allowed source")
        except socket.gaierror:
            raise HTTPException(status_code=500, detail="Internal Server Error: Unable to resolve APISIX container IP")

# Crear la aplicación FastAPI
app = FastAPI(title="MyMind - Visualization Service", dependencies=[Depends(verify_request_from_apisix)])

# Incluye las rutas
app.include_router(transcription.router, tags=["Transcriptions"])

# Ruta de prueba
@app.get("/")
async def root():
    return {"message": "Bienvenido al servicio de visualización de MyMind 🚀"}
