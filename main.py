from fastapi import FastAPI
from app.routes import transcription
from app.routes import user  # Asegúrate de que sea minúscula "user" en lugar de "User"

app = FastAPI()

# Incluye las rutas
app.include_router(transcription.router, tags=["Transcriptions"])
app.include_router(user.router, tags=["Users"])  
