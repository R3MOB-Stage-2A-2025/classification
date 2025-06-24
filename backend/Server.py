import json
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

# Retrieve functions from the parsing module.
import sys
import os

dir_path_current: str = os.path.dirname(os.path.abspath(__file__))
os.chdir('..')

dir_path: str = os.path.dirname(
    os.path.abspath("parsing/python/json/JsonParserCrossref.py")
)
sys.path.append(dir_path)

from JsonParserCrossref import JsonParserCrossref

os.chdir(dir_path_current)
# </Retrieve functions from the parsing module>

# Retrieve keywords.
from functions import load_json
from functions import classify_abstract_by_keywords
from functions import classify_abstract_TF_IDF

themes_keywords: dict[str, list[str]] = load_json('data/themes_keywords.json')
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
def handle_classify(data: str) -> None:
    print(f"Classification query received: {data}")

    themes: str = json.dumps(
        classify_abstract_TF_IDF(data, themes_keywords)
    )

    # debug.
    print(f'Themes found: {themes}')
    # </debug>

    if themes == "[]":
        emit("classification_error", { 'error': 'No themes found' }, to=request.sid)
    else:
        emit("classification_results", { 'themes': themes }, to=request.sid)

@socketio.on('json_classification')
def handle_json_classify(data: str) -> None:
    print(f"JSON Classification query received: {data}")

    data_parsed: str = JsonParserCrossref(data).classify_me()

    # debug.
    print(data_parsed)
    # </debug>

    #try:
    themes: str = json.dumps(
        classify_abstract_by_keywords(data_parsed, themes_keywords)
    )
    #except:
        #emit("json_classification_error", { 'error': 'Impossible to classify' }, to=request.sid)

    # debug.
    print(f'Themes found: {themes}')
    # </debug>

    if themes == "[]":
        emit("json_classification_error", { 'error': 'No themes found' }, to=request.sid)
    else:
        emit("json_classification_results", { 'themes': themes }, to=request.sid)

@socketio.on("disconnect")
def disconnected():
    """event listener when client disconnects to the classification module"""
    print(f'client number {request.sid} is disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True, port=BACKEND_PORT)

