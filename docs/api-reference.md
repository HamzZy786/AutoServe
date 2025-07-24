# API Reference

This document provides comprehensive API documentation for AutoServe services.

## Overview

AutoServe exposes RESTful APIs for all core functionalities. All APIs use JSON for request/response payloads and follow OpenAPI 3.0 specification.

## Base URLs

- **Development**: `http://localhost:8000`
- **Staging**: `https://api-staging.autoserve.com`
- **Production**: `https://api.autoserve.com`

## Authentication

AutoServe uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

### Authentication Endpoints

#### POST /auth/login
Authenticate user and receive JWT token.

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### POST /auth/refresh
Refresh JWT token using refresh token.

**Request:**
```json
{
  "refresh_token": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### POST /auth/logout
Invalidate JWT token.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

## Core API Endpoints

### Health and Status

#### GET /health
Check service health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0",
  "dependencies": {
    "database": "healthy",
    "redis": "healthy"
  }
}
```

#### GET /metrics
Prometheus metrics endpoint (plain text format).

#### GET /info
Get service information.

**Response:**
```json
{
  "name": "autoserve-backend",
  "version": "1.0.0",
  "description": "AutoServe Backend API",
  "environment": "production"
}
```

### User Management

#### GET /users/me
Get current user profile.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "id": "uuid",
  "username": "string",
  "email": "string",
  "full_name": "string",
  "is_active": true,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

#### PUT /users/me
Update current user profile.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request:**
```json
{
  "full_name": "string",
  "email": "string"
}
```

**Response:**
```json
{
  "id": "uuid",
  "username": "string",
  "email": "string",
  "full_name": "string",
  "is_active": true,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

#### POST /users/register
Register new user.

**Request:**
```json
{
  "username": "string",
  "password": "string",
  "email": "string",
  "full_name": "string"
}
```

**Response:**
```json
{
  "id": "uuid",
  "username": "string",
  "email": "string",
  "full_name": "string",
  "is_active": true,
  "created_at": "2024-01-01T12:00:00Z"
}
```

### Task Management

#### GET /tasks
List tasks for current user.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Query Parameters:**
- `limit` (int, optional): Number of tasks to return (default: 50, max: 100)
- `offset` (int, optional): Offset for pagination (default: 0)
- `status` (string, optional): Filter by task status (pending, running, completed, failed)

**Response:**
```json
{
  "tasks": [
    {
      "id": "uuid",
      "title": "string",
      "description": "string",
      "status": "pending",
      "priority": "normal",
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z",
      "scheduled_at": "2024-01-01T12:30:00Z",
      "completed_at": null,
      "result": null,
      "error": null
    }
  ],
  "total": 10,
  "limit": 50,
  "offset": 0
}
```

#### POST /tasks
Create a new task.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request:**
```json
{
  "title": "string",
  "description": "string",
  "priority": "normal",
  "scheduled_at": "2024-01-01T12:30:00Z",
  "task_type": "data_processing",
  "parameters": {
    "input_file": "file.csv",
    "output_format": "json"
  }
}
```

**Response:**
```json
{
  "id": "uuid",
  "title": "string",
  "description": "string",
  "status": "pending",
  "priority": "normal",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "scheduled_at": "2024-01-01T12:30:00Z",
  "task_type": "data_processing",
  "parameters": {
    "input_file": "file.csv",
    "output_format": "json"
  }
}
```

#### GET /tasks/{task_id}
Get specific task details.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "id": "uuid",
  "title": "string",
  "description": "string",
  "status": "completed",
  "priority": "normal",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:35:00Z",
  "scheduled_at": "2024-01-01T12:30:00Z",
  "completed_at": "2024-01-01T12:35:00Z",
  "task_type": "data_processing",
  "parameters": {
    "input_file": "file.csv",
    "output_format": "json"
  },
  "result": {
    "output_file": "processed_data.json",
    "records_processed": 1000
  },
  "error": null
}
```

#### PUT /tasks/{task_id}
Update task details.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request:**
```json
{
  "title": "string",
  "description": "string",
  "priority": "high"
}
```

**Response:**
```json
{
  "id": "uuid",
  "title": "string",
  "description": "string",
  "status": "pending",
  "priority": "high",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:10:00Z"
}
```

#### DELETE /tasks/{task_id}
Cancel/delete a task.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "message": "Task cancelled successfully"
}
```

#### POST /tasks/{task_id}/retry
Retry a failed task.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "id": "uuid",
  "status": "pending",
  "retry_count": 1,
  "updated_at": "2024-01-01T12:45:00Z"
}
```

### System Metrics

#### GET /metrics/system
Get system performance metrics.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "cpu_usage": 45.2,
  "memory_usage": 67.8,
  "disk_usage": 23.1,
  "network_io": {
    "bytes_sent": 1048576,
    "bytes_received": 2097152
  },
  "active_connections": 25,
  "request_rate": 150.5,
  "error_rate": 0.2
}
```

#### GET /metrics/tasks
Get task processing metrics.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "tasks_total": 1000,
  "tasks_pending": 5,
  "tasks_running": 3,
  "tasks_completed": 990,
  "tasks_failed": 2,
  "average_processing_time": 45.2,
  "queue_depth": 8,
  "worker_count": 3,
  "throughput": 22.5
}
```

