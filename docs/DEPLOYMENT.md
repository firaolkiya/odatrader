# OdaTrade Cloud Deployment Guide

## Architecture

```
                    ┌─────────────┐
                    │  Dashboard  │ (Streamlit)
                    └──────┬──────┘
                           │ HTTP/WS
                    ┌──────▼──────┐
                    │  FastAPI    │ ← JWT Auth, WebSocket Hub
                    │  API (x2)   │
                    └──────┬──────┘
              ┌────────────┼────────────┐
              │            │            │
       ┌──────▼──┐  ┌─────▼────┐  ┌───▼────┐
       │  Redis  │  │ Postgres │  │  Bots  │
       │ EventBus│  │   Pool   │  │ (x N)  │
       └─────────┘  └──────────┘  └────────┘
```

## Local Development

```bash
docker compose up -d
# API: http://localhost:8000
# Dashboard: http://localhost:8501
# Redis: localhost:6379
# Postgres: localhost:5432
```

## AWS (ECS Fargate)

1. `cd deploy/aws/terraform && terraform apply`
2. Push images to ECR
3. Deploy ECS task from `deploy/aws/ecs-task-definition.json`

Services: ECS Fargate (API + Bot), RDS PostgreSQL, ElastiCache Redis

## DigitalOcean

```bash
doctl apps create --spec deploy/digitalocean/app.yaml
```

## GCP (Cloud Run)

```bash
gcloud run services replace deploy/gcp/cloud-run.yaml
```

## Kubernetes

```bash
kubectl apply -f deploy/kubernetes/namespace.yaml
kubectl apply -f deploy/kubernetes/redis-postgres.yaml
kubectl apply -f deploy/kubernetes/api-deployment.yaml
kubectl apply -f deploy/kubernetes/bot-deployment.yaml
```

## Multi-Bot Deployment

Each bot runs as an isolated worker with its own:
- Event pipeline (market data → strategy → risk → orders → PnL)
- Redis state namespace (`odatrade:bot:{id}:*`)
- Config (strategy, risk profile, symbols)

Create bots via API:
```bash
curl -X POST http://localhost:8000/bots/ \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "BTC Scalper", "symbols": ["btcusdt"], "risk_profile": "moderate"}'
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection | sqlite fallback |
| REDIS_URL | Redis connection | redis://localhost:6379/0 |
| EVENT_BACKEND | redis, kafka, or nats | redis |
| JWT_SECRET | API auth secret | change-me |
