The purpose of this project was to test/practice different DevOps skills as well as cloud engineering skills.

# AutoServe Documentation

This directory contains comprehensive documentation for the AutoServe platform.

## Table of Contents

- [Architecture](./architecture.md) - System architecture and design patterns
- [Deployment Guide](./deployment-guide.md) - Step-by-step deployment instructions
- [API Reference](./api-reference.md) - Complete API documentation
- [Monitoring Guide](./monitoring-guide.md) - Observability and monitoring setup
- [ML Scaling](./ml-scaling.md) - Machine learning-based auto-scaling
- [Troubleshooting](./troubleshooting.md) - Common issues and solutions
- [Contributing](./contributing.md) - Development and contribution guidelines
- [Examples](./examples/) - Usage examples and tutorials

## Quick Start

1. [Prerequisites](./deployment-guide.md#prerequisites)
2. [Local Development](./deployment-guide.md#local-development)
3. [Kubernetes Deployment](./deployment-guide.md#kubernetes-deployment)
4. [Monitoring Setup](./monitoring-guide.md)

## Architecture Overview

AutoServe is a self-healing, auto-scaling microservices platform that demonstrates modern cloud-native technologies:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React SPA     │    │  FastAPI        │    │  Celery Worker  │
│   Frontend      │───▶│  Backend        │───▶│  Service        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  ML Controller  │
                    │  (Auto-scaling) │
                    └─────────────────┘
```

For detailed architecture information, see [Architecture Documentation](./architecture.md).



