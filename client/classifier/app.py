from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

import json
import re

from Classifier import Classifier
import config

# <Use the multithreading to labellize a dataset>, development mode.
#                           Otherwise, production mode is managed by
#                               Gunicorn.
#socketio = SocketIO(async_mode='threading')
# </Use the multithreading to labellize a dataset>

socketio = SocketIO(async_mode='gevent', path='/socket.io/')
classifier = Classifier()

def create_app() -> Flask:
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config.FLASK_BACKEND_SECRETKEY
    CORS(app, resources={r"/*": { "origins": "*" }})
    socketio.init_app(app, cors_allowed_origins=config.FLASK_ALLOWED_ORIGINS)
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
    emit("classification_results", classifier.error_payload(), to=request.sid)

    print("ERROR:\n " + error_str + "\n/ERROR")

@socketio.on('text_classification')
def handle_text_classify(data: str) -> None:
    print(f"Text Classification query received: {data[:100]}")
    parsed_data: str = str(data)

    # <Get the prompt result>
    results: dict[str, list[str]] =\
        classifier.add_extra_class(classifier.prompt_generic(parsed_data))
    # </Get the prompt result>

    emit("classification_results", results, to=request.sid)

@socketio.on('json_classification')
def handle_json_classify(data: str) -> None:
    print(f"Json Classification query received: {data[:100]}")

    # <Parse json data>
    def safe_object_hook(obj):
        # Only allow known keys to prevent hefty exploitations
        allowed_keys: list[str] = [
            "DOI", "ISSN", "OPENALEX", "TL;DR", "URL", "abstract",
            "abstract_inverted_index", "author", "concepts", "container-title",
            "container-url", "keywords", "publication_date", "publisher",
            "reference", "related", "sustainable_development_goals",
            "title", "topics", "type"
        ]

        return {key: obj[key] for key in obj if key in allowed_keys}

    data_dict: dict[str, int | str] =\
        json.loads(data, object_hook=safe_object_hook)

    doi: str = data_dict.get('DOI', "")
    parsed_data: str = classifier.parsing_by_publication(data)
    # </Parse json data>

    # <Get the prompt result>
    results: dict[str, list[str]] =\
        classifier.add_extra_class(classifier.prompt_generic(parsed_data))

    results['DOI'] = doi
    # </Get the prompt result>

    emit("classification_results", results, to=request.sid)

@socketio.on('dataset_classification')
def handle_dataset_classify(data: str) -> None:
    print(f"Classification query received: {data}")

    # <Parse json data>
    def safe_object_hook(obj):
        # Only allow known keys to prevent hefty exploitations
        allowed_keys: list[str] = [
            "DOI", "ISSN", "OPENALEX", "TL;DR", "URL", "abstract",
            "abstract_inverted_index", "author", "concepts", "container-title",
            "container-url", "keywords", "publication_date", "publisher",
            "reference", "related", "sustainable_development_goals",
            "title", "topics", "type"
        ]

        return {key: obj[key] for key in obj if key in allowed_keys}

    data_dict: dict[str, int | str] =\
        json.loads(data, object_hook=safe_object_hook)

    doi: str = str(data_dict.get('DOI', ""))
    # </Parse json data>

    # <Get the prompt result>
    results: dict[str, list[str]] =\
        classifier.add_extra_class(
            classifier.prompt_generic(classifier.parsing_by_line(data))
        )

    results['DOI'] = doi
    # </Get the prompt result>

    emit("classification_results", results, to=request.sid)

@socketio.on("disconnect")
def disconnected(data: str = None):
    print(f'client number {request.sid} is disconnected')

app: Flask = create_app()

# <Development mode>
if __name__ == '__main__':
    socketio.run(
        app,
        debug=config.FLASK_DEBUG,
        host=config.FLASK_FRONTEND_HOST,
        port=config.FLASK_BACKEND_PORT
    )
# </Development mode>

