
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

RASA_URL = 'http://localhost:5005/webhooks/rest/webhook'

# ① index.html 서빙
@app.route('/', methods=['GET'])
def home():
    return send_from_directory('.', 'index.html')

# ② 메시지 포워딩
@app.route('/send_message', methods=['POST'])
def send_message():
    payload = request.get_json()
    user_text = payload.get('message')
    rasa_res = requests.post(
        RASA_URL,
        json={'sender': 'user', 'message': user_text},
        timeout=5
    )
    return jsonify(rasa_res.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
