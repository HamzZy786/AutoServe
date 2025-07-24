# FastAPI Backend Service

A high-performance FastAPI backend with automatic documentation, monitoring, and observability features.

## Features

- 🚀 FastAPI with automatic OpenAPI documentation
- 📊 Prometheus metrics integration
- 🔍 Distributed tracing with Jaeger
- 🗄️ PostgreSQL database with SQLAlchemy
- 🔄 Celery background tasks
- 🔐 JWT authentication
- 📝 Comprehensive logging
- 🧪 Full test coverage

## Local Development

```bash
cd apps/backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `CELERY_BROKER_URL`: Celery broker URL
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
