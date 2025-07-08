
from flask import Flask, request, jsonify
import boto3

app = Flask(__name__)


@app.route('/api/message', methods=['POST'])
def handle_message():
    data = request.get_json()
    message = data.get('message', '')
    return jsonify({'response': f'Received: {message}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
