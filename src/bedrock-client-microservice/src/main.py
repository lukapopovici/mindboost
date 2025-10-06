from fastapi import FastAPI, UploadFile, File, Request
import requests
import os
import json

app = FastAPI()

PDF_PARSER_URL = os.getenv("PDF_PARSER_URL", "http://localhost:8002/parse-pdf/")
BEDROCK_MONITOR_URL = os.getenv("BEDROCK_MONITOR_URL", "http://localhost:8502/log")
INTEREST_MONITOR_URL = os.getenv("INTEREST_MONITOR_URL", "http://localhost:8020/interest")

# Bedrock config
BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-1")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "your-bedrock-model-id")

def call_bedrock_for_quiz_and_topics(text: str):
    import boto3

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

    client = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)

    body = json.dumps({"input": prompt})
    resp = client.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=body
    )

    raw = resp.get("body")
    if hasattr(raw, "read"):
        raw = raw.read()
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8")

    payload = json.loads(raw)  # must contain {"quiz": [...], "topics": [...]}
    quiz = payload["quiz"]
    topics = payload["topics"]

    cost = float(resp.get("cost", 0.0))
    return quiz, topics, cost

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

    # Bedrock: quiz + topics
    try:
        quiz, topics, bedrock_cost = call_bedrock_for_quiz_and_topics(text)
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
