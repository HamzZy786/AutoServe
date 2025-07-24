# Troubleshooting Guide

This guide helps diagnose and resolve common issues with AutoServe deployment and operation.

## Quick Diagnostics

### Health Check Commands

```powershell
# Check all pod status
kubectl get pods -n autoserve-prod

# Check service endpoints
kubectl get endpoints -n autoserve-prod

# Check ingress configuration
kubectl get ingress -n autoserve-prod

# Check HPA status
kubectl get hpa -n autoserve-prod

# Check recent events
kubectl get events -n autoserve-prod --sort-by='.lastTimestamp'
```

## Common Issues

### 1. Pods Not Starting

#### Symptoms
- Pods stuck in `Pending`, `CrashLoopBackOff`, or `ImagePullBackOff` status
- Services unavailable

#### Diagnosis
```powershell
# Check pod details
kubectl describe pod <pod-name> -n autoserve-prod

# Check pod logs
kubectl logs <pod-name> -n autoserve-prod --previous

# Check resource quotas
kubectl describe quota -n autoserve-prod

# Check node resources
kubectl top nodes
kubectl describe nodes
```

#### Common Causes and Solutions

**Image Pull Issues**
```powershell
# Check image exists and is accessible
docker pull autoserve/backend:latest

# Verify image registry credentials
kubectl get secrets -n autoserve-prod
kubectl describe secret regcred -n autoserve-prod

# Update image pull policy
kubectl patch deployment backend -p '{"spec":{"template":{"spec":{"containers":[{"name":"backend","imagePullPolicy":"Always"}]}}}}'
```

**Resource Constraints**
```powershell
# Check resource requests vs. available
kubectl describe node <node-name>

# Temporarily reduce resource requests
kubectl patch deployment backend -p '{"spec":{"template":{"spec":{"containers":[{"name":"backend","resources":{"requests":{"memory":"128Mi","cpu":"100m"}}}]}}}}'

# Scale down other non-essential workloads
kubectl scale deployment non-essential-app --replicas=0
```

**Configuration Issues**
```powershell
# Check ConfigMaps
kubectl get configmaps -n autoserve-prod
kubectl describe configmap app-config -n autoserve-prod

# Check Secrets
kubectl get secrets -n autoserve-prod
kubectl describe secret app-secrets -n autoserve-prod

# Validate YAML syntax
kubectl apply --dry-run=client -f k8s/overlays/prod/
```

### 2. Service Connectivity Issues

#### Symptoms
- 503 Service Unavailable errors
- Connection timeouts
- Services can't reach each other

#### Diagnosis
```powershell
# Check service endpoints
kubectl get endpoints backend -n autoserve-prod

# Test service DNS resolution
kubectl run debug --rm -i --tty --image=busybox -- nslookup backend.autoserve-prod.svc.cluster.local

# Test port connectivity
kubectl run debug --rm -i --tty --image=busybox -- telnet backend.autoserve-prod.svc.cluster.local 8000

# Check network policies
kubectl get networkpolicies -n autoserve-prod
```

#### Solutions

**Service Selector Mismatch**
```powershell
# Check service selector matches pod labels
kubectl get service backend -o yaml
kubectl get pods --show-labels -n autoserve-prod

# Fix service selector
kubectl patch service backend -p '{"spec":{"selector":{"app":"backend","version":"v1"}}}'
```

**Port Configuration**
```powershell
# Verify service ports
kubectl describe service backend -n autoserve-prod

# Check container ports
kubectl describe pod <backend-pod> -n autoserve-prod

# Update service port
kubectl patch service backend -p '{"spec":{"ports":[{"port":8000,"targetPort":8000}]}}'
```

**Network Policy Restrictions**
```powershell
# Temporarily disable network policies for testing
kubectl delete networkpolicy --all -n autoserve-prod

# Check policy rules
kubectl describe networkpolicy allow-backend -n autoserve-prod
```

### 3. Database Connection Issues

#### Symptoms
- Database connection errors in application logs
- Slow query performance
- Connection pool exhaustion

