import os
import time
import logging
from datetime import datetime, timedelta
from celery import Celery
from celery.signals import worker_ready, worker_shutdown
import structlog
import requests
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Setup structured logging
logging.basicConfig(level=logging.INFO)
logger = structlog.get_logger(__name__)

# Prometheus metrics
TASKS_TOTAL = Counter('celery_tasks_total', 'Total number of Celery tasks', ['task_name', 'status'])
TASK_DURATION = Histogram('celery_task_duration_seconds', 'Task execution duration', ['task_name'])
ACTIVE_WORKERS = Gauge('celery_active_workers', 'Number of active Celery workers')

# Initialize Celery app
app = Celery(
    'worker',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379'),
    include=['worker.tasks']
)

# Celery configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,
    
    # Task routing
    task_routes={
        'worker.tasks.send_notification': {'queue': 'notifications'},
        'worker.tasks.process_metrics': {'queue': 'metrics'},
        'worker.tasks.train_ml_model': {'queue': 'ml'},
        'worker.tasks.backup_data': {'queue': 'maintenance'},
    },
    
    # Beat schedule for periodic tasks
    beat_schedule={
        'collect-metrics': {
            'task': 'worker.tasks.collect_metrics',
            'schedule': 60.0,  # Every minute
        },
        'cleanup-old-data': {
            'task': 'worker.tasks.cleanup_old_data',
            'schedule': 3600.0,  # Every hour
        },
        'retrain-ml-models': {
            'task': 'worker.tasks.retrain_ml_models',
            'schedule': 86400.0,  # Every day
        },
        'health-check-services': {
            'task': 'worker.tasks.health_check_services',
            'schedule': 300.0,  # Every 5 minutes
        },
    },
)

@worker_ready.connect
def worker_ready_handler(sender=None, **kwargs):
    """Handler called when worker is ready"""
    logger.info("Celery worker ready", worker_id=sender.hostname)
    ACTIVE_WORKERS.inc()
    
    # Start Prometheus metrics server
    start_http_server(8002)
    logger.info("Prometheus metrics server started on port 8002")

@worker_shutdown.connect
def worker_shutdown_handler(sender=None, **kwargs):
    """Handler called when worker shuts down"""
    logger.info("Celery worker shutting down", worker_id=sender.hostname)
    ACTIVE_WORKERS.dec()

# Task decorator with metrics
def monitored_task(*args, **kwargs):
    def decorator(func):
        @app.task(*args, **kwargs)
        def wrapper(*args, **kwargs):
            task_name = func.__name__
            start_time = time.time()
            
            try:
                logger.info("Task started", task=task_name, args=args, kwargs=kwargs)
                result = func(*args, **kwargs)
                
                duration = time.time() - start_time
                TASK_DURATION.labels(task_name=task_name).observe(duration)
                TASKS_TOTAL.labels(task_name=task_name, status='success').inc()
                
                logger.info("Task completed", task=task_name, duration=duration)
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                TASK_DURATION.labels(task_name=task_name).observe(duration)
                TASKS_TOTAL.labels(task_name=task_name, status='failure').inc()
                
                logger.error("Task failed", task=task_name, error=str(e), duration=duration)
                raise
        
        return wrapper
    return decorator

if __name__ == '__main__':
    app.start()
