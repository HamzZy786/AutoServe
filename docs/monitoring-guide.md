# Monitoring Guide

This guide covers the comprehensive observability and monitoring setup for AutoServe, including metrics, logging, tracing, and alerting.

## Overview

AutoServe implements the three pillars of observability:
- **Metrics**: Quantitative measurements (Prometheus + Grafana)
- **Logs**: Event records (Loki + Fluent Bit)
- **Traces**: Request flow tracking (Jaeger)

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Application │───▶│ Prometheus  │───▶│  Grafana    │
│  Services   │    │   Metrics   │    │ Dashboards │
└─────────────┘    └─────────────┘    └─────────────┘
       │
       ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Fluent Bit  │───▶│    Loki     │───▶│  Grafana    │
│ Log Agent   │    │ Log Storage │    │ Log Query   │
└─────────────┘    └─────────────┘    └─────────────┘
       │
       ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ OpenTelemetry│───▶│   Jaeger    │───▶│ Trace UI    │
│ Tracing     │    │ Trace Store │    │  & Analysis │
└─────────────┘    └─────────────┘    └─────────────┘
```

## Metrics Collection (Prometheus)

### Service Metrics

Each service exposes metrics on `/metrics` endpoint:

#### Backend Service Metrics
```
# Request metrics
http_requests_total{method="GET", endpoint="/api/tasks", status="200"}
http_request_duration_seconds{method="GET", endpoint="/api/tasks"}
http_requests_in_flight{endpoint="/api/tasks"}

# Database metrics
db_connections_active
db_connections_idle
db_query_duration_seconds{operation="select"}

# Custom business metrics
tasks_created_total
tasks_completed_total
tasks_failed_total
user_registrations_total
```

#### Worker Service Metrics
```
# Celery metrics
celery_tasks_total{task="data_processing", state="SUCCESS"}
celery_task_duration_seconds{task="data_processing"}
celery_workers_active
celery_queue_depth{queue="default"}

# Processing metrics
data_records_processed_total
data_processing_errors_total
worker_memory_usage_bytes
```

#### ML Controller Metrics
```
# Scaling metrics
scaling_decisions_total{action="scale_up", service="backend"}
scaling_prediction_accuracy
model_inference_duration_seconds
model_last_training_timestamp

# Kubernetes metrics
kubernetes_pods_running{service="backend"}
kubernetes_pods_pending{service="backend"}
kubernetes_resource_requests{resource="cpu", service="backend"}
```

### Infrastructure Metrics

Kubernetes and system metrics are collected automatically:

```
# Node metrics
node_cpu_usage_percentage
node_memory_usage_bytes
node_disk_usage_bytes
node_network_receive_bytes_total

# Pod metrics
container_cpu_usage_seconds_total
container_memory_usage_bytes
container_network_receive_bytes_total
```

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'worker'
    static_configs:
      - targets: ['worker:8001']
    metrics_path: '/metrics'

  - job_name: 'ml-controller'
    static_configs:
      - targets: ['ml-controller:8002']
    metrics_path: '/metrics'

  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
```

## Logging (Loki + Fluent Bit)

### Log Structure

All services use structured JSON logging:

```json
{
  "timestamp": "2024-01-01T12:00:00.123Z",
  "level": "INFO",
  "service": "backend",
  "module": "auth",
  "message": "User login successful",
  "correlation_id": "abc123",
  "user_id": "user123",
  "request_id": "req456",
  "duration_ms": 45,
  "metadata": {
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0..."
  }
}
```

### Log Levels

- **DEBUG**: Detailed information for diagnosis
- **INFO**: General operational messages
- **WARN**: Potentially harmful situations
- **ERROR**: Error events that might allow application to continue
- **FATAL**: Severe error events that lead to application termination

### Fluent Bit Configuration

```yaml
# fluent-bit.conf
[SERVICE]
    Flush         1
    Log_Level     info
    Daemon        off
    Parsers_File  parsers.conf

[INPUT]
    Name              tail
    Path              /var/log/containers/*.log
    Parser            docker
    Tag               kube.*
    Refresh_Interval  5
    Mem_Buf_Limit     50MB

[FILTER]
    Name                kubernetes
    Match               kube.*
    Kube_URL            https://kubernetes.default.svc:443
    Kube_CA_File        /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    Kube_Token_File     /var/run/secrets/kubernetes.io/serviceaccount/token

[OUTPUT]
    Name                 loki
    Match                *
    Host                 loki
    Port                 3100
    Labels               job=fluent-bit
    Auto_Kubernetes_Labels true
```