#### Diagnosis
```powershell
# Check PostgreSQL pod status
kubectl get pods -l app=postgres -n autoserve-prod

# Check PostgreSQL logs
kubectl logs -f deployment/postgres -n autoserve-prod

# Test database connectivity
kubectl run pg-client --rm -i --tty --image=postgres:14 -- psql -h postgres.autoserve-prod.svc.cluster.local -U autoserve -d autoserve

# Check connection pool metrics
curl http://backend.autoserve-prod.svc.cluster.local:8000/metrics | grep db_connections
```

#### Solutions

**Connection String Issues**
```powershell
# Check database configuration
kubectl get configmap app-config -o yaml
kubectl get secret app-secrets -o yaml

# Update connection string
kubectl patch configmap app-config -p '{"data":{"DATABASE_URL":"postgresql://autoserve:password@postgres:5432/autoserve"}}'
```

**Connection Pool Configuration**
```python
# Update connection pool settings in application
DATABASE_CONFIG = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_timeout": 30,
    "pool_recycle": 3600
}
```

**Database Performance**
```sql
-- Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Check connection count
SELECT count(*) as connections, state 
FROM pg_stat_activity 
GROUP BY state;

-- Check index usage
SELECT schemaname, tablename, attname, n_distinct, correlation 
FROM pg_stats 
WHERE tablename = 'your_table';
```

### 4. Autoscaling Not Working

#### Symptoms
- HPA not scaling despite high load
- Pods not starting during scale-up
- Erratic scaling behavior

#### Diagnosis
```powershell
# Check HPA status
kubectl describe hpa backend-hpa -n autoserve-prod

# Check metrics server
kubectl get pods -n kube-system | grep metrics-server
kubectl logs -f deployment/metrics-server -n kube-system

# Check custom metrics
kubectl get --raw "/apis/custom.metrics.k8s.io/v1beta1"

# Check pod resource usage
kubectl top pods -n autoserve-prod
```

#### Solutions

**Metrics Server Issues**
```powershell
# Restart metrics server
kubectl rollout restart deployment/metrics-server -n kube-system

# Check metrics server configuration
kubectl describe deployment metrics-server -n kube-system

# Verify kubelet metrics
kubectl get --raw "/api/v1/nodes/<node-name>/proxy/metrics/cadvisor"
```

**HPA Configuration**
```powershell
# Update HPA thresholds
kubectl patch hpa backend-hpa -p '{"spec":{"targetCPUUtilizationPercentage":70}}'

# Add custom metrics
kubectl patch hpa backend-hpa -p '{
  "spec": {
    "metrics": [
      {
        "type": "Resource",
        "resource": {
          "name": "cpu",
          "target": {
            "type": "Utilization",
            "averageUtilization": 70
          }
        }
      }
    ]
  }
}'
```

**Resource Limits**
```powershell
# Ensure resource requests are set
kubectl patch deployment backend -p '{
  "spec": {
    "template": {
      "spec": {
        "containers": [
          {
            "name": "backend",
            "resources": {
              "requests": {
                "cpu": "100m",
                "memory": "128Mi"
              },
              "limits": {
                "cpu": "500m",
                "memory": "512Mi"
              }
            }
          }
        ]
      }
    }
  }
}'
```

### 5. ML Controller Issues

#### Symptoms
- Scaling predictions not accurate
- ML service not responding
- Model training failures

#### Diagnosis
```powershell
# Check ML controller logs
kubectl logs -f deployment/ml-controller -n autoserve-prod

# Check ML controller metrics
curl http://ml-controller.autoserve-prod.svc.cluster.local:8002/metrics

# Test ML API
curl http://ml-controller.autoserve-prod.svc.cluster.local:8002/health
curl http://ml-controller.autoserve-prod.svc.cluster.local:8002/ml/scaling/predictions
```

#### Solutions

**Model Loading Issues**
```python
# Check model file permissions and paths
import os
model_path = "/app/models/scaling_model.pkl"
print(f"Model exists: {os.path.exists(model_path)}")
print(f"Model readable: {os.access(model_path, os.R_OK)}")

# Retrain model with more data
curl -X POST http://ml-controller:8002/ml/model/retrain \
  -H "Content-Type: application/json" \
  -d '{"training_hours": 168, "force_retrain": true}'
```

