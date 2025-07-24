from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr


# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Service schemas
class ServiceBase(BaseModel):
    name: str
    image: str
    replicas: int = 1
    port: int = 80

class ServiceCreate(ServiceBase):
    cpu_limit: Optional[str] = "500m"
    memory_limit: Optional[str] = "512Mi"
    cpu_request: Optional[str] = "100m"
    memory_request: Optional[str] = "128Mi"
    environment_vars: Optional[Dict[str, str]] = {}
    labels: Optional[Dict[str, str]] = {}

class ServiceResponse(ServiceBase):
    id: int
    status: str
    cpu_limit: str
    memory_limit: str
    cpu_request: str
    memory_request: str
    environment_vars: Dict[str, str]
    labels: Dict[str, str]
    created_at: datetime
    updated_at: datetime
    owner_id: int

    class Config:
        from_attributes = True


# Metric schemas
class MetricBase(BaseModel):
    service_name: str
    metric_name: str
    value: float

class MetricCreate(MetricBase):
    labels: Optional[Dict[str, str]] = {}

class MetricResponse(MetricBase):
    id: int
    labels: Dict[str, str]
    timestamp: datetime

    class Config:
        from_attributes = True


# Scaling event schemas
class ScalingEventBase(BaseModel):
    service_name: str
    action: str
    previous_replicas: int
    new_replicas: int
    trigger: str

class ScalingEventCreate(ScalingEventBase):
    confidence: Optional[float] = None
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

class ScalingEventResponse(ScalingEventBase):
    id: int
    confidence: Optional[float]
    reason: Optional[str]
    timestamp: datetime
    metadata: Dict[str, Any]

    class Config:
        from_attributes = True


# ML Model schemas
class MLModelBase(BaseModel):
    name: str
    version: str
    model_type: str

class MLModelCreate(MLModelBase):
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    hyperparameters: Optional[Dict[str, Any]] = {}

class MLModelResponse(MLModelBase):
    id: int
    accuracy: Optional[float]
    precision: Optional[float]
    recall: Optional[float]
    f1_score: Optional[float]
    is_active: bool
    predictions_made: int
    correct_predictions: int
    created_at: datetime
    trained_at: Optional[datetime]

    class Config:
        from_attributes = True


# Alert schemas
class AlertBase(BaseModel):
    service_name: str
    alert_type: str
    severity: str
    message: str

class AlertCreate(AlertBase):
    threshold_value: Optional[float] = None
    current_value: Optional[float] = None

class AlertResponse(AlertBase):
    id: int
    status: str
    threshold_value: Optional[float]
    current_value: Optional[float]
    created_at: datetime
    resolved_at: Optional[datetime]
    notification_sent: bool

    class Config:
        from_attributes = True


# Health check schema
class HealthResponse(BaseModel):
    status: str
    timestamp: float
    version: str
    checks: Dict[str, str]


# Prediction schemas
class PredictionRequest(BaseModel):
    service_name: str
    metrics: Dict[str, float]
    time_window: Optional[str] = "1h"

class PredictionResponse(BaseModel):
    service_name: str
    current_replicas: int
    recommended_replicas: int
    confidence: float
    reason: str
    timestamp: float
    metadata: Optional[Dict[str, Any]] = {}


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


# Dashboard data schemas
class DashboardMetrics(BaseModel):
    total_services: int
    running_services: int
    total_replicas: int
    avg_cpu_usage: float
    avg_memory_usage: float
    request_rate: float
    error_rate: float
    response_time: float

class ServiceStatus(BaseModel):
    name: str
    status: str
    replicas: int
    cpu_usage: float
    memory_usage: float
    request_rate: float
    error_rate: float
