# PDF Parser Microservice

This service parses PDF files and extracts their text content.

## Running

```bash
uvicorn src.main:app --reload
```

## Endpoint
- `/parse-pdf/` (POST, accepts PDF file upload)
