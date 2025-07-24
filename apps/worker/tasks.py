import os
import json
import time
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import structlog
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

from .worker import monitored_task, app

logger = structlog.get_logger(__name__)

@monitored_task(bind=True)
def send_notification(self, notification_type: str, message: str, recipients: List[str], **kwargs):
    """Send notification to specified recipients"""
    try:
        if notification_type == 'email':
            return send_email_notification(message, recipients)
        elif notification_type == 'slack':
            return send_slack_notification(message, kwargs.get('webhook_url'))
        elif notification_type == 'sms':
            return send_sms_notification(message, recipients)
        else:
            raise ValueError(f"Unknown notification type: {notification_type}")
    except Exception as e:
        logger.error("Notification failed", type=notification_type, error=str(e))
        raise

def send_email_notification(message: str, recipients: List[str]) -> bool:
    """Send email notification (mock implementation)"""
    logger.info("Sending email notification", recipients=recipients, message=message)
    # TODO: Implement actual email sending logic
    time.sleep(1)  # Simulate sending delay
    return True

def send_slack_notification(message: str, webhook_url: str) -> bool:
    """Send Slack notification"""
    if not webhook_url:
        logger.warning("No Slack webhook URL provided")
        return False
    
    payload = {
        "text": message,
        "username": "AutoServe Bot",
        "icon_emoji": ":robot_face:"
    }
    
    response = requests.post(webhook_url, json=payload)
    if response.status_code == 200:
        logger.info("Slack notification sent successfully")
        return True
    else:
        logger.error("Failed to send Slack notification", status_code=response.status_code)
        return False

def send_sms_notification(message: str, recipients: List[str]) -> bool:
    """Send SMS notification (mock implementation)"""
    logger.info("Sending SMS notification", recipients=recipients, message=message)
    # TODO: Implement actual SMS sending logic (Twilio, etc.)
    time.sleep(1)  # Simulate sending delay
    return True

@monitored_task(bind=True)
def process_metrics(self, service_name: str, metrics_data: Dict[str, Any]):
    """Process and aggregate metrics data"""
    try:
        logger.info("Processing metrics", service=service_name, metrics_count=len(metrics_data))
        
        # Calculate aggregations
        processed_metrics = {
            'service_name': service_name,
            'timestamp': datetime.utcnow().isoformat(),
            'avg_cpu': np.mean(metrics_data.get('cpu_values', [])),
            'max_cpu': np.max(metrics_data.get('cpu_values', [])),
            'avg_memory': np.mean(metrics_data.get('memory_values', [])),
            'max_memory': np.max(metrics_data.get('memory_values', [])),
            'request_count': sum(metrics_data.get('request_counts', [])),
            'error_count': sum(metrics_data.get('error_counts', [])),
        }
        
        # Store in database (mock)
        logger.info("Metrics processed", processed_metrics=processed_metrics)
        
        # Check for alerts
        check_metric_alerts.delay(service_name, processed_metrics)
        
        return processed_metrics
    except Exception as e:
        logger.error("Metrics processing failed", service=service_name, error=str(e))
        raise

@monitored_task(bind=True)
def check_metric_alerts(self, service_name: str, metrics: Dict[str, Any]):
    """Check metrics against alert thresholds"""
    try:
        alerts = []
        
        # CPU alert
        if metrics.get('avg_cpu', 0) > 80:
            alerts.append({
                'type': 'cpu_high',
                'severity': 'high' if metrics['avg_cpu'] > 90 else 'medium',
                'message': f"High CPU usage detected: {metrics['avg_cpu']:.1f}%",
                'service': service_name
            })
        
        # Memory alert
        if metrics.get('avg_memory', 0) > 85:
            alerts.append({
                'type': 'memory_high',
                'severity': 'high' if metrics['avg_memory'] > 95 else 'medium',
                'message': f"High memory usage detected: {metrics['avg_memory']:.1f}%",
                'service': service_name
            })
        
        # Error rate alert
        total_requests = metrics.get('request_count', 1)
        error_rate = (metrics.get('error_count', 0) / total_requests) * 100 if total_requests > 0 else 0
        
        if error_rate > 5:
            alerts.append({
                'type': 'error_rate_high',
                'severity': 'critical' if error_rate > 10 else 'high',
                'message': f"High error rate detected: {error_rate:.1f}%",
                'service': service_name
            })
        
        # Send alerts
        for alert in alerts:
            send_notification.delay(
                'slack',
                f"🚨 Alert: {alert['message']} (Service: {alert['service']})",
                [],
                webhook_url=os.getenv('SLACK_WEBHOOK_URL')
            )
        
        return alerts
    except Exception as e:
        logger.error("Alert checking failed", service=service_name, error=str(e))
        raise

