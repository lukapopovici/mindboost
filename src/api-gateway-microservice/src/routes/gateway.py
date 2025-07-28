from flask import Blueprint, request, jsonify
import requests

gateway = Blueprint('gateway', __name__)

PDF_PARSER_URL = 'http://pdf-parser-service/api/parse'
BEDROCK_API_URL = 'http://bedrock-service/api/ask'

@gateway.route('/api/parse-pdf', methods=['POST'])
def parse_pdf():
    pdf_file = request.files.get('file')
    if not pdf_file:
        return jsonify({'error': 'No file provided'}), 400

    response = requests.post(PDF_PARSER_URL, files={'file': pdf_file})
    if response.status_code != 200:
        return jsonify({'error': 'Failed to parse PDF'}), response.status_code

    parsed_data = response.json()
    return jsonify(parsed_data)

@gateway.route('/api/ask-bedrock', methods=['POST'])
def ask_bedrock():
    data = request.get_json()
    question = data.get('question', '')
    if not question:
        return jsonify({'error': 'No question provided'}), 400

    response = requests.post(BEDROCK_API_URL, json={'question': question})
    if response.status_code != 200:
        return jsonify({'error': 'Failed to get response from Bedrock API'}), response.status_code

    bedrock_response = response.json()
    return jsonify(bedrock_response)