# Bedrock Client Microservice

This service handles communication with Amazon Bedrock.

## Running

```bash
uvicorn src.main:app --reload
```

## Endpoint
- `/invoke-bedrock/` (POST, accepts JSON payload)
