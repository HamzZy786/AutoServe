# AutoServe Helm values template
nameOverride: ""
fullnameOverride: ""

frontend:
  replicaCount: ${replica_count.frontend}
  image:
    repository: autoserve/frontend
    tag: "${image_tag}"
  resources:
    requests:
      cpu: ${resources.frontend.requests.cpu}
      memory: ${resources.frontend.requests.memory}
    limits:
      cpu: ${resources.frontend.limits.cpu}
      memory: ${resources.frontend.limits.memory}

backend:
  replicaCount: ${replica_count.backend}
  image:
    repository: autoserve/backend
    tag: "${image_tag}"
  resources:
    requests:
      cpu: ${resources.backend.requests.cpu}
      memory: ${resources.backend.requests.memory}
    limits:
      cpu: ${resources.backend.limits.cpu}
      memory: ${resources.backend.limits.memory}
  env:
    DATABASE_URL: "postgresql://postgres:password@postgres:5432/autoserve_${environment}"
    REDIS_URL: "redis://redis:6379/0"
    SECRET_KEY: "your-secret-key-${environment}"

worker:
  replicaCount: ${replica_count.worker}
  image:
    repository: autoserve/worker
    tag: "${image_tag}"
  resources:
    requests:
      cpu: ${resources.worker.requests.cpu}
      memory: ${resources.worker.requests.memory}
    limits:
      cpu: ${resources.worker.limits.cpu}
      memory: ${resources.worker.limits.memory}

mlController:
  replicaCount: ${replica_count.ml_controller}
  image:
    repository: autoserve/ml-controller
    tag: "${image_tag}"
  resources:
    requests:
      cpu: ${resources.ml_controller.requests.cpu}
      memory: ${resources.ml_controller.requests.memory}
    limits:
      cpu: ${resources.ml_controller.limits.cpu}
      memory: ${resources.ml_controller.limits.memory}

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
  hosts:
    - host: ${domain}
      paths:
        - path: /
          pathType: Prefix
          service: frontend
        - path: /api
          pathType: Prefix
          service: backend
        - path: /ml
          pathType: Prefix
          service: mlController
  tls:
    - secretName: autoserve-tls
      hosts:
        - ${domain}

monitoring:
  enabled: true

postgres:
  enabled: true
  env:
    POSTGRES_DB: "autoserve_${environment}"

redis:
  enabled: true
