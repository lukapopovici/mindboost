
import json
from flask import Blueprint, request, jsonify
import requests
import boto3
import os
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv

load_dotenv()

gateway = Blueprint('gateway', __name__)

PDF_PARSER_URL = 'http://pdf-parser-service/api/parse'
BEDROCK_REGION = os.environ.get('BEDROCK_REGION', 'us-east-1')
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-v2')

@gateway.route('/api/parse-pdf', methods=['POST'])
import json
def parse_pdf():
    pdf_file = request.files.get('file')
    if not pdf_file:
        return jsonify({'error': 'No file provided'}), 400

    response = requests.post(PDF_PARSER_URL, files={'file': pdf_file})
    if response.status_code != 200:
        return jsonify({'error': 'Failed to parse PDF'}), response.status_code

    parsed_data = response.json()
    # Assume parsed_data contains the text content of the PDF
    pdf_text = parsed_data.get('text') or parsed_data.get('content') or str(parsed_data)
    prompt = (
        "Extract a list of quiz questions from the following study material. "
        "Return the result as a JSON array of objects, each with 'question', 'choices', and 'answer' fields.\n"
        f"Material:\n{pdf_text}\nQuestions:"
    )
    try:
        bedrock = boto3.client('bedrock-runtime', region_name=BEDROCK_REGION)
        body = {
            "prompt": f"Human: {prompt}\nAssistant:",
            "max_tokens_to_sample": 512,
            "temperature": 0.3,
            "top_k": 250,
            "top_p": 1,
            "stop_sequences": ["\nHuman:"]
        }
        bedrock_response = bedrock.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=str(body).replace("'", '"')
        )
        result = bedrock_response['body'].read().decode('utf-8')
        # Try to extract JSON from the result
        try:
            # If the model returns text with JSON inside, extract the JSON part
            start = result.find('[')
            end = result.rfind(']')
            if start != -1 and end != -1:
                quiz_json = result[start:end+1]
                quiz = json.loads(quiz_json)
            else:
                quiz = json.loads(result)
        except Exception as e:
            return jsonify({'error': 'Failed to parse quiz JSON from Bedrock', 'raw': result}), 500
        return jsonify({'quiz': quiz})
    except (BotoCoreError, ClientError) as e:
        return jsonify({'error': f'Failed to get response from Amazon Bedrock: {str(e)}'}), 500

@gateway.route('/api/ask-bedrock', methods=['POST'])
def ask_bedrock():
    data = request.get_json()
    question = data.get('question', '')
    if not question:
        return jsonify({'error': 'No question provided'}), 400

    try:
        bedrock = boto3.client('bedrock-runtime', region_name=BEDROCK_REGION)
        body = {
            "prompt": f"Human: {question}\nAssistant:",
            "max_tokens_to_sample": 256,
            "temperature": 0.5,
            "top_k": 250,
            "top_p": 1,
            "stop_sequences": ["\nHuman:"]
        }
        response = bedrock.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=str(body).replace("'", '"')
        )
        result = response['body'].read().decode('utf-8')
        return jsonify({"bedrock_response": result})
    except (BotoCoreError, ClientError) as e:
        return jsonify({'error': f'Failed to get response from Amazon Bedrock: {str(e)}'}), 500