**Prediction Accuracy**
```python
# Check prediction accuracy metrics
import requests
response = requests.get("http://ml-controller:8002/ml/scaling/history")
accuracy = response.json().get("accuracy_rate", 0)
print(f"Current accuracy: {accuracy}")

# Adjust model parameters
if accuracy < 0.8:
    # Increase training data
    # Tune hyperparameters
    # Add more features
```

### 6. Monitoring and Observability Issues

#### Symptoms
- Metrics not appearing in Grafana
- Logs not showing in Loki
- Traces missing in Jaeger

#### Diagnosis
```powershell
# Check monitoring stack
kubectl get pods -n monitoring

# Check Prometheus targets
kubectl port-forward svc/prometheus -n monitoring 9090:9090
# Visit http://localhost:9090/targets

# Check Grafana data sources
kubectl port-forward svc/grafana -n monitoring 3000:80
# Visit http://localhost:3000

# Check log collection
kubectl logs -f daemonset/fluent-bit -n monitoring
```

#### Solutions

**Prometheus Scraping Issues**
```powershell
# Check service annotations
kubectl patch service backend -p '{
  "metadata": {
    "annotations": {
      "prometheus.io/scrape": "true",
      "prometheus.io/port": "8000",
      "prometheus.io/path": "/metrics"
    }
  }
}'

# Verify metrics endpoint
kubectl exec -it <backend-pod> -- curl localhost:8000/metrics
```

**Grafana Dashboard Issues**
```powershell
# Reload Grafana configuration
kubectl rollout restart deployment/grafana -n monitoring

# Check dashboard JSON syntax
cat monitoring/grafana/dashboards/application-overview.json | jq .

# Import dashboard manually
# Use Grafana UI: + → Import → paste JSON
```

**Log Collection Issues**
```powershell
# Check Fluent Bit configuration
kubectl describe configmap fluent-bit-config -n monitoring

# Test Loki connectivity
kubectl exec -it fluent-bit-xxx -n monitoring -- curl http://loki:3100/ready

# Check log format
kubectl logs <app-pod> -n autoserve-prod | head -5
```

### 7. Performance Issues

#### Symptoms
- High response times
- CPU/Memory spikes
- Queue backlog

#### Diagnosis Tools
```powershell
# Application Performance Monitoring
kubectl exec -it <backend-pod> -- top
kubectl exec -it <backend-pod> -- iostat -x 1
kubectl exec -it <backend-pod> -- netstat -tulpn

# Database Performance
kubectl exec -it postgres-pod -- psql -U autoserve -c "
SELECT 
  query,
  mean_time,
  calls,
  total_time
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;"

# Cache Performance
kubectl exec -it redis-pod -- redis-cli info stats
kubectl exec -it redis-pod -- redis-cli info memory
```

#### Solutions

**Application Optimization**
```python
# Add caching
from functools import lru_cache

@lru_cache(maxsize=1000)
def expensive_operation(param):
    return result

# Optimize database queries
# Use connection pooling
# Add database indexes
# Implement pagination
```

**Resource Scaling**
```powershell
# Scale horizontally
kubectl scale deployment backend --replicas=5

# Scale vertically
kubectl patch deployment backend -p '{
  "spec": {
    "template": {
      "spec": {
        "containers": [
          {
            "name": "backend",
            "resources": {
              "requests": {
                "cpu": "200m",
                "memory": "256Mi"
              },
              "limits": {
                "cpu": "1000m",
                "memory": "1Gi"
              }
            }
          }
        ]
      }
    }
  }
}'
```

## Debug Utilities

### Debug Pod for Troubleshooting

```powershell
# Create debug pod with networking tools
kubectl run debug --rm -i --tty --image=nicolaka/netshoot -- /bin/bash

# Inside debug pod, you can:
# Test DNS: nslookup backend.autoserve-prod.svc.cluster.local
# Test connectivity: telnet backend 8000
# Check routes: ip route
# Test HTTP: curl http://backend:8000/health
```

