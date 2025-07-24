import os
import time
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import structlog
import requests
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
from kubernetes import client, config
import schedule
import threading

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = structlog.get_logger(__name__)

class MLScalingController:
    def __init__(self):
        self.app = FastAPI(
            title="ML Scaling Controller",
            description="Intelligent Kubernetes scaling using machine learning",
            version="1.0.0"
        )
        
        # Configuration
        self.prometheus_url = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")
        self.confidence_threshold = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))
        self.scaling_cooldown = int(os.getenv("SCALING_COOLDOWN", "300"))  # 5 minutes
        
        # Model storage
        self.models = {}
        self.scalers = {}
        self.last_scaling_times = {}
        
        # Initialize Kubernetes client
        try:
            if os.path.exists('/var/run/secrets/kubernetes.io/serviceaccount'):
                config.load_incluster_config()
            else:
                config.load_kube_config()
            self.k8s_apps_v1 = client.AppsV1Api()
            self.k8s_core_v1 = client.CoreV1Api()
            logger.info("Kubernetes client initialized")
        except Exception as e:
            logger.error("Failed to initialize Kubernetes client", error=str(e))
            self.k8s_apps_v1 = None
            self.k8s_core_v1 = None
        
        self.setup_routes()
        self.setup_middleware()
        self.load_models()
        self.setup_scheduler()
    
    def setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "timestamp": time.time(),
                "models_loaded": len(self.models),
                "kubernetes_connected": self.k8s_apps_v1 is not None
            }
        
        @self.app.post("/predict")
        async def predict_scaling(request: dict):
            """Predict optimal scaling for a service"""
            try:
                service_name = request.get("service_name")
                current_metrics = request.get("metrics", {})
                
                if not service_name:
                    raise HTTPException(status_code=400, detail="service_name is required")
                
                prediction = await self.predict_scaling_decision(service_name, current_metrics)
                return prediction
            except Exception as e:
                logger.error("Prediction failed", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/models")
        async def list_models():
            """List available ML models"""
            return {
                "models": list(self.models.keys()),
                "model_info": {
                    name: {
                        "loaded": True,
                        "type": type(model).__name__
                    } for name, model in self.models.items()
                }
            }
        
        @self.app.post("/models/retrain")
        async def retrain_models():
            """Retrain ML models with latest data"""
            try:
                result = await self.retrain_models()
                return result
            except Exception as e:
                logger.error("Model retraining failed", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/scaling-events")
        async def get_scaling_events():
            """Get recent scaling events"""
            # TODO: Implement scaling events history
            return {"events": []}
        
        @self.app.post("/scale")
        async def manual_scale(request: dict):
            """Manually scale a service"""
            try:
                service_name = request.get("service_name")
                replicas = request.get("replicas")
                namespace = request.get("namespace", "default")
                
                if not service_name or replicas is None:
                    raise HTTPException(status_code=400, detail="service_name and replicas are required")
                
                result = await self.scale_deployment(service_name, replicas, namespace)
                return result
            except Exception as e:
                logger.error("Manual scaling failed", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
    
    def setup_middleware(self):
        """Setup FastAPI middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def load_models(self):
        """Load ML models from disk"""
        try:
            # For demo, create a simple model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            scaler = StandardScaler()
            
            # Generate some synthetic training data
            X_train, y_train = self.generate_synthetic_data()
            X_train_scaled = scaler.fit_transform(X_train)
            model.fit(X_train_scaled, y_train)
            
            self.models['scaling_predictor'] = model
            self.scalers['scaling_predictor'] = scaler
            
            logger.info("ML models loaded successfully")
        except Exception as e:
            logger.error("Failed to load models", error=str(e))
    
    def generate_synthetic_data(self):
        """Generate synthetic training data"""
        np.random.seed(42)
        n_samples = 1000
        
        # Features: CPU, Memory, Request Rate, Response Time, Hour, Day of Week
        X = np.random.rand(n_samples, 6)
        X[:, 0] *= 100  # CPU percentage
        X[:, 1] *= 100  # Memory percentage
        X[:, 2] *= 1000  # Request rate
        X[:, 3] *= 500  # Response time
        X[:, 4] *= 24  # Hour of day
        X[:, 5] *= 7   # Day of week
        
        # Target: Optimal replicas (1-10)
        load_factor = (X[:, 0] * 0.3 + X[:, 1] * 0.3 + X[:, 2] / 100 * 0.4)
        y = np.clip(np.round(1 + (load_factor / 100) * 9), 1, 10)
        
        return X, y
    
    async def get_prometheus_metrics(self, service_name: str, time_range: str = "5m") -> Dict[str, float]:
        """Fetch metrics from Prometheus"""
        try:
            metrics = {}
            
            # Define Prometheus queries
            queries = {
                'cpu_usage': f'avg(rate(cpu_usage_total{{service="{service_name}"}}[{time_range}])) * 100',
                'memory_usage': f'avg(memory_usage_bytes{{service="{service_name}"}}) / avg(memory_limit_bytes{{service="{service_name}"}}) * 100',
                'request_rate': f'sum(rate(http_requests_total{{service="{service_name}"}}[{time_range}]))',
                'response_time': f'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{{service="{service_name}"}}[{time_range}])) * 1000',
                'error_rate': f'sum(rate(http_requests_total{{service="{service_name}",status=~"5.."}}[{time_range}])) / sum(rate(http_requests_total{{service="{service_name}"}}[{time_range}])) * 100'
            }
            
            for metric_name, query in queries.items():
                try:
                    response = requests.get(
                        f"{self.prometheus_url}/api/v1/query",
                        params={'query': query},
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data['data']['result']:
                            value = float(data['data']['result'][0]['value'][1])
                            metrics[metric_name] = value
                        else:
                            metrics[metric_name] = 0.0
                    else:
                        logger.warning(f"Failed to fetch {metric_name} from Prometheus")
                        metrics[metric_name] = 0.0
                        
                except Exception as e:
                    logger.error(f"Error fetching {metric_name}", error=str(e))
                    metrics[metric_name] = 0.0
            
            # Add time-based features
            now = datetime.now()
            metrics['hour_of_day'] = now.hour
            metrics['day_of_week'] = now.weekday()
            
            return metrics
            
        except Exception as e:
            logger.error("Failed to fetch Prometheus metrics", service=service_name, error=str(e))
            return {}
    
    async def predict_scaling_decision(self, service_name: str, current_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Predict optimal scaling decision"""
        try:
            # Get current metrics if not provided
            if not current_metrics:
                current_metrics = await self.get_prometheus_metrics(service_name)
            
            # Get current replica count
            current_replicas = await self.get_current_replicas(service_name)
            
            if 'scaling_predictor' not in self.models:
                return {
                    "service_name": service_name,
                    "current_replicas": current_replicas,
                    "recommended_replicas": current_replicas,
                    "confidence": 0.0,
                    "reason": "No ML model available",
                    "action": "none"
                }
            
            # Prepare features
            features = [
                current_metrics.get('cpu_usage', 0),
                current_metrics.get('memory_usage', 0),
                current_metrics.get('request_rate', 0),
                current_metrics.get('response_time', 0),
                current_metrics.get('hour_of_day', datetime.now().hour),
                current_metrics.get('day_of_week', datetime.now().weekday())
            ]
            
            # Scale features
            model = self.models['scaling_predictor']
            scaler = self.scalers['scaling_predictor']
            features_scaled = scaler.transform([features])
            
            # Make prediction
            predicted_replicas = int(round(model.predict(features_scaled)[0]))
            predicted_replicas = max(1, min(10, predicted_replicas))  # Clamp between 1-10
            
            # Calculate confidence (simplified)
            # In a real implementation, you'd use prediction intervals or ensemble disagreement
            feature_stability = 1.0 - (np.std(features[:4]) / (np.mean(features[:4]) + 1e-6))
            confidence = min(0.95, max(0.5, feature_stability))
            
            # Determine action
            action = "none"
            reason = "Current scaling is optimal"
            
            if predicted_replicas > current_replicas:
                action = "scale_up"
                reason = f"Predicted load increase requires {predicted_replicas} replicas"
            elif predicted_replicas < current_replicas:
                action = "scale_down"
                reason = f"Predicted load decrease allows reduction to {predicted_replicas} replicas"
            
            # Check scaling cooldown
            last_scaling = self.last_scaling_times.get(service_name, 0)
            if time.time() - last_scaling < self.scaling_cooldown:
                action = "none"
                reason = "Scaling cooldown period active"
            
            prediction = {
                "service_name": service_name,
                "current_replicas": current_replicas,
                "recommended_replicas": predicted_replicas,
                "confidence": confidence,
                "reason": reason,
                "action": action,
                "timestamp": time.time(),
                "metrics": current_metrics
            }
            
            # Execute scaling if confidence is high enough
            if (action != "none" and 
                confidence >= self.confidence_threshold and 
                predicted_replicas != current_replicas):
                
                await self.scale_deployment(service_name, predicted_replicas)
                self.last_scaling_times[service_name] = time.time()
                prediction["executed"] = True
            else:
                prediction["executed"] = False
            
            logger.info("Scaling prediction made", prediction=prediction)
            return prediction
            
        except Exception as e:
            logger.error("Prediction failed", service=service_name, error=str(e))
            raise
    
    async def get_current_replicas(self, service_name: str, namespace: str = "default") -> int:
        """Get current replica count for a deployment"""
        try:
            if not self.k8s_apps_v1:
                return 1  # Default if Kubernetes not available
            
            deployment = self.k8s_apps_v1.read_namespaced_deployment(
                name=service_name,
                namespace=namespace
            )
            return deployment.spec.replicas or 1
            
        except Exception as e:
            logger.warning("Failed to get current replicas", service=service_name, error=str(e))
            return 1
    
    async def scale_deployment(self, service_name: str, replicas: int, namespace: str = "default") -> Dict[str, Any]:
        """Scale a Kubernetes deployment"""
        try:
            if not self.k8s_apps_v1:
                logger.warning("Kubernetes not available, simulating scaling")
                return {
                    "service_name": service_name,
                    "replicas": replicas,
                    "status": "simulated",
                    "message": "Kubernetes not available"
                }
            
            # Update deployment replica count
            deployment = self.k8s_apps_v1.read_namespaced_deployment(
                name=service_name,
                namespace=namespace
            )
            
            deployment.spec.replicas = replicas
            
            self.k8s_apps_v1.patch_namespaced_deployment(
                name=service_name,
                namespace=namespace,
                body=deployment
            )
            
            logger.info("Deployment scaled", service=service_name, replicas=replicas)
            
            return {
                "service_name": service_name,
                "replicas": replicas,
                "status": "success",
                "message": f"Scaled {service_name} to {replicas} replicas"
            }
            
        except Exception as e:
            logger.error("Failed to scale deployment", service=service_name, error=str(e))
            return {
                "service_name": service_name,
                "replicas": replicas,
                "status": "error",
                "message": str(e)
            }
    
    async def retrain_models(self) -> Dict[str, Any]:
        """Retrain ML models with latest data"""
        try:
            logger.info("Starting model retraining")
            
            # In a real implementation, you would:
            # 1. Fetch historical metrics and scaling decisions
            # 2. Prepare training data
            # 3. Train new model
            # 4. Validate performance
            # 5. Replace old model if performance is better
            
            # For demo, just reload the existing model
            self.load_models()
            
            return {
                "status": "success",
                "message": "Models retrained successfully",
                "models_updated": list(self.models.keys()),
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error("Model retraining failed", error=str(e))
            return {
                "status": "error",
                "message": str(e),
                "timestamp": time.time()
            }
    
    def setup_scheduler(self):
        """Setup periodic tasks"""
        schedule.every(5).minutes.do(self.periodic_scaling_check)
        schedule.every(1).hours.do(self.model_performance_check)
        schedule.every(1).days.do(self.retrain_models_scheduled)
        
        # Start scheduler in background thread
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(30)
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        logger.info("Scheduler started")
    
    def periodic_scaling_check(self):
        """Periodic scaling check for all services"""
        try:
            # Get list of monitored services
            services = ['frontend', 'backend-api', 'background-worker']
            
            for service in services:
                asyncio.create_task(self.predict_scaling_decision(service, {}))
                
        except Exception as e:
            logger.error("Periodic scaling check failed", error=str(e))
    
    def model_performance_check(self):
        """Check model performance and accuracy"""
        try:
            logger.info("Running model performance check")
            # TODO: Implement model performance monitoring
            
        except Exception as e:
            logger.error("Model performance check failed", error=str(e))
    
    def retrain_models_scheduled(self):
        """Scheduled model retraining"""
        try:
            asyncio.create_task(self.retrain_models())
            
        except Exception as e:
            logger.error("Scheduled model retraining failed", error=str(e))

# Initialize controller
controller = MLScalingController()
app = controller.app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
