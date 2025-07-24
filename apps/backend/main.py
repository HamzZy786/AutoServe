import os
import time
import logging
from contextlib import asynccontextmanager
from typing import List

import structlog
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import start_http_server
import redis
from sqlalchemy.orm import Session

from .database import engine, SessionLocal, Base
from .models import User, Service, MetricRecord
from .schemas import (
    UserCreate, UserResponse, ServiceCreate, ServiceResponse,
    MetricCreate, MetricResponse, HealthResponse
)
from .auth import get_current_user, create_access_token, verify_password
from .monitoring import setup_tracing, get_logger

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

# Setup structured logging
logger = get_logger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting AutoServe Backend API")
    
    # Start Prometheus metrics server
    start_http_server(8001)
    logger.info("Prometheus metrics server started on port 8001")
    
    yield
    
    logger.info("Shutting down AutoServe Backend API")

# Initialize FastAPI app
app = FastAPI(
    title="AutoServe Backend API",
    description="Self-Healing, Auto-Scaling Microservices Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Setup tracing
setup_tracing(app)

# Security
security = HTTPBearer()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Redis connection
def get_redis():
    return redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# Middleware for metrics
@app.middleware("http")
async def metrics_middleware(request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    REQUEST_DURATION.observe(duration)
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    response.headers["X-Process-Time"] = str(duration)
    return response

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint for load balancer"""
    try:
        # Check database connection
        db.execute("SELECT 1")
        
        # Check Redis connection
        r = get_redis()
        r.ping()
        
        return HealthResponse(
            status="healthy",
            timestamp=time.time(),
            version="1.0.0",
            checks={
                "database": "healthy",
                "redis": "healthy"
            }
        )
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unavailable")

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

# Authentication endpoints
@app.post("/auth/login")
async def login(username: str, password: str, db: Session = Depends(get_db)):
    """Login endpoint"""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# User management
@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    db_user = User(username=user.username, email=user.email)
    db_user.set_password(user.password)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    logger.info("User created", username=user.username)
    return db_user

@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

# Service management
@app.get("/services/", response_model=List[ServiceResponse])
async def list_services(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all services"""
    services = db.query(Service).offset(skip).limit(limit).all()
    return services

@app.post("/services/", response_model=ServiceResponse)
async def create_service(
    service: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new service"""
    db_service = Service(
        name=service.name,
        image=service.image,
        replicas=service.replicas,
        status="deploying",
        owner_id=current_user.id
    )
    
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    
    logger.info("Service created", service_name=service.name, owner=current_user.username)
    
    # TODO: Deploy to Kubernetes
    
    return db_service

@app.get("/services/{service_id}", response_model=ServiceResponse)
async def get_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get service by ID"""
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@app.delete("/services/{service_id}")
async def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a service"""
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # TODO: Remove from Kubernetes
    
    db.delete(service)
    db.commit()
    
    logger.info("Service deleted", service_name=service.name, owner=current_user.username)
    return {"message": "Service deleted successfully"}

# Metrics collection
@app.post("/metrics/", response_model=MetricResponse)
async def record_metric(
    metric: MetricCreate,
    db: Session = Depends(get_db)
):
    """Record a metric value"""
    db_metric = MetricRecord(
        service_name=metric.service_name,
        metric_name=metric.metric_name,
        value=metric.value,
        labels=metric.labels
    )
    
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    
    return db_metric

@app.get("/metrics/{service_name}")
async def get_service_metrics(
    service_name: str,
    metric_name: str = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get metrics for a service"""
    query = db.query(MetricRecord).filter(MetricRecord.service_name == service_name)
    
    if metric_name:
        query = query.filter(MetricRecord.metric_name == metric_name)
    
    metrics = query.order_by(MetricRecord.timestamp.desc()).limit(limit).all()
    return metrics

# ML predictions endpoint
@app.post("/predict/scaling")
async def predict_scaling(
    service_name: str,
    current_metrics: dict,
    current_user: User = Depends(get_current_user)
):
    """Predict scaling requirements for a service"""
    # TODO: Implement ML prediction logic
    
    logger.info("Scaling prediction requested", 
                service_name=service_name, 
                user=current_user.username)
    
    # Mock prediction
    prediction = {
        "service_name": service_name,
        "current_replicas": current_metrics.get("replicas", 1),
        "recommended_replicas": current_metrics.get("replicas", 1) + 1,
        "confidence": 0.85,
        "reason": "Predicted traffic increase based on historical patterns",
        "timestamp": time.time()
    }
    
    return prediction

# WebSocket endpoint for real-time updates
@app.websocket("/ws/metrics")
async def websocket_metrics(websocket):
    """WebSocket endpoint for real-time metrics"""
    await websocket.accept()
    try:
        while True:
            # Send real-time metrics
            data = {
                "timestamp": time.time(),
                "cpu_usage": 45.2,
                "memory_usage": 67.8,
                "request_rate": 1234,
                "error_rate": 0.12
            }
            await websocket.send_json(data)
            await asyncio.sleep(1)
    except Exception as e:
        logger.error("WebSocket connection error", error=str(e))
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
