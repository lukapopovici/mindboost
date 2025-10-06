from fastapi import FastAPI, UploadFile, File, Request
import requests
import os
import json

app = FastAPI()

PDF_PARSER_URL = os.getenv("PDF_PARSER_URL", "http://localhost:8002/parse-pdf/")
BEDROCK_MONITOR_URL = os.getenv("BEDROCK_MONITOR_URL", "http://localhost:8502/log")
INTEREST_MONITOR_URL = os.getenv("INTEREST_MONITOR_URL", "http://localhost:8020/interest")
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

def call_bedrock_for_quiz_and_topics(text: str, apikey: str = None):
    # Use boto3 for Bedrock LLM calls, passing API key if possible (mock: use as AWS_ACCESS_KEY_ID)
    import boto3
    import botocore
    import base64
    import tempfile

    # If apikey is provided, set it as AWS_ACCESS_KEY_ID (mock)
    # In real AWS, you would use AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
    # Here, we use apikey as AWS_ACCESS_KEY_ID and a dummy secret
    session = boto3.Session(
        aws_access_key_id=apikey if apikey else "dummy-access-key",
        aws_secret_access_key="dummy-secret-key",
        region_name="us-east-1"
    )
    client = session.client("bedrock-runtime")

    prompt = (
        "You are an assistant that outputs only strict JSON.\n"
        "Given the following document text, produce an object with two keys:\n"
        "1) 'quiz': A list of EXACTLY 5 multiple-choice questions (MCQ). "
        "   Each item must be: "
        "{\"question\": str, \"options\": [str, str, str, str], \"correct_answer\": str}\n"
        "2) 'topics': A list of EXACTLY 5 items capturing the main topics of the paper, each: "
        "{\"topic\": str, \"relevance\": float, \"summary\": str, \"key_terms\": [str, ...]}\n"
        "Return valid JSON only with keys 'quiz' and 'topics'. No extra commentary.\n\n"
        f"Document text:\n{text}"
    )
    body = json.dumps({"input": prompt})
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
        payload = json.loads(raw)
        quiz = payload.get("quiz", [])
        topics = payload.get("topics", [])
        cost = float(resp.get("cost", 0.0))
        return quiz, topics, cost
    except botocore.exceptions.BotoCoreError as e:
        raise Exception(f"Bedrock boto3 error: {e}")
    except Exception as e:
        raise Exception(f"Bedrock call failed: {e}")


@app.post("/quiz-from-pdf/")
async def quiz_from_pdf(request: Request, file: UploadFile = File(...)):
    user = request.headers.get("X-User", "anonymous")

    # Parse PDF
    files = {"file": (file.filename, await file.read(), file.content_type)}
    r = requests.post(PDF_PARSER_URL, files=files, timeout=30)
    if r.status_code != 200:
        return {"error": "PDF parsing failed", "details": r.text}
    text = r.json().get("text", "")

    if not text:
        return {"error": "Parsed PDF contained no text"}

    # Read API key from file
    apikey = read_apikey()
    if not apikey:
        return {"error": "Bedrock API key not found in bedrock_apikey.txt"}

    # Bedrock: quiz + topics
    try:
        quiz, topics, bedrock_cost = call_bedrock_for_quiz_and_topics(text, apikey=apikey)
    except Exception as e:
        return {"error": "Bedrock call failed", "details": str(e)}

    # Log to Bedrock Monitor
    try:
        requests.post(
            BEDROCK_MONITOR_URL,
            json={"user": user, "request": text, "response": {"quiz": quiz, "topics": topics}, "cost": bedrock_cost},
            timeout=5
        )
    except Exception as e:
        print(f"Bedrock Monitor logging failed: {e}")

    # Forward topics to Interest Monitor
    interest_payload = {
        "user": user,
        "label": "interest",
        "topics": topics,
        "source": file.filename
    }
    try:
        ir = requests.post(INTEREST_MONITOR_URL, json=interest_payload, timeout=5)
        if ir.status_code >= 300:
            print(f"Interest Monitor returned {ir.status_code}: {ir.text}")
    except Exception as e:
        print(f"Failed to forward interests to Interest Monitor: {e}")

    # Return to client
    return {"quiz": quiz, "topics": topics, "source_text": text, "cost": bedrock_cost}
