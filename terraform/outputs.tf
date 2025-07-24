output "nginx_ingress_ip" {
  description = "External IP of NGINX Ingress Controller"
  value       = helm_release.nginx_ingress.status[0].load_balancer[0].ingress[0].ip
}

output "autoserve_namespace" {
  description = "Kubernetes namespace for AutoServe"
  value       = var.namespace
}

output "autoserve_domain" {
  description = "Domain for AutoServe application"
  value       = var.domain
}

output "prometheus_url" {
  description = "Prometheus URL"
  value       = var.enable_monitoring ? "http://prometheus.monitoring.svc.cluster.local:9090" : null
}

output "grafana_url" {
  description = "Grafana URL"
  value       = var.enable_monitoring ? "http://grafana.monitoring.svc.cluster.local:3000" : null
}

output "argocd_url" {
  description = "ArgoCD URL"
  value       = var.enable_argocd ? "https://argocd.${var.domain}" : null
}

output "autoserve_urls" {
  description = "AutoServe application URLs"
  value = {
    frontend      = "https://${var.domain}"
    backend_api   = "https://api.${var.domain}"
    ml_controller = "https://ml.${var.domain}"
  }
}
