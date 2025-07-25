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
        "text_classification_results",
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

@socketio.on('text_classification')
def handle_classify(data: str) -> None:
    print(f"Classification query received: {data}")

    results: dict[str, list[str]] = classifier.prompt(data)
    if classifier.classification_error(results):
        return

    emit(
        "text_classification_results",
        {
            'challenges': results['challenges'],
            'themes': results['themes'],
            'scientificThemes': results['scientificThemes'],
            'mobilityTypes': results['mobilityTypes'],
            'axes': results['axes'],
            'usages': results['usages'],
        },
        to=request.sid
    )

@socketio.on('json_classification')
def handle_json_classify(data: str) -> None:
    print(f"JSON Classification query received: {data}")
    data_dict = json.loads(data)
    doi = data_dict.get("DOI")

    results: dict[str, list[str]] = classifier.prompt(data)
    if classifier.classification_error(results):
        return

    emit(
        "json_classification_results",
        {
            'DOI': doi,
            'challenges': results['challenges'],
            'themes': results['themes'],
            'scientificThemes': results['scientificThemes'],
            'mobilityTypes': results['mobilityTypes'],
            'axes': results['axes'],
            'usages': results['usages'],
        },
        to=request.sid
    )

@socketio.on('dataset_classification')
def handle_json_classify(data: str) -> None:
    print(f"Dataset Classification query received: {data}")
    data_dict = json.loads(data)
    doi = data_dict.get("DOI")

    results: dict[str, list[str]] = classifier.prompt(data)
    if classifier.classification_error(results):
        return

    emit(
        "dataset_classification_results",
        {
            'DOI': doi,
            'challenges': results['challenges'],
            'themes': results['themes'],
            'scientificThemes': results['scientificThemes'],
            'mobilityTypes': results['mobilityTypes'],
            'axes': results['axes'],
            'usages': results['usages'],
        },
        to=request.sid
    )

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