### File Management

#### POST /files/upload
Upload a file for processing.

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data
```

**Request:**
```
file: <binary_data>
description: string (optional)
```

**Response:**
```json
{
  "id": "uuid",
  "filename": "example.csv",
  "size": 1048576,
  "content_type": "text/csv",
  "description": "Data file for processing",
  "upload_date": "2024-01-01T12:00:00Z",
  "status": "uploaded"
}
```

#### GET /files/{file_id}
Get file metadata.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "id": "uuid",
  "filename": "example.csv",
  "size": 1048576,
  "content_type": "text/csv",
  "description": "Data file for processing",
  "upload_date": "2024-01-01T12:00:00Z",
  "status": "processed",
  "download_url": "https://api.autoserve.com/files/uuid/download"
}
```

#### GET /files/{file_id}/download
Download file content.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
Binary file content with appropriate Content-Type header.

## ML Controller API

The ML Controller service provides APIs for auto-scaling and machine learning operations.

### Base URL
- **Development**: `http://localhost:8001`
- **Production**: `https://ml.autoserve.com`

#### GET /ml/scaling/predictions
Get scaling predictions.

**Response:**
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "predictions": [
    {
      "service": "backend",
      "current_replicas": 3,
      "predicted_replicas": 5,
      "confidence": 0.85,
      "reason": "Traffic spike predicted in next 5 minutes",
      "prediction_horizon": "5m"
    }
  ],
  "model_version": "1.2.3",
  "model_accuracy": 0.89
}
```

#### GET /ml/scaling/history
Get scaling history and decisions.

**Query Parameters:**
- `hours` (int, optional): Hours of history to return (default: 24, max: 168)

**Response:**
```json
{
  "history": [
    {
      "timestamp": "2024-01-01T11:55:00Z",
      "service": "backend",
      "action": "scale_up",
      "from_replicas": 3,
      "to_replicas": 5,
      "trigger": "ml_prediction",
      "metrics": {
        "cpu_usage": 78.5,
        "memory_usage": 65.2,
        "request_rate": 250.0
      }
    }
  ],
  "total_decisions": 48,
  "accuracy_rate": 0.91
}
```

#### POST /ml/model/retrain
Trigger model retraining.

**Request:**
```json
{
  "model_type": "scaling_predictor",
  "training_hours": 168,
  "force_retrain": false
}
```

**Response:**
```json
{
  "job_id": "uuid",
  "status": "started",
  "estimated_duration": "30m",
  "message": "Model retraining started"
}
```

## Error Responses

All APIs return consistent error responses:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    },
    "timestamp": "2024-01-01T12:00:00Z",
    "request_id": "uuid"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| VALIDATION_ERROR | 400 | Invalid request parameters |
| UNAUTHORIZED | 401 | Missing or invalid authentication |
| FORBIDDEN | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource not found |
| CONFLICT | 409 | Resource already exists |
| RATE_LIMITED | 429 | Too many requests |
| INTERNAL_ERROR | 500 | Server error |
| SERVICE_UNAVAILABLE | 503 | Service temporarily unavailable |

## Rate Limiting

APIs are rate limited to ensure fair usage:

- **Anonymous**: 100 requests per hour
- **Authenticated**: 1000 requests per hour
- **Premium**: 10000 requests per hour

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## WebSocket API

Real-time updates are available via WebSocket connections.

### Connection
```
WSS /ws/events?token=<jwt_token>
```

### Event Types

#### Task Status Updates
```json
{
  "type": "task_status",
  "data": {
    "task_id": "uuid",
    "status": "running",
    "progress": 45,
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

#### System Metrics
```json
{
  "type": "system_metrics",
  "data": {
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "active_connections": 25,
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

#### Scaling Events
```json
{
  "type": "scaling_event",
  "data": {
    "service": "backend",
    "action": "scale_up",
    "from_replicas": 3,
    "to_replicas": 5,
    "reason": "High CPU usage",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

## SDK and Client Libraries

### Python SDK

```python
from autoserve_sdk import AutoServeClient

client = AutoServeClient(
    base_url="https://api.autoserve.com",
    api_key="your_api_key"
)

# Authenticate
token = client.auth.login("username", "password")

# Create task
task = client.tasks.create({
    "title": "Process data",
    "task_type": "data_processing",
    "parameters": {"input_file": "data.csv"}
})

# Get task status
status = client.tasks.get(task.id)
```

### JavaScript SDK

```javascript
import { AutoServeClient } from '@autoserve/sdk';

const client = new AutoServeClient({
  baseUrl: 'https://api.autoserve.com',
  apiKey: 'your_api_key'
});

// Authenticate
const token = await client.auth.login('username', 'password');

// Create task
const task = await client.tasks.create({
  title: 'Process data',
  taskType: 'data_processing',
  parameters: { inputFile: 'data.csv' }
});
```

## Interactive API Documentation

Interactive API documentation is available at:
- **Development**: http://localhost:8000/docs
- **Production**: https://api.autoserve.com/docs

The interactive docs provide:
- Complete API schema
- Try-it-now functionality
- Request/response examples
- Authentication testing
- Schema validation

For additional API examples and tutorials, see the [Examples](./examples/) directory.