### Log Queries

Common LogQL queries for troubleshooting:

```logql
# All error logs in the last hour
{service="backend"} |= "ERROR" | json | level="ERROR" | __error__!="JSONParserErr"

# Authentication failures
{service="backend"} |= "auth" |= "failed" | json | message=~".*authentication.*failed.*"

# High latency requests
{service="backend"} | json | duration_ms > 1000

# Worker task failures
{service="worker"} |= "task" |= "failed" | json | task_status="FAILURE"

# ML scaling decisions
{service="ml-controller"} |= "scaling" | json | action=~"scale_(up|down)"
```

## Distributed Tracing (Jaeger)

### Trace Implementation

Services use OpenTelemetry for distributed tracing:

```python
# Python example
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("process_task")
def process_task(task_id):
    span = trace.get_current_span()
    span.set_attribute("task.id", task_id)
    span.set_attribute("task.type", "data_processing")
    
    try:
        # Task processing logic
        result = do_work(task_id)
        span.set_attribute("task.status", "success")
        span.set_attribute("task.result_size", len(result))
        return result
    except Exception as e:
        span.set_attribute("task.status", "error")
        span.set_attribute("error.message", str(e))
        span.record_exception(e)
        raise
```

### Trace Context Propagation

HTTP headers are used to propagate trace context:

```
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
tracestate: congo=t61rcWkgMzE
```

### Common Trace Queries

- **Service dependency map**: Visualize service interactions
- **Error traces**: Find requests with errors
- **Latency analysis**: Identify slow operations
- **Database queries**: Track database operation performance

## Grafana Dashboards

### Application Overview Dashboard

Key metrics displayed:
- Request rate and error rate
- Response time percentiles (p50, p95, p99)
- Active users and sessions
- Task queue depth and processing rate
- Resource utilization (CPU, memory)

### Kubernetes Infrastructure Dashboard

Infrastructure metrics:
- Cluster resource utilization
- Pod status and distribution
- Node health and capacity
- Network traffic and I/O
- Storage usage

### ML Scaling Dashboard

ML-specific metrics:
- Scaling decisions over time
- Model prediction accuracy
- Resource optimization impact
- Cost savings from intelligent scaling
- Alert correlations

### Database Performance Dashboard

Database metrics:
- Query performance and slow queries
- Connection pool status
- Transaction rates
- Index usage statistics
- Replication lag (if applicable)

## Alerting Rules

### Critical Alerts (Page immediately)

```yaml
# High error rate
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "High error rate detected"
    description: "Error rate is {{ $value }} errors per second"

# Service down
- alert: ServiceDown
  expr: up{job=~"backend|worker|ml-controller"} == 0
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "Service {{ $labels.job }} is down"

# Database connection issues
- alert: DatabaseConnectionHigh
  expr: db_connections_active / db_connections_max > 0.8
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "Database connection pool nearly exhausted"
```

### Warning Alerts (Investigate)

```yaml
# High latency
- alert: HighLatency
  expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "High latency detected"

# Memory usage high
- alert: HighMemoryUsage
  expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.8
  for: 15m
  labels:
    severity: warning
  annotations:
    summary: "High memory usage in {{ $labels.pod }}"

# Disk space low
- alert: LowDiskSpace
  expr: node_filesystem_avail_bytes / node_filesystem_size_bytes < 0.1
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Low disk space on {{ $labels.instance }}"
```

## SLIs and SLOs

### Service Level Indicators (SLIs)

1. **Availability**: Percentage of successful requests
2. **Latency**: 95th percentile response time
3. **Error Rate**: Percentage of failed requests
4. **Throughput**: Requests per second

### Service Level Objectives (SLOs)

```yaml
# Backend API SLOs
backend_api:
  availability: 99.9%  # 99.9% of requests succeed
  latency_p95: 500ms   # 95% of requests complete in <500ms
  error_rate: 0.1%     # <0.1% error rate

# Worker Service SLOs
worker_service:
  availability: 99.5%  # 99.5% of tasks complete successfully
  processing_time: 60s # 95% of tasks complete in <60s
  queue_delay: 30s     # Tasks start processing within 30s

# ML Controller SLOs
ml_controller:
  prediction_accuracy: 85%  # 85% scaling prediction accuracy
  decision_latency: 10s     # Scaling decisions made within 10s
  model_availability: 99%   # Model available 99% of time
```

