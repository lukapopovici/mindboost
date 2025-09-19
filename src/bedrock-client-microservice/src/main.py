from fastapi import FastAPI, UploadFile, File
import requests
import boto3
import os

app = FastAPI()

# PDF Parser microservice URL
PDF_PARSER_URL = os.getenv("PDF_PARSER_URL", "http://localhost:8002/parse-pdf/")

@app.post("/quiz-from-pdf/")
async def quiz_from_pdf(file: UploadFile = File(...)):
    # Send PDF to PDF Parser microservice
    files = {"file": (file.filename, await file.read(), file.content_type)}
    response = requests.post(PDF_PARSER_URL, files=files)
    if response.status_code != 200:
        return {"error": "PDF parsing failed", "details": response.text}
    text = response.json().get("text", "")

    # Example: Amazon Bedrock call (uncomment and configure for real use)
    # import boto3
    # bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
    # prompt = f"Generate a quiz from the following text:\n{text}"
    # response = bedrock_client.invoke_model(
    #     modelId='your-bedrock-model-id',
    #     contentType='application/json',
    #     accept='application/json',
    #     body=json.dumps({"input": prompt})
    # )
    # quiz = json.loads(response['body'])

    # Simulate a quiz response in JSON format
    quiz = [
        {
            "question": "What is the main topic of the document?",
            "options": ["Math", "Science", "History", "Literature"],
            "correct_answer": "Science"
        },
        {
            "question": "How many pages does the document have?",
            "options": ["1", "2", "5", "10"],
            "correct_answer": str(text.count('\n') // 30 + 1)  # crude estimate
        },
        {
            "question": "Which keyword appears most?",
            "options": ["data", "analysis", "experiment", "result"],
            "correct_answer": "data"
        }
    ]
    return {"quiz": quiz, "source_text": text}
