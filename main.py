from fastapi import FastAPI, Request, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import socket
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Gauge, Histogram
import time
from fastapi.exceptions import RequestValidationError

# Cargar variables de entorno
load_dotenv()

# Middleware para verificar la fuente de la solicitud
async def verify_request_from_apisix(request: Request):
    if request.url.path == "/metrics":
        try:
            prometheus_ip = socket.gethostbyname("prometheus")
            client_ip = request.client.host
            if client_ip == prometheus_ip:
                return
        except Exception as e:
            print(f"Error resolviendo Prometheus: {e}")

    entorno = os.getenv("ENVIRONMENT")

    if entorno == "production":
        expected_url = os.getenv("APISIX_PROD")
        client_ip = request.client.host
        print(f"Client IP (Production): {client_ip}, Expected URL: {expected_url}")

        if not client_ip.startswith("http"):
            if client_ip != expected_url:
                raise HTTPException(status_code=403, detail="Forbidden: Not allowed source")
    else:
        expected_container_name = "apisix"
        expected_ip = socket.gethostbyname(expected_container_name)
        client_ip = request.client.host

        if client_ip != expected_ip:
            raise HTTPException(status_code=403, detail="Forbidden: Not allowed source")

# Crear la aplicación FastAPI
app = FastAPI(
    title="MyMind - Visualization Service",
     dependencies=[Depends(verify_request_from_apisix)]
)

# Contadores personalizados
REQUEST_COUNT = Counter(
    'fastapi_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'app_name']
)

RESPONSE_COUNT = Counter(
    'fastapi_responses_total',
    'Total number of responses',
    ['method', 'endpoint', 'status_code', 'app_name']
)
RESPONSE_COUNT.labels(method="GET", endpoint="/", status_code="500", app_name="mymind-visualizations").inc(0)

EXCEPTION_COUNT = Counter(
    'fastapi_exceptions_total',
    'Total number of exceptions',
    ['method', 'endpoint', 'exception', 'app_name']
)
EXCEPTION_COUNT.labels(method="GET", endpoint="/", exception="None", app_name="mymind-visualizations").inc(0)

IN_PROGRESS = Gauge(
    'fastapi_requests_in_progress',
    'Number of requests in progress',
    ['method', 'endpoint', 'app_name']
)

REQUEST_LATENCY = Histogram(
    'fastapi_request_duration_seconds',
    'Request latency',
    ['method', 'endpoint', 'app_name'],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
)

# Instrumentación y exposición en "/metrics"
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# Conexión a MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_database("mymind_users")  # Nombre de la BD

# Importar y registrar las rutas
from app.routes import transcription

app.include_router(transcription.router, prefix="/transcriptions", tags=["Transcriptions"])

# Ruta de prueba
@app.get("/")
async def root():
    return {"message": "Bienvenido al servicio de visualizaciones de MyMind 🚀"}

# Middleware para métricas
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    method = request.method
    endpoint = request.url.path
    app_name = "mymind-visualizations"

    # Ignorar métricas para /metrics
    if endpoint == "/metrics":
        response = await call_next(request)
        return response

    REQUEST_COUNT.labels(method=method, endpoint=endpoint, app_name=app_name).inc()
    IN_PROGRESS.labels(method=method, endpoint=endpoint, app_name=app_name).inc()
    start_time = time.time()

    try:
        response = await call_next(request)
        duration = time.time() - start_time
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint, app_name=app_name).observe(duration)
        RESPONSE_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(response.status_code),
            app_name=app_name
        ).inc()

        if response.status_code >= 500:
            EXCEPTION_COUNT.labels(
                method=method,
                endpoint=endpoint,
                exception="HTTPException",
                app_name=app_name
            ).inc()

    except HTTPException as he:
        EXCEPTION_COUNT.labels(
            method=method,
            endpoint=endpoint,
            exception=str(type(he)._name_),
            app_name=app_name
        ).inc()
        raise he

    except RequestValidationError as ve:
        EXCEPTION_COUNT.labels(
            method=method,
            endpoint=endpoint,
            exception="RequestValidationError",
            app_name=app_name
        ).inc()
        raise ve

    except Exception as e:
        EXCEPTION_COUNT.labels(
            method=method,
            endpoint=endpoint,
            exception=str(type(e)._name_),
            app_name=app_name
        ).inc()
        RESPONSE_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status_code="500",
            app_name=app_name
        ).inc()
        raise e

    finally:
        IN_PROGRESS.labels(method=method, endpoint=endpoint, app_name=app_name).dec()

    return response