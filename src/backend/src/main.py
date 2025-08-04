from fastapi import FastAPI, UploadFile, File, Request
import httpx

app = FastAPI()

PDF_PARSER_URL = "http://localhost:8001/parse-pdf/"
BEDROCK_CLIENT_URL = "http://localhost:8002/invoke-bedrock/"

@app.post("/parse-pdf/")
async def proxy_parse_pdf(file: UploadFile = File(...)):
    async with httpx.AsyncClient() as client:
        files = {'file': (file.filename, await file.read(), file.content_type)}
        response = await client.post(PDF_PARSER_URL, files=files)
        return response.json()

@app.post("/invoke-bedrock/")
async def proxy_invoke_bedrock(request: Request):
    data = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(BEDROCK_CLIENT_URL, json=data)
        return response.json()
