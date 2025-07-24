# AutoServe Platform Setup Script for Windows 11
# This script will install all necessary dependencies and set up the AutoServe platform

Write-Host "🚀 AutoServe Platform Setup for Windows 11" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ This script requires Administrator privileges. Please run as Administrator." -ForegroundColor Red
    exit 1
}

# Function to check if command exists
function Test-Command($command) {
    try {
        Get-Command $command -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

# Function to install via winget if not already installed
function Install-IfNotExists($packageName, $wingetId, $command) {
    if (Test-Command $command) {
        Write-Host "✅ $packageName is already installed" -ForegroundColor Green
    } else {
        Write-Host "📦 Installing $packageName..." -ForegroundColor Yellow
        winget install $wingetId --accept-source-agreements --accept-package-agreements
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $packageName installed successfully" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to install $packageName" -ForegroundColor Red
        }
    }
}

Write-Host "`n🔧 Installing Core Dependencies..." -ForegroundColor Blue

# Install Git
Install-IfNotExists "Git" "Git.Git" "git"

# Install Docker Desktop
Install-IfNotExists "Docker Desktop" "Docker.DockerDesktop" "docker"

# Install kubectl
Install-IfNotExists "kubectl" "Kubernetes.kubectl" "kubectl"

# Install minikube
Install-IfNotExists "minikube" "Kubernetes.minikube" "minikube"

# Install Helm
Install-IfNotExists "Helm" "Helm.Helm" "helm"

# Install Terraform
Install-IfNotExists "Terraform" "HashiCorp.Terraform" "terraform"

# Install Node.js
Install-IfNotExists "Node.js" "OpenJS.NodeJS" "node"

# Install Python
Install-IfNotExists "Python" "Python.Python.3.11" "python"

Write-Host "`n🐍 Setting up Python Environment..." -ForegroundColor Blue

# Upgrade pip
python -m pip install --upgrade pip

# Install Python dependencies
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "`n📱 Setting up Frontend..." -ForegroundColor Blue

# Navigate to frontend directory and install dependencies
if (Test-Path "apps/frontend/package.json") {
    Set-Location "apps/frontend"
    Write-Host "📦 Installing Node.js dependencies..." -ForegroundColor Yellow
    npm install
    Set-Location "../.."
    Write-Host "✅ Frontend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "⚠️ Frontend package.json not found" -ForegroundColor Yellow
}

Write-Host "`n🔧 Configuring Development Environment..." -ForegroundColor Blue

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating .env file..." -ForegroundColor Yellow
    @"
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/autoserve
POSTGRES_DB=autoserve
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production

# ML Controller Configuration
PROMETHEUS_URL=http://localhost:9090
CONFIDENCE_THRESHOLD=0.7
SCALING_COOLDOWN=300

# Monitoring Configuration
GRAFANA_ADMIN_PASSWORD=admin
SLACK_WEBHOOK_URL=

# Application Configuration
LOG_LEVEL=INFO
ENVIRONMENT=development
"@ | Out-File -FilePath ".env" -Encoding utf8
    Write-Host "✅ .env file created" -ForegroundColor Green
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

Write-Host "`n🐳 Starting Docker Desktop..." -ForegroundColor Blue

# Check if Docker Desktop is running
$dockerStatus = docker version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "🚀 Starting Docker Desktop..." -ForegroundColor Yellow
    Start-Process "Docker Desktop" -WindowStyle Hidden
    Write-Host "⏳ Waiting for Docker to start..." -ForegroundColor Yellow
    
    # Wait for Docker to be ready
    $timeout = 60
    $elapsed = 0
    while ($elapsed -lt $timeout) {
        Start-Sleep 5
        $dockerStatus = docker version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Docker is running" -ForegroundColor Green
            break
        }
        $elapsed += 5
        Write-Host "⏳ Still waiting for Docker... ($elapsed/$timeout seconds)" -ForegroundColor Yellow
    }
    
    if ($elapsed -ge $timeout) {
        Write-Host "❌ Docker failed to start within $timeout seconds" -ForegroundColor Red
        Write-Host "Please start Docker Desktop manually and run this script again." -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "✅ Docker is already running" -ForegroundColor Green
}

Write-Host "`n🏗️ Building Docker Images..." -ForegroundColor Blue

