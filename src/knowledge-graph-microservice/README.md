# Knowledge Graph Microservice

This service accepts a PDF file, extracts its text, and returns a simple knowledge graph suitable for visualization in the frontend (e.g., with Recharts).

## Running

```bash
uvicorn src.main:app --reload
```

## Endpoint
- `/knowledge-graph/` (POST, accepts PDF file upload, returns nodes and links)

