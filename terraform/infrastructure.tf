# Install NGINX Ingress Controller
resource "helm_release" "nginx_ingress" {
  name       = "nginx-ingress"
  repository = "https://kubernetes.github.io/ingress-nginx"
  chart      = "ingress-nginx"
  namespace  = "ingress-nginx"
  version    = "4.7.1"

  create_namespace = true

  set {
    name  = "controller.replicaCount"
    value = "2"
  }

  set {
    name  = "controller.metrics.enabled"
    value = "true"
  }

  set {
    name  = "controller.metrics.serviceMonitor.enabled"
    value = var.enable_monitoring
  }
}

# Install cert-manager for TLS certificates
resource "helm_release" "cert_manager" {
  name       = "cert-manager"
  repository = "https://charts.jetstack.io"
  chart      = "cert-manager"
  namespace  = "cert-manager"
  version    = "v1.13.0"

  create_namespace = true

  set {
    name  = "installCRDs"
    value = "true"
  }

  set {
    name  = "prometheus.enabled"
    value = var.enable_monitoring
  }
}

# Install Prometheus Operator if monitoring is enabled
resource "helm_release" "prometheus_operator" {
  count = var.enable_monitoring ? 1 : 0

  name       = "prometheus-operator"
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "kube-prometheus-stack"
  namespace  = "monitoring"
  version    = "51.2.0"

  create_namespace = true

  values = [
    file("${path.module}/values/prometheus-operator.yaml")
  ]

  set {
    name  = "grafana.adminPassword"
    value = "admin123"
  }

  set {
    name  = "prometheus.prometheusSpec.retention"
    value = "30d"
  }
}

# Install ArgoCD if enabled
resource "helm_release" "argocd" {
  count = var.enable_argocd ? 1 : 0

  name       = "argocd"
  repository = "https://argoproj.github.io/argo-helm"
  chart      = "argo-cd"
  namespace  = "argocd"
  version    = "5.46.7"

  create_namespace = true

  values = [
    file("${path.module}/values/argocd.yaml")
  ]

  depends_on = [helm_release.nginx_ingress]
}

# Deploy AutoServe application using Helm
resource "helm_release" "autoserve" {
  name      = "autoserve"
  chart     = "../helm/autoserve"
  namespace = var.namespace
  version   = "0.1.0"

  create_namespace = true

  values = [
    templatefile("${path.module}/values/autoserve.yaml.tpl", {
      environment   = var.environment
      domain        = var.domain
      image_tag     = var.image_tag
      replica_count = var.replica_count
      resources     = var.resources
    })
  ]

  depends_on = [
    helm_release.nginx_ingress,
    helm_release.cert_manager
  ]
}

# Create monitoring ServiceMonitors for AutoServe components
resource "kubectl_manifest" "autoserve_servicemonitors" {
  count = var.enable_monitoring ? 4 : 0

  yaml_body = templatefile("${path.module}/manifests/servicemonitor.yaml.tpl", {
    name      = local.services[count.index].name
    namespace = var.namespace
    port      = local.services[count.index].port
    selector  = local.services[count.index].selector
  })

  depends_on = [
    helm_release.prometheus_operator,
    helm_release.autoserve
  ]
}

locals {
  services = [
    {
      name     = "backend"
      port     = "metrics"
      selector = { app = "backend" }
    },
    {
      name     = "worker"
      port     = "metrics"
      selector = { app = "worker" }
    },
    {
      name     = "ml-controller"
      port     = "metrics"
      selector = { app = "ml-controller" }
    },
    {
      name     = "nginx-ingress"
      port     = "metrics"
      selector = { "app.kubernetes.io/name" = "ingress-nginx" }
    }
  ]
}
