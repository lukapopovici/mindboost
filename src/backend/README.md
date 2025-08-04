# Backend (API Gateway) Microservice

This service acts as the API gateway, routing requests to the PDF Parser and Bedrock Client microservices.

## Running

```bash
uvicorn src.main:app --reload
```

## Endpoints
- `/parse-pdf/` (proxies to PDF Parser microservice)
- `/invoke-bedrock/` (proxies to Bedrock Client microservice)
