from fastapi import FastAPI, UploadFile, File
import requests
import os

app = FastAPI()

PDF_PARSER_URL = os.getenv("PDF_PARSER_URL", "http://pdf-parser-microservice:8001/parse-pdf/")
BEDROCK_CLIENT_URL = os.getenv("BEDROCK_CLIENT_URL", "http://bedrock-client-microservice:8002/invoke-bedrock/")
APIKEY_PATH = os.path.join(os.path.dirname(__file__), "bedrock_apikey.txt")

def read_apikey():
    try:
        with open(APIKEY_PATH, "r") as f:
            for line in f:
                if line.startswith("BEDROCK_API_KEY="):
                    return line.strip().split("=", 1)[1]
    except Exception:
        return None
    return None

@app.post("/knowledge-graph/")
async def knowledge_graph(file: UploadFile = File(...)):
    files = {"file": (file.filename, await file.read(), file.content_type)}
    pdf_resp = requests.post(PDF_PARSER_URL, files=files, timeout=30)
    if pdf_resp.status_code != 200:
        return {"error": "PDF parsing failed", "details": pdf_resp.text}
    text = pdf_resp.json().get("text", "")
    if not text:
        return {"error": "Parsed PDF contained no text"}

    apikey = read_apikey()
    if not apikey:
        return {"error": "Bedrock API key not found in bedrock_apikey.txt"}

    import boto3
    import botocore
    import json as _json
    session = boto3.Session(
        aws_access_key_id=apikey,
        aws_secret_access_key="dummy-secret-key",
        region_name="us-east-1"
    )
    client = session.client("bedrock-runtime")
    prompt = (
        "You are an assistant that outputs only strict JSON.\n"
        "Given the following document text, produce a knowledge graph as a JSON object with two keys:\n"
        "1) 'nodes': a list of nodes, each: {id: str, label: str}\n"
        "2) 'links': a list of links, each: {source: str, target: str}\n"
        "Return valid JSON only with keys 'nodes' and 'links'. No extra commentary.\n\n"
        f"Document text:\n{text}"
    )
    body = _json.dumps({"input": prompt})
    try:
        resp = client.invoke_model(
            modelId="your-bedrock-model-id",
            contentType="application/json",
            accept="application/json",
            body=body
        )
        raw = resp.get("body")
        if hasattr(raw, "read"):
            raw = raw.read()
        if isinstance(raw, (bytes, bytearray)):
            raw = raw.decode("utf-8")
        result = _json.loads(raw)
        return result
    except botocore.exceptions.BotoCoreError as e:
        return {"error": f"Bedrock boto3 error: {e}"}
    except Exception as e:
        return {"error": f"Bedrock call failed: {e}"}
