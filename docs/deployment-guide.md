# Deployment Guide

This guide provides step-by-step instructions for deploying AutoServe in various environments.

## Prerequisites

### Local Development
- Windows 11 (or WSL2)
- Docker Desktop
- kubectl
- Helm 3.x
- PowerShell 7+ (for setup script)

### Cloud Deployment
- Kubernetes cluster (EKS, GKE, AKS, or self-managed)
- kubectl configured for your cluster
- Helm 3.x
- Terraform (for infrastructure)

## Quick Start

### 1. Automated Setup (Windows)

Run the automated setup script to install all dependencies:

```powershell
# Clone the repository
git clone https://github.com/yourusername/AutoServe.git
cd AutoServe

# Run setup script (requires admin privileges)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\setup.ps1
```

This script will:
- Install Docker Desktop
- Install kubectl
- Install Helm
- Install Terraform
- Enable required Windows features
- Set up development environment

### 2. Manual Setup

If you prefer manual installation:

#### Install Docker Desktop
1. Download from [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Install and enable WSL2 integration
3. Start Docker Desktop

#### Install kubectl
```powershell
# Using Chocolatey
choco install kubernetes-cli

# Or using winget
winget install Kubernetes.kubectl
```

#### Install Helm
```powershell
# Using Chocolatey
choco install kubernetes-helm

# Or download from releases
# https://github.com/helm/helm/releases
```

#### Install Terraform
```powershell
# Using Chocolatey
choco install terraform

# Or using winget
winget install HashiCorp.Terraform
```

## Local Development

### 1. Start Local Environment

```powershell
# Start all services with Docker Compose
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 2. Access Services

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Jaeger**: http://localhost:16686

### 3. Development Workflow

```powershell
# Make changes to code
# Rebuild specific service
docker-compose build backend
docker-compose up -d backend

# Or rebuild all services
docker-compose build
docker-compose up -d
```

### 4. Database Operations

```powershell
# Initialize database
docker-compose exec backend python scripts/database/migrate.py

# Connect to database
docker-compose exec postgres psql -U autoserve -d autoserve

# Backup database
docker-compose exec postgres pg_dump -U autoserve autoserve > backup.sql
```

## Kubernetes Deployment

### 1. Prepare Kubernetes Cluster

#### Using minikube (Local)
```powershell
# Install minikube
choco install minikube

# Start cluster
minikube start --memory=8192 --cpus=4 --driver=docker

# Enable addons
minikube addons enable ingress
minikube addons enable metrics-server
```

#### Using Docker Desktop Kubernetes
```powershell
# Enable Kubernetes in Docker Desktop settings
# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
```

### 2. Deploy with Kustomize

#### Development Environment
```powershell
# Apply base resources
kubectl apply -k k8s/base

# Apply development overlay
kubectl apply -k k8s/overlays/dev

# Check deployment status
kubectl get pods -n autoserve-dev
kubectl get services -n autoserve-dev
```

#### Staging Environment
```powershell
# Apply staging overlay
kubectl apply -k k8s/overlays/staging

# Check status
kubectl get pods -n autoserve-staging
```

#### Production Environment
```powershell
# Apply production overlay
kubectl apply -k k8s/overlays/prod

# Check status
kubectl get pods -n autoserve-prod
```

### 3. Deploy with Helm

#### Add Helm Repository (if publishing to registry)
```powershell
# Add your Helm repository
helm repo add autoserve https://your-helm-repo.com
helm repo update
```

#### Install Chart
```powershell
# Development
helm install autoserve-dev ./helm/autoserve -n autoserve-dev --create-namespace -f helm/autoserve/values-dev.yaml

# Staging
helm install autoserve-staging ./helm/autoserve -n autoserve-staging --create-namespace -f helm/autoserve/values-staging.yaml

# Production
helm install autoserve-prod ./helm/autoserve -n autoserve-prod --create-namespace -f helm/autoserve/values-prod.yaml
```

#### Upgrade Deployment
```powershell
# Upgrade with new values
helm upgrade autoserve-prod ./helm/autoserve -n autoserve-prod -f helm/autoserve/values-prod.yaml

# Rollback if needed
helm rollback autoserve-prod 1 -n autoserve-prod
```

### 4. Configure Ingress

#### Update DNS (Local)
Add to `C:\Windows\System32\drivers\etc\hosts`:
```
127.0.0.1 autoserve.local
127.0.0.1 api.autoserve.local
127.0.0.1 grafana.autoserve.local
```

#### Access Services
- **Frontend**: http://autoserve.local
- **API**: http://api.autoserve.local
- **Grafana**: http://grafana.autoserve.local

## Cloud Deployment

### 1. Infrastructure with Terraform

#### Azure (AKS)
```powershell
cd terraform

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var="environment=prod" -var="cluster_name=autoserve-prod"

# Apply infrastructure
terraform apply -var="environment=prod" -var="cluster_name=autoserve-prod"

# Get kubeconfig
az aks get-credentials --resource-group autoserve-prod --name autoserve-prod-aks
```

#### AWS (EKS)
```powershell
# Configure AWS CLI
aws configure

# Initialize and apply Terraform
cd terraform
terraform init
terraform plan -var="cloud_provider=aws" -var="environment=prod"
terraform apply
```

#### Google Cloud (GKE)
```powershell
# Authenticate with Google Cloud
gcloud auth login
gcloud config set project your-project-id

# Initialize and apply Terraform
cd terraform
terraform init
terraform plan -var="cloud_provider=gcp" -var="environment=prod"
terraform apply
```

### 2. Deploy Application

After infrastructure is ready:

```powershell
# Update kubeconfig
kubectl config current-context

# Deploy monitoring stack first
kubectl apply -k k8s/monitoring

# Deploy application
helm install autoserve-prod ./helm/autoserve -n autoserve-prod --create-namespace -f helm/autoserve/values-prod.yaml

# Configure DNS
# Update your DNS provider to point to the ingress controller IP
kubectl get service -n ingress-nginx ingress-nginx-controller
```

## GitOps Deployment with ArgoCD

### 1. Install ArgoCD

```powershell
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Get admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Port forward to access UI
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

### 2. Configure Applications

```powershell
# Apply ArgoCD project and applications
kubectl apply -f argocd/

# Sync applications via CLI
argocd app sync autoserve-dev
argocd app sync autoserve-staging
argocd app sync autoserve-prod
```

### 3. Access ArgoCD UI

- **URL**: https://localhost:8080
- **Username**: admin
- **Password**: (from secret above)

## Monitoring Setup

### 1. Deploy Monitoring Stack

```powershell
# Deploy Prometheus, Grafana, and other monitoring tools
kubectl apply -k k8s/monitoring

# Check monitoring pods
kubectl get pods -n monitoring
```

### 2. Access Monitoring Tools

```powershell
# Port forward to Grafana
kubectl port-forward svc/grafana -n monitoring 3000:80

# Port forward to Prometheus
kubectl port-forward svc/prometheus -n monitoring 9090:9090

# Port forward to Jaeger
kubectl port-forward svc/jaeger -n monitoring 16686:16686
```

### 3. Import Dashboards

Grafana dashboards are automatically imported from `monitoring/grafana/dashboards/`.

## Verification and Testing

### 1. Health Checks

```powershell
# Check all pods are running
kubectl get pods -n autoserve-prod

# Check services
kubectl get services -n autoserve-prod

# Check ingress
kubectl get ingress -n autoserve-prod
```

### 2. Functional Testing

```powershell
# Test API endpoints
curl http://api.autoserve.local/health
curl http://api.autoserve.local/metrics

# Generate test traffic
python scripts/traffic-generator.py --target http://api.autoserve.local --duration 60
```

### 3. Scaling Testing

```powershell
# Test horizontal pod autoscaler
kubectl get hpa -n autoserve-prod

# Generate load to trigger scaling
python scripts/traffic-generator.py --target http://api.autoserve.local --concurrent 50 --duration 300

# Watch scaling events
kubectl get events -n autoserve-prod --sort-by='.lastTimestamp'
```

## Troubleshooting

### Common Issues

#### 1. Pods not starting
```powershell
# Check pod logs
kubectl logs -f deployment/backend -n autoserve-prod

# Describe pod for events
kubectl describe pod <pod-name> -n autoserve-prod

# Check resource limits
kubectl top pods -n autoserve-prod
```

#### 2. Service connectivity issues
```powershell
# Test service resolution
kubectl exec -it <pod-name> -n autoserve-prod -- nslookup backend

# Test port connectivity
kubectl exec -it <pod-name> -n autoserve-prod -- telnet backend 8000
```

#### 3. Ingress not working
```powershell
# Check ingress controller
kubectl get pods -n ingress-nginx

# Check ingress events
kubectl describe ingress autoserve-ingress -n autoserve-prod

# Verify DNS resolution
nslookup autoserve.local
```

### Cleanup

#### Remove Application
```powershell
# Using Helm
helm uninstall autoserve-prod -n autoserve-prod

# Using Kustomize
kubectl delete -k k8s/overlays/prod
```

#### Remove Infrastructure
```powershell
# Using Terraform
cd terraform
terraform destroy
```

## Security Considerations

### 1. Secrets Management

```powershell
# Create secrets for production
kubectl create secret generic autoserve-secrets \
  --from-literal=postgres-password=your-secure-password \
  --from-literal=redis-password=your-redis-password \
  --from-literal=jwt-secret=your-jwt-secret \
  -n autoserve-prod
```

### 2. Network Policies

Network policies are included in the Kubernetes manifests to restrict pod-to-pod communication.

### 3. RBAC

Role-based access control is configured for service accounts and user access.

### 4. TLS/SSL

Configure TLS certificates for production:

```powershell
# Install cert-manager for automatic certificate management
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

## Performance Tuning

### 1. Resource Optimization

Review and adjust resource requests/limits in values files:
- CPU: Start with 100m requests, 500m limits
- Memory: Start with 128Mi requests, 512Mi limits

### 2. Autoscaling Configuration

Tune HPA settings based on your traffic patterns:
- Target CPU: 70%
- Target Memory: 80%
- Min replicas: 2
- Max replicas: 10

### 3. Database Performance

- Configure connection pooling
- Set up read replicas for read-heavy workloads
- Implement proper indexing strategy

This deployment guide should get you started with AutoServe in any environment. For additional help, see the [Troubleshooting Guide](./troubleshooting.md).
