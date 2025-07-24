# Kubernetes Manifests

This directory contains all Kubernetes YAML manifests for deploying the AutoServe platform.

## Structure

```
k8s/
├── base/                          # Base Kustomize resources
│   ├── kustomization.yaml        # Base kustomization
│   ├── namespace.yaml            # Namespace definition
│   ├── configmaps/               # Configuration maps
│   ├── deployments/              # Application deployments
│   ├── services/                 # Service definitions
│   ├── ingress/                  # Ingress resources
│   └── monitoring/               # Monitoring stack
├── overlays/                     # Environment-specific configurations
│   ├── development/              # Development environment
│   ├── staging/                  # Staging environment
│   └── production/               # Production environment
└── components/                   # Reusable components
    ├── hpa/                      # Horizontal Pod Autoscalers
    ├── pdb/                      # Pod Disruption Budgets
    └── rbac/                     # RBAC resources
```

## Deployment

### Development Environment
```bash
kubectl apply -k k8s/overlays/development/
```

### Staging Environment
```bash
kubectl apply -k k8s/overlays/staging/
```

### Production Environment
```bash
kubectl apply -k k8s/overlays/production/
```

## Features

- ✅ **Kustomize**: Environment-specific configurations
- ✅ **Probes**: Liveness, readiness, and startup probes
- ✅ **HPA**: Horizontal Pod Autoscaling
- ✅ **PDB**: Pod Disruption Budgets for availability
- ✅ **RBAC**: Role-based access control
- ✅ **NetworkPolicy**: Network security policies
- ✅ **Resources**: CPU and memory limits/requests
- ✅ **Monitoring**: ServiceMonitor for Prometheus

## Services

- **Frontend**: React application with NGINX
- **Backend**: FastAPI application
- **Worker**: Celery background workers
- **ML Controller**: ML-based scaling controller
- **Database**: PostgreSQL with persistent storage
- **Cache**: Redis for caching and message broker
- **Monitoring**: Prometheus, Grafana, Jaeger stack
