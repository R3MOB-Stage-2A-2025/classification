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

themes_keywords: str = load_json('data/themes_keywords.json')
# </Retrieve keywords>

app = Flask(__name__)
app.config['SECRET_KEY'] = BACKEND_SECRETKEY
CORS(app, resources={r"/*": { "origins": "*" }})
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on("connect")
def connected():
    """event listener when client connects to the classification module"""
    print(f'client number {request.sid} is connected')

@socketio.on('data')
def handle_message(data):
    """event listener when client types a message"""
    print("data from the front end: ", str(data))

@socketio.on('classification')
def handle_classify(data) -> None:
    print(f"Classification query received: {query}")

    abstract_text: str = data.get(key='text', default='')
    themes: list[str] = classify_abstract_combined(abstract_text, themes_keywords)

    # debug.
    print(f'Themes found: {themes}')
    # </debug>

    emit("classification_results", jsonify({ 'themes': themes }), to=request.sid)

@socketio.on("disconnect")
def disconnected():
    """event listener when client disconnects to the classification module"""
    print(f'client number {request.sid} is disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True, port=BACKEND_PORT)

