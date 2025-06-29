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
from functions import unsupervised_cosine_similarity

challenge_keywords: dict[str, list[str]] = \
    load_json('data/challenge_keywords.json')
theme_keywords: dict[str, list[str]] = \
    load_json('data/theme_keywords.json')
scientificTheme_keywords: dict[str, list[str]] = \
    load_json('data/scientificTheme_keywords.json')
mobilityType_keywords: dict[str, list[str]] = \
    load_json('data/mobilityType_keywords.json')
# </Retrieve keywords>

# Retrieve Classification Results
def classification_results(data: str) -> dict[str, list[str]]:
    """
    :param data: it needs to be already parsed.
    """
    try:
        challenges: list[str] = json.dumps(
            unsupervised_cosine_similarity(data, challenge_keywords)
        )

        themes: list[str] = json.dumps(
            unsupervised_cosine_similarity(data, theme_keywords,
                                           precision=0.05)
        )

        scientificThemes: list[str] = json.dumps(
            unsupervised_cosine_similarity(data, scientificTheme_keywords)
        )

        mobilityTypes: list[str] = json.dumps(
            unsupervised_cosine_similarity(data, mobilityType_keywords,
                                           precision=0.02)
        )
    except:
        emit("classification_error", { 'error': 'Impossible to classify' }, to=request.sid)

    return {
        'challenges': challenges or [],
        'themes': themes or [],
        'scientificThemes': scientificThemes or [],
        'mobilityTypes': mobilityTypes or [],
    }

def classification_error(results: dict[str, list[str]]) -> bool:
    if 'challenges' in results and results['challenges'] == "[]":
        emit("classification_error", { 'error': 'No challenges found' }, to=request.sid)
        return True
    elif 'themes' in results and results['themes'] == "[]":
        emit("classification_error", { 'error': 'No themes found' }, to=request.sid)
        return True
    elif 'scientificThemes' in results and results['scientificThemes'] == "[]":
        emit("classification_error", { 'error': 'No scientific themes found' }, to=request.sid)
        return True
    elif 'mobilityTypes' in results and results['mobilityTypes'] == "[]":
        emit("classification_error", { 'error': 'No mobility types found' }, to=request.sid)
        return True
    else:
        return False

# </Retrieve Classification Results>

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
    results = classification_results(data)

    if not classification_error(results):
        emit(
            "classification_results",
            {
                'challenges': results['challenges'],
                'themes': results['themes'],
                'scientificThemes': results['scientificThemes'],
                'mobilityTypes': results['mobilityTypes'],
            },
            to=request.sid
        )

@socketio.on('json_classification')
def handle_json_classify(data: str) -> None:
    print(f"JSON Classification query received: {data}")
    data_parsed: str = JsonParserCrossref(data).classify_me()
    results = classification_results(data_parsed)

    # debug.
    print(data_parsed)
    # </debug>

    if not classification_error(results):
        emit(
            "json_classification_results",
            {
                'challenges': results['challenges'],
                'themes': results['themes'],
                'scientificThemes': results['scientificThemes'],
                'mobilityTypes': results['mobilityTypes'],
            },
            to=request.sid
        )

@socketio.on("disconnect")
def disconnected():
    """event listener when client disconnects to the classification module"""
    print(f'client number {request.sid} is disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True, port=BACKEND_PORT)