# Build Docker images
$images = @(
    @{name="frontend"; path="apps/frontend"},
    @{name="backend"; path="apps/backend"},
    @{name="worker"; path="apps/worker"},
    @{name="ml-controller"; path="ml-controller"}
)

foreach ($image in $images) {
    Write-Host "🔨 Building $($image.name) image..." -ForegroundColor Yellow
    docker build -t "autoserve/$($image.name):latest" $image.path
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ $($image.name) image built successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to build $($image.name) image" -ForegroundColor Red
    }
}

Write-Host "`n🚀 Starting Services with Docker Compose..." -ForegroundColor Blue

# Start services
docker-compose up -d
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Services started successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to start services" -ForegroundColor Red
}

Write-Host "`n☸️ Setting up Kubernetes..." -ForegroundColor Blue

# Start minikube if not already running
$minikubeStatus = minikube status 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "🚀 Starting minikube..." -ForegroundColor Yellow
    minikube start --driver=docker --cpus=4 --memory=8192
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ minikube started successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to start minikube" -ForegroundColor Red
    }
} else {
    Write-Host "✅ minikube is already running" -ForegroundColor Green
}

# Add Helm repositories
Write-Host "📦 Adding Helm repositories..." -ForegroundColor Yellow
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
helm repo update

Write-Host "`n📊 Installing Monitoring Stack..." -ForegroundColor Blue

# Install Prometheus and Grafana
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
helm upgrade --install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring --wait
helm upgrade --install jaeger jaegertracing/jaeger --namespace monitoring --wait

Write-Host "`n🎯 Final Setup Steps..." -ForegroundColor Blue

# Create initial database schema
Write-Host "🗄️ Setting up database..." -ForegroundColor Yellow
# The database will be initialized by the backend service

Write-Host "`n🎉 Setup Complete!" -ForegroundColor Green
Write-Host "==================" -ForegroundColor Green

Write-Host "`n📋 Service URLs:" -ForegroundColor Cyan
Write-Host "🌐 Frontend:        http://localhost:3000" -ForegroundColor White
Write-Host "🔧 Backend API:     http://localhost:8000" -ForegroundColor White
Write-Host "📊 Grafana:         http://localhost:3001 (admin/admin)" -ForegroundColor White
Write-Host "🔍 Prometheus:      http://localhost:9090" -ForegroundColor White
Write-Host "📈 Jaeger:          http://localhost:16686" -ForegroundColor White
Write-Host "💾 MinIO:           http://localhost:9001 (minioadmin/minioadmin)" -ForegroundColor White

Write-Host "`n🚀 Quick Start Commands:" -ForegroundColor Cyan
Write-Host "# View running services:" -ForegroundColor Gray
Write-Host "docker-compose ps" -ForegroundColor White
Write-Host "`n# View logs:" -ForegroundColor Gray
Write-Host "docker-compose logs -f [service-name]" -ForegroundColor White
Write-Host "`n# Access Kubernetes cluster:" -ForegroundColor Gray
Write-Host "kubectl get pods -n autoserve" -ForegroundColor White
Write-Host "`n# Deploy to Kubernetes:" -ForegroundColor Gray
Write-Host "kubectl apply -k k8s/overlays/development/" -ForegroundColor White

Write-Host "`n📖 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Open http://localhost:3000 to access the AutoServe dashboard" -ForegroundColor White
Write-Host "2. Check http://localhost:8000/docs for API documentation" -ForegroundColor White
Write-Host "3. Monitor services at http://localhost:3001 (Grafana)" -ForegroundColor White
Write-Host "4. Run load tests: python scripts/traffic-generator.py" -ForegroundColor White
Write-Host "5. View the README.md for detailed documentation" -ForegroundColor White

Write-Host "`n🔧 Troubleshooting:" -ForegroundColor Cyan
Write-Host "If you encounter issues:" -ForegroundColor White
Write-Host "- Check Docker Desktop is running: docker --version" -ForegroundColor Gray
Write-Host "- Restart services: docker-compose down && docker-compose up -d" -ForegroundColor Gray
Write-Host "- Check logs: docker-compose logs [service-name]" -ForegroundColor Gray
Write-Host "- Reset minikube: minikube delete && minikube start" -ForegroundColor Gray

Write-Host "`n✨ Happy coding with AutoServe! ✨" -ForegroundColor Magenta