### Log Analysis Scripts

```powershell
# Get recent error logs
kubectl logs --since=1h --selector=app=backend | grep ERROR

# Get logs with specific correlation ID
kubectl logs --selector=app=backend | grep "correlation_id=abc123"

# Aggregate error patterns
kubectl logs --selector=app=backend | grep ERROR | awk '{print $NF}' | sort | uniq -c | sort -nr
```

### Performance Profiling

```python
# Python profiling
import cProfile
import pstats

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Your code here
    result = expensive_function()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative').print_stats(10)
    
    return result
```

## Recovery Procedures

### Database Recovery

```powershell
# Restore from backup
kubectl exec -i postgres-pod -- psql -U autoserve -d autoserve < backup.sql

# Reset database (destructive)
kubectl exec -it postgres-pod -- psql -U autoserve -c "DROP DATABASE autoserve;"
kubectl exec -it postgres-pod -- psql -U autoserve -c "CREATE DATABASE autoserve;"
kubectl exec -it backend-pod -- python scripts/database/migrate.py
```

### Service Recovery

```powershell
# Restart deployment
kubectl rollout restart deployment/backend -n autoserve-prod

# Rollback to previous version
kubectl rollout undo deployment/backend -n autoserve-prod

# Force pod recreation
kubectl delete pods -l app=backend -n autoserve-prod
```

### Configuration Recovery

```powershell
# Restore ConfigMap from Git
kubectl apply -f k8s/base/configmaps/

# Update configuration without restart
kubectl patch configmap app-config -p '{"data":{"LOG_LEVEL":"DEBUG"}}'

# Reload configuration (if supported by app)
kubectl exec -it backend-pod -- kill -HUP 1
```

## Prevention Strategies

### Monitoring and Alerting

```yaml
# Critical alerts for immediate attention
- alert: ServiceDown
  expr: up == 0
  for: 1m
  
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
  for: 5m

- alert: HighLatency
  expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
  for: 10m
```

### Health Checks

```python
# Comprehensive health check
from fastapi import FastAPI, HTTPException
import redis
import psycopg2

app = FastAPI()

@app.get("/health")
async def health_check():
    health = {"status": "healthy", "checks": {}}
    
    # Database check
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.close()
        health["checks"]["database"] = "healthy"
    except Exception as e:
        health["checks"]["database"] = f"unhealthy: {e}"
        health["status"] = "unhealthy"
    
    # Redis check
    try:
        r = redis.Redis.from_url(REDIS_URL)
        r.ping()
        health["checks"]["redis"] = "healthy"
    except Exception as e:
        health["checks"]["redis"] = f"unhealthy: {e}"
        health["status"] = "unhealthy"
    
    if health["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health)
    
    return health
```

### Chaos Engineering

```python
# Chaos testing script
import random
import requests
import time

def chaos_test():
    """Simulate various failure scenarios"""
    
    # Network delays
    time.sleep(random.uniform(0, 2))
    
    # Random failures
    if random.random() < 0.1:  # 10% failure rate
        raise Exception("Simulated failure")
    
    # Resource exhaustion
    if random.random() < 0.05:  # 5% chance
        # Consume memory
        big_list = [0] * 1000000
    
    return "success"
```

## Emergency Contacts

### Escalation Matrix

| Severity | Contact | Response Time |
|----------|---------|---------------|
| Critical | On-call engineer | 15 minutes |
| High | Team lead | 1 hour |
| Medium | Development team | 4 hours |
| Low | Next business day | 24 hours |

### Runbook Links

- [Service Recovery Procedures](./runbooks/service-recovery.md)
- [Database Maintenance](./runbooks/database-maintenance.md)
- [Security Incident Response](./runbooks/security-incident.md)
- [Performance Tuning](./runbooks/performance-tuning.md)

This troubleshooting guide covers the most common issues you'll encounter with AutoServe. For additional help, check the monitoring dashboards, logs, and reach out to the development team with specific error messages and symptoms.
