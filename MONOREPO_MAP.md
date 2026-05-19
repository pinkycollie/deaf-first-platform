# MBTQ.dev Monorepo Map

This repository contains multiple subsystems. Each subsystem is isolated by boundaries.

## 1. Backend Services (Python)
- app/ (Flask)
- fastapi_backend/
- magician_api/
- database/

## 2. Frontend / Static
- static/
- templates/
- docs/
- GitHub Pages demo

## 3. AI / Quantum
- magician_api/ai
- magician_api/quantum
- app/core/quantum

## 4. Integrations
- app/integrations/
- fastapi_backend/api/v1/integration_endpoints.py

## 5. Infrastructure
- deployment/docker/
- deployment/kubernetes/
- deployment/terraform/
- deployment/ansible/

## 6. Tests
- tests/unit
- tests/integration
- tests/e2e
- tests/accessibility
- tests/performance

## 7. Scripts
- scripts/setup
- scripts/deployment
- scripts/data
- scripts/maintenance
- scripts/monitoring
