import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from passlib.context import CryptContext

from .database import Base

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    services = relationship("Service", back_populates="owner")
    
    def set_password(self, password: str):
        self.hashed_password = pwd_context.hash(password)
    
    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)


class Service(Base):
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    image = Column(String, nullable=False)
    replicas = Column(Integer, default=1)
    status = Column(String, default="pending")  # pending, running, stopped, error
    port = Column(Integer, default=80)
    cpu_limit = Column(String, default="500m")
    memory_limit = Column(String, default="512Mi")
    cpu_request = Column(String, default="100m")
    memory_request = Column(String, default="128Mi")
    environment_vars = Column(JSON, default={})
    labels = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Foreign key
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    owner = relationship("User", back_populates="services")
    metrics = relationship("MetricRecord", back_populates="service")


class MetricRecord(Base):
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String, index=True, nullable=False)
    metric_name = Column(String, index=True, nullable=False)
    value = Column(Float, nullable=False)
    labels = Column(JSON, default={})
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    
    # Foreign key (optional - for linking to service)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)
    
    # Relationships
    service = relationship("Service", back_populates="metrics")


class ScalingEvent(Base):
    __tablename__ = "scaling_events"
    
    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String, index=True, nullable=False)
    action = Column(String, nullable=False)  # scale_up, scale_down
    previous_replicas = Column(Integer, nullable=False)
    new_replicas = Column(Integer, nullable=False)
    trigger = Column(String, nullable=False)  # manual, ml_prediction, hpa
    confidence = Column(Float, nullable=True)  # For ML predictions
    reason = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    
    # Metadata
    metadata = Column(JSON, default={})


class MLModel(Base):
    __tablename__ = "ml_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    version = Column(String, nullable=False)
    model_type = Column(String, nullable=False)  # regression, classification, etc.
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    is_active = Column(Boolean, default=False)
    model_path = Column(String, nullable=True)  # Path to serialized model
    training_data_info = Column(JSON, default={})
    hyperparameters = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    trained_at = Column(DateTime, nullable=True)
    
    # Performance tracking
    predictions_made = Column(Integer, default=0)
    correct_predictions = Column(Integer, default=0)


class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String, index=True, nullable=False)
    alert_type = Column(String, nullable=False)  # cpu_high, memory_high, error_rate_high
    severity = Column(String, nullable=False)  # low, medium, high, critical
    message = Column(Text, nullable=False)
    status = Column(String, default="active")  # active, resolved, silenced
    threshold_value = Column(Float, nullable=True)
    current_value = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)
    
    # Notification tracking
    notification_sent = Column(Boolean, default=False)
    notification_channels = Column(JSON, default=[])  # email, slack, sms
