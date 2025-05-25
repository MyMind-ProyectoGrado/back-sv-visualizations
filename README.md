# MyMind - Visualization Service 📊

Microservicio FastAPI para el análisis y visualización de transcripciones de audio con detección de emociones y sentimientos.

## 🚀 Características

- **Análisis de Emociones**: Procesamiento de 9 emociones (joy, anger, sadness, disgust, fear, neutral, surprise, trust, anticipation)
- **Análisis de Sentimientos**: Clasificación en positivo, negativo y neutral
- **Autenticación JWT**: Integración con APISIX para validación de tokens
- **Base de Datos MongoDB**: Almacenamiento escalable con Motor (async)
- **Métricas Prometheus**: Monitoreo y observabilidad integrada
- **Containerización Docker**: Despliegue simplificado

## 📋 Requisitos Previos

- Python 3.10+
- Docker y Docker Compose
- MongoDB (local o en la nube)
- Variables de entorno configuradas

## 🛠️ Instalación

### Opción 1: Desarrollo Local

1. **Clonar el repositorio**
```bash
git clone <url-del-repositorio>
cd service-visualizations
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
```
Editar `.env` con tus configuraciones:
```env
MONGO_URI=mongodb://localhost:27017
ENVIRONMENT=development
APISIX_PROD=tu_ip_produccion
```

5. **Ejecutar la aplicación**
```bash
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

### Opción 2: Docker

1. **Construir y ejecutar con Docker Compose**
```bash
docker-compose up --build
```

2. **Solo Docker**
```bash
docker build -t mymind-visualizations .
docker run -p 8002:8002 --env-file .env mymind-visualizations
```

## 📚 API Endpoints

### Transcripciones

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/transcriptions` | Obtener todas las transcripciones (admin) |
| `GET` | `/transcriptions/user` | Transcripciones del usuario autenticado |
| `GET` | `/transcriptions/user/latest` | Última transcripción del usuario |
| `GET` | `/transcriptions/user/last-7-days` | Promedios de los últimos 7 días |
| `GET` | `/transcriptions/user/last-week/top-emotions-sentiments` | Top 3 emociones y sentimiento principal |
| `GET` | `/transcriptions/user/audio/{audio_id}` | Transcripción específica por ID |

### Sistema

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/metrics` | Métricas de Prometheus |

## 🔐 Autenticación

El servicio utiliza JWT tokens pasados por APISIX. El token debe incluirse en el header:

```
Authorization: Bearer <jwt_token>
```

El token debe contener el campo `sub` con el ID del usuario.

## 📊 Modelos de Datos

### TranscriptionOut
```json
{
  "id": "string",
  "user_id": "string",
  "date": "2024-01-15",
  "time": "14:30:00",
  "text": "Texto transcrito...",
  "emotion": "joy",
  "sentiment": "positive",
  "emotionProbabilities": {
    "joy": 0.8,
    "anger": 0.1,
    "sadness": 0.05,
    "disgust": 0.02,
    "fear": 0.01,
    "neutral": 0.01,
    "surprise": 0.01,
    "trust": 0.0,
    "anticipation": 0.0
  },
  "sentimentProbabilities": {
    "positive": 0.85,
    "negative": 0.10,
    "neutral": 0.05
  },
  "topic": "conversación_casual"
}
```

### TranscriptionAverages
Promedios de probabilidades de emociones y sentimientos en un período específico.

### TrancriptionTop3
```json
{
  "emotion_probs_top1": "joy",
  "emotion_probs_top2": "trust",
  "emotion_probs_top3": "anticipation",
  "sentiment_probs_top1": "positive"
}
```

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     APISIX      │────│   FastAPI App   │────│    MongoDB      │
│   (Gateway)     │    │ (Visualizations)│    │   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │
                       ┌─────────────────┐
                       │   Prometheus    │
                       │   (Metrics)     │
                       └─────────────────┘
```

### Componentes Principales

- **main.py**: Aplicación principal con middleware de métricas
- **app/routes/transcription.py**: Endpoints de transcripciones
- **app/core/auth.py**: Validación JWT
- **app/core/database.py**: Conexión MongoDB
- **app/schemas/**: Modelos Pydantic

## 📈 Monitoreo

El servicio expone métricas en `/metrics` para Prometheus:

- `fastapi_requests_total`: Total de requests
- `fastapi_responses_total`: Total de responses
- `fastapi_exceptions_total`: Total de excepciones
- `fastapi_requests_in_progress`: Requests en progreso
- `fastapi_request_duration_seconds`: Latencia de requests

## 🔧 Configuración

### Variables de Entorno

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `MONGO_URI` | URI de conexión MongoDB | `mongodb://localhost:27017` |
| `ENVIRONMENT` | Entorno de ejecución | `development` / `production` |
| `APISIX_PROD` | IP de APISIX en producción | `192.168.1.100` |

### Estructura de MongoDB

```
myMindDB-Users/
├── users/
    ├── _id: "user_id"
    ├── email: "user@example.com"
    ├── name: "Usuario"
    └── transcriptions: [
        {
            _id: ObjectId,
            date: "2024-01-15",
            time: "14:30:00",
            text: "...",
            emotion: "joy",
            sentiment: "positive",
            emotionProbabilities: {...},
            sentimentProbabilities: {...}
        }
    ]
```

## 🧪 Testing

```bash
# Ejecutar con pytest (cuando se implementen los tests)
pytest

# Health check manual
curl http://localhost:8002/

# Test de endpoint con autenticación
curl -H "Authorization: Bearer <token>" http://localhost:8002/transcriptions/user
```

## 📦 Dependencias Principales

- **FastAPI**: Framework web async
- **Motor**: Driver async para MongoDB
- **PyJWT**: Manejo de tokens JWT
- **Prometheus FastAPI Instrumentator**: Métricas
- **Pydantic**: Validación de datos
- **Uvicorn**: Servidor ASGI

## 🚀 Despliegue

### Docker Compose (Recomendado)

```yaml
services:
  backend:
    container_name: back-sv-visualizations
    build: .
    ports:
      - "8002:8002"
    networks:
      - shared-net
```

### Consideraciones de Producción

- Configurar `ENVIRONMENT=production`
- Asegurar conexión segura a MongoDB
- Configurar límites de rate limiting
- Implementar logs estructurados
- Configurar alertas en Prometheus

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 License

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico o preguntas:
- Crear un issue en GitHub
- Contactar al equipo de desarrollo

---

**MyMind Visualization Service** - Análisis inteligente de emociones y sentimientos 🧠✨
