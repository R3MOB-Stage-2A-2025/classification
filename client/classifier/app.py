from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

import json
import re

from Classifier import Classifier
import config

socketio = SocketIO()
classifier = Classifier()

def create_app() -> Flask:
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config.BACKEND_SECRETKEY
    CORS(app, resources={r"/*": { "origins": "*" }})
    socketio.init_app(app, cors_allowed_origins="*")
    return app

@socketio.on("connect")
def connected():
    print(f'client number {request.sid} is connected')

@socketio.on('data')
def handle_message(data):
    print("data from the front end: ", str(data))

@socketio.on_error()
def handle_error(e):
    error_str: str = e.__str__()
    error_json_dict: dict[str, dict] = { 'error': { 'message': error_str } }
    emit("classification_error", error_json_dict, to=request.sid)

    emit(
        "classification_results",
        {
            'challenges': '[]',
            'themes': '[]',
            'scientificThemes': '[]',
            'mobilityTypes': '[]',
            'axes': '[]',
            'usages': '[]',
        },
        to=request.sid
    )

    print("ERROR:\n " + error_str + "\n/ERROR")

@socketio.on('classification')
def handle_json_classify(data: str) -> None:
    print(f"Classification query received: {data}")

    # <Is it a *json* publication or a text?>
    decoder = json.JSONDecoder()
    possible_keys = decoder.memo.fromkeys(data)

    if 'DOI' in possible_keys:
        data_dict = json.loads(data)
        doi = data_dict.get("DOI")
    # </Is it a *json* publication or a text?>

    # <Get the prompt result>
    results: dict[str, list[str]] = classifier.prompt(data)
    if classifier.classification_error(results):
        return
    # </Get the prompt result>

    payload: dict[str, list[str]] = {
        'challenges': results['challenges'],
        'themes': results['themes'],
        'scientificThemes': results['scientificThemes'],
        'mobilityTypes': results['mobilityTypes'],
        'axes': results['axes'],
        'usages': results['usages'],
    }

    if 'DOI' in possible_keys:
        payload['DOI'] = doi

    emit("classification_results", payload, to=request.sid)

@socketio.on("disconnect")
def disconnected():
    print(f'client number {request.sid} is disconnected')

if __name__ == '__main__':
    app: Flask = create_app()
    socketio.run(
        app,
        debug=True,
        host=config.FRONTEND_HOST,
        port=config.BACKEND_PORT
    )