@monitored_task(bind=True)
def train_ml_model(self, model_name: str, training_data: Dict[str, Any]):
    """Train machine learning model for scaling predictions"""
    try:
        logger.info("Starting ML model training", model=model_name)
        
        # Generate synthetic training data for demo
        data = generate_synthetic_training_data()
        
        # Prepare features and target
        features = ['cpu_usage', 'memory_usage', 'request_rate', 'response_time', 'hour_of_day', 'day_of_week']
        X = data[features]
        y = data['optimal_replicas']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Save model
        model_path = f"/tmp/{model_name}_{int(time.time())}.joblib"
        joblib.dump({
            'model': model,
            'scaler': scaler,
            'features': features,
            'metrics': {'mae': mae, 'r2_score': r2}
        }, model_path)
        
        logger.info("ML model training completed", 
                   model=model_name, 
                   mae=mae, 
                   r2_score=r2,
                   model_path=model_path)
        
        return {
            'model_name': model_name,
            'model_path': model_path,
            'metrics': {'mae': mae, 'r2_score': r2},
            'trained_at': datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("ML model training failed", model=model_name, error=str(e))
        raise

def generate_synthetic_training_data() -> pd.DataFrame:
    """Generate synthetic training data for ML model"""
    np.random.seed(42)
    n_samples = 10000
    
    data = {
        'cpu_usage': np.random.uniform(10, 95, n_samples),
        'memory_usage': np.random.uniform(20, 90, n_samples),
        'request_rate': np.random.exponential(100, n_samples),
        'response_time': np.random.lognormal(5, 0.5, n_samples),
        'hour_of_day': np.random.randint(0, 24, n_samples),
        'day_of_week': np.random.randint(0, 7, n_samples),
    }
    
    # Create target variable (optimal replicas) based on features
    df = pd.DataFrame(data)
    
    # Simple heuristic for optimal replicas
    df['load_score'] = (
        df['cpu_usage'] * 0.3 +
        df['memory_usage'] * 0.3 +
        np.clip(df['request_rate'] / 100, 0, 100) * 0.4
    )
    
    df['optimal_replicas'] = np.clip(
        np.round(1 + (df['load_score'] / 100) * 9).astype(int),
        1, 10
    )
    
    return df

@monitored_task(bind=True)
def backup_data(self, backup_type: str, **kwargs):
    """Backup data (database, files, etc.)"""
    try:
        logger.info("Starting backup", type=backup_type)
        
        if backup_type == 'database':
            return backup_database()
        elif backup_type == 'metrics':
            return backup_metrics()
        elif backup_type == 'models':
            return backup_ml_models()
        else:
            raise ValueError(f"Unknown backup type: {backup_type}")
    except Exception as e:
        logger.error("Backup failed", type=backup_type, error=str(e))
        raise

def backup_database():
    """Backup database"""
    logger.info("Performing database backup")
    # TODO: Implement actual database backup logic
    time.sleep(5)  # Simulate backup time
    backup_file = f"db_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.sql"
    logger.info("Database backup completed", file=backup_file)
    return backup_file

def backup_metrics():
    """Backup metrics data"""
    logger.info("Performing metrics backup")
    # TODO: Implement actual metrics backup logic
    time.sleep(3)  # Simulate backup time
    backup_file = f"metrics_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    logger.info("Metrics backup completed", file=backup_file)
    return backup_file

def backup_ml_models():
    """Backup ML models"""
    logger.info("Performing ML models backup")
    # TODO: Implement actual models backup logic
    time.sleep(2)  # Simulate backup time
    backup_file = f"models_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.tar.gz"
    logger.info("ML models backup completed", file=backup_file)
    return backup_file

@monitored_task(bind=True)
def collect_metrics(self):
    """Periodic task to collect metrics from services"""
    try:
        logger.info("Starting metrics collection")
        
        # Mock service endpoints
        services = ['frontend', 'backend-api', 'background-worker']
        
        for service in services:
            try:
                # Simulate metrics collection
                metrics = {
                    'cpu_values': [np.random.uniform(20, 80) for _ in range(10)],
                    'memory_values': [np.random.uniform(30, 70) for _ in range(10)],
                    'request_counts': [np.random.poisson(50) for _ in range(10)],
                    'error_counts': [np.random.poisson(2) for _ in range(10)],
                }
                
                # Process metrics asynchronously
                process_metrics.delay(service, metrics)
                
            except Exception as e:
                logger.error("Failed to collect metrics for service", service=service, error=str(e))
        
        logger.info("Metrics collection completed")
        return True
    except Exception as e:
        logger.error("Metrics collection failed", error=str(e))
        raise

@monitored_task(bind=True)
def cleanup_old_data(self):
    """Periodic task to cleanup old data"""
    try:
        logger.info("Starting data cleanup")
        
        # TODO: Implement actual cleanup logic
        # - Remove old metrics (>30 days)
        # - Remove old logs (>7 days)
        # - Remove old backups (>90 days)
        
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        logger.info("Data cleanup completed", cutoff_date=cutoff_date.isoformat())
        
        return True
    except Exception as e:
        logger.error("Data cleanup failed", error=str(e))
        raise

@monitored_task(bind=True)
def retrain_ml_models(self):
    """Periodic task to retrain ML models"""
    try:
        logger.info("Starting ML model retraining")
        
        # Retrain scaling prediction model
        train_ml_model.delay('scaling_predictor', {})
        
        logger.info("ML model retraining scheduled")
        return True
    except Exception as e:
        logger.error("ML model retraining failed", error=str(e))
        raise

@monitored_task(bind=True)
def health_check_services(self):
    """Periodic health check of all services"""
    try:
        logger.info("Starting service health checks")
        
        services = [
            {'name': 'frontend', 'url': 'http://frontend:80/health'},
            {'name': 'backend-api', 'url': 'http://backend:8000/health'},
            {'name': 'ml-controller', 'url': 'http://ml-controller:8000/health'},
        ]
        
        unhealthy_services = []
        
        for service in services:
            try:
                response = requests.get(service['url'], timeout=5)
                if response.status_code != 200:
                    unhealthy_services.append(service['name'])
                    logger.warning("Service health check failed", 
                                 service=service['name'], 
                                 status_code=response.status_code)
            except requests.RequestException as e:
                unhealthy_services.append(service['name'])
                logger.error("Service health check error", 
                           service=service['name'], 
                           error=str(e))
        
        # Send alert if any services are unhealthy
        if unhealthy_services:
            send_notification.delay(
                'slack',
                f"🚨 Unhealthy services detected: {', '.join(unhealthy_services)}",
                [],
                webhook_url=os.getenv('SLACK_WEBHOOK_URL')
            )
        
        logger.info("Service health checks completed", 
                   unhealthy_count=len(unhealthy_services))
        
        return {
            'healthy_services': len(services) - len(unhealthy_services),
            'unhealthy_services': unhealthy_services,
            'total_services': len(services)
        }
    except Exception as e:
        logger.error("Service health checks failed", error=str(e))
        raise
