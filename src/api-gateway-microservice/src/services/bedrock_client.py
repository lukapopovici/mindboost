from flask import jsonify
import requests

class BedrockClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key

    def ask_question(self, question):
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'question': question
        }
        response = requests.post(f'{self.base_url}/ask', json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': 'Failed to get response from Bedrock API', 'status_code': response.status_code}