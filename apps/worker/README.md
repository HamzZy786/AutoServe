# Background Worker Service

A Celery-based background worker for processing asynchronous tasks in the AutoServe platform.

## Features

- 🔄 Celery task processing with Redis broker
- 📊 Task monitoring and metrics
- 🔍 Distributed tracing integration
- 📝 Comprehensive logging
- ⚡ Auto-scaling task processing
- 🔔 Task failure notifications

## Local Development

```bash
cd apps/worker
pip install -r requirements.txt
celery -A worker worker --loglevel=info
```

## Task Types

- **Email notifications**: Send alerts and reports
- **Data processing**: Clean and aggregate metrics
- **ML model training**: Retrain scaling models
- **Backup operations**: Database and file backups
- **Health checks**: Periodic service monitoring

## Environment Variables

- `CELERY_BROKER_URL`: Redis broker URL
- `CELERY_RESULT_BACKEND`: Result backend URL
- `DATABASE_URL`: PostgreSQL connection string
- `LOG_LEVEL`: Logging level
