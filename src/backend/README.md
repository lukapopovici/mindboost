# Backend (API Gateway) Microservice


This service acts as the API gateway, routing requests to the PDF Parser, Bedrock Client, and Knowledge Graph microservices.

## Running

```bash
uvicorn src.main:app --reload
```

## Endpoints
- `/parse-pdf/` (proxies to PDF Parser microservice)
- `/invoke-bedrock/` (proxies to Bedrock Client microservice)
- `/knowledge-graph/` (proxies to Knowledge Graph microservice)
