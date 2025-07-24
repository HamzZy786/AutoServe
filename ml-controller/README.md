# ML Controller Service

Intelligent scaling controller that uses machine learning to predict optimal resource allocation for services.

## Features

- 🧠 Machine learning-based scaling predictions
- 📊 Real-time metrics analysis
- 🎯 Confidence-based scaling decisions
- 📈 Model performance tracking
- 🔄 Automated model retraining
- ⚙️ Kubernetes API integration

## Local Development

```bash
cd ml-controller
pip install -r requirements.txt
python controller.py
```

## Models

- **Scaling Predictor**: Predicts optimal replica count
- **Anomaly Detector**: Detects unusual traffic patterns
- **Load Forecaster**: Forecasts future resource needs

## API Endpoints

- `GET /health`: Health check
- `POST /predict`: Get scaling prediction
- `GET /models`: List available models
- `POST /models/retrain`: Retrain models

## Environment Variables

- `PROMETHEUS_URL`: Prometheus server URL
- `KUBERNETES_SERVICE_HOST`: Kubernetes API server
- `MODEL_UPDATE_INTERVAL`: Model retraining interval