## Monitoring Setup

### Local Development

```powershell
# Start monitoring stack with Docker Compose
docker-compose up -d prometheus grafana jaeger loki

# Access dashboards
# Grafana: http://localhost:3001 (admin/admin)
# Prometheus: http://localhost:9090
# Jaeger: http://localhost:16686
```

### Kubernetes Deployment

```powershell
# Deploy monitoring stack
kubectl apply -k k8s/monitoring

# Port forward to access services
kubectl port-forward svc/grafana -n monitoring 3000:80
kubectl port-forward svc/prometheus -n monitoring 9090:9090
kubectl port-forward svc/jaeger -n monitoring 16686:16686
```

### Configuration

1. **Import Dashboards**: Dashboards are automatically imported from `monitoring/grafana/dashboards/`
2. **Configure Data Sources**: Prometheus, Loki, and Jaeger are pre-configured
3. **Set Up Alerts**: Alert rules are loaded from `monitoring/prometheus/rules/`

## Troubleshooting

### Common Issues

#### 1. Metrics not showing up
```powershell
# Check Prometheus targets
kubectl port-forward svc/prometheus -n monitoring 9090:9090
# Visit http://localhost:9090/targets

# Check service annotations
kubectl get pods -n autoserve-prod -o yaml | grep prometheus.io
```

#### 2. Logs not appearing in Loki
```powershell
# Check Fluent Bit status
kubectl logs -f daemonset/fluent-bit -n monitoring

# Test Loki connectivity
kubectl exec -it fluent-bit-xxx -n monitoring -- curl http://loki:3100/ready
```

#### 3. Traces not in Jaeger
```powershell
# Check Jaeger collector
kubectl logs -f deployment/jaeger -n monitoring

# Verify trace sampling
# Check application trace configuration
```

### Performance Optimization

#### 1. Reduce metric cardinality
```yaml
# Avoid high cardinality labels
# Bad: user_id as label
http_requests_total{user_id="12345"}

# Good: user_id in log, not metric
http_requests_total{endpoint="/api/users"}
```

#### 2. Optimize log volume
```yaml
# Set appropriate log levels
# Use structured logging
# Sample high-volume logs
```

#### 3. Configure retention policies
```yaml
# Prometheus retention
--storage.tsdb.retention.time=30d

# Loki retention
retention_period: 168h  # 7 days

# Jaeger retention
--store.memory.max-traces=10000
```

## Best Practices

### 1. Metric Naming
- Use consistent naming conventions
- Include units in metric names
- Use labels for dimensions, not metric names

### 2. Log Structure
- Use structured logging (JSON)
- Include correlation IDs
- Log at appropriate levels
- Include context information

### 3. Trace Sampling
- Use appropriate sampling rates
- Sample based on service criticality
- Include important operations
- Tag spans with useful attributes

### 4. Dashboard Design
- Group related metrics
- Use consistent time ranges
- Include SLI/SLO indicators
- Provide drill-down capabilities

### 5. Alert Design
- Alert on symptoms, not causes
- Use appropriate thresholds
- Include runbook links
- Test alert conditions

## Advanced Features

### Custom Metrics

```python
# Python example for custom business metrics
from prometheus_client import Counter, Histogram, Gauge

# Counter for business events
user_registrations = Counter('user_registrations_total', 'Total user registrations')

# Histogram for timing
task_duration = Histogram('task_processing_seconds', 'Task processing time')

# Gauge for current state
active_sessions = Gauge('active_sessions', 'Number of active user sessions')

# Usage
user_registrations.inc()
with task_duration.time():
    process_task()
active_sessions.set(get_session_count())
```

### Log Correlation

```python
# Correlate logs with traces
import logging
from opentelemetry import trace

# Custom log formatter
class TraceFormatter(logging.Formatter):
    def format(self, record):
        span = trace.get_current_span()
        if span:
            record.trace_id = format(span.get_span_context().trace_id, '032x')
            record.span_id = format(span.get_span_context().span_id, '016x')
        return super().format(record)
```

### Anomaly Detection

```python
# ML-based anomaly detection for metrics
from sklearn.ensemble import IsolationForest
import numpy as np

def detect_anomalies(metrics_data):
    model = IsolationForest(contamination=0.1)
    anomalies = model.fit_predict(metrics_data)
    return np.where(anomalies == -1)[0]
```

This monitoring guide provides comprehensive coverage of observability in AutoServe. For specific implementation details, refer to the configuration files in the `monitoring/` directory.
