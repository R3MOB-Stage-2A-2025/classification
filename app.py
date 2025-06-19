from flask import Flask, request, jsonify, send_from_directory, Response
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# Retrieve environment variables.
import os
from dotenv import load_dotenv, dotenv_values

load_dotenv()
BACKEND_PORT: int = int(os.getenv("BACKEND_PORT"))
BACKEND_SECRETKEY: str = os.getenv("BACKEND_SECRETKEY")
# </Retrieve environment variables>

# Retrieve keywords.
from functions import classify_abstract_combined, load_json

themes_keywords = load_json('data/themes_keywords.json')
# </Retrieve keywords>

app = Flask(__name__)
app.config['SECRET_KEY'] = BACKEND_SECRETKEY
CORS(app, resources={r"/*": { "origins": "*" }})
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/classify', methods=['POST'])
def classify() -> Response:
    data = request.json
    abstract_text = data.get('text', '')

    # Classification
    themes = classify_abstract_combined(abstract_text, themes_keywords)

    return jsonify({'themes': themes})

@app.route('/')
def index():
    return send_from_directory('static', 'classification.html')

@socketio.on("connect")
def connected():
    """event listener when client connects to the classification module"""
    print(f'client number {request.sid} is connected')

@socketio.on('data')
def handle_message(data):
    """event listener when client types a message"""
    print("data from the front end: ", str(data))

@socketio.on("disconnect")
def disconnected():
    """event listener when client disconnects to the classification module"""
    print(f'client number {request.sid} is disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True, port=BACKEND_PORT)

