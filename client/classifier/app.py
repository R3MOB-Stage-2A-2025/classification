from flask import Flask, request, abort
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from time import time

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

    config.debug_wrapper(timestamp=time(), message="Classifier app created.")
    return app

@socketio.on("connect")
def connected():
    config.debug_wrapper(event="connect", timestamp=time(),\
                     clientid=request.sid, message="client is connected.")

@socketio.on('data')
def handle_message(data):
    config.debug_wrapper(event="data", timestamp=time(), data=str(data))

    if not isinstance(data, str) or len(data) > config.FLASK_MAX_INPUT_LENGTH:
        config.debug_wrapper(event="data", timestamp=time(),\
                             typeof=type(data), clientid=request.sid,\
                             length=len(data), message="send 400")
        abort(400)  # Invalid input

@socketio.on_error()
def handle_error(e):
    error_str: str = e.__str__()
    error_json_dict: dict[str, dict] = { 'error': { 'message': error_str } }

    emit("classification_error", error_json_dict, to=request.sid)
    emit("classification_results", classifier.error_payload(), to=request.sid)

    config.debug_wrapper(event="error", timestamp=time(),\
                         clientid=request.sid,\
                         message=f'ERROR\n{error_str}\n/ERROR')

@socketio.on('text_classification')
def handle_text_classify(data: str) -> None:

    if not isinstance(data, str) or len(data) > config.FLASK_MAX_INPUT_LENGTH:
        config.debug_wrapper(event="text_classification", timestamp=time(),\
                             typeof=type(data), clientid=request.sid,\
                             length=len(data), message="send 400")
        abort(400)  # Invalid input

    parsed_data: str = str(data)
    config.debug_wrapper(event="text_classification", timestamp=time(),\
                         clientid=request.sid, prompt=parsed_data)

    # <Get the prompt result>
    config.debug_wrapper(event="text_classification", timestamp=time(),\
                         clientid=request.sid,\
                         message="calling classifier.prompt_generic()")

    results: dict[str, list[str]] =\
        classifier.add_extra_class(classifier.prompt_generic(parsed_data))

    config.debug_wrapper(event="text_classification", timestamp=time(),\
                         clientid=request.sid,\
                         message="classifier.prompt_generic() returned",\
                         output={str(results)[:300]})
    # </Get the prompt result>

    config.debug_wrapper(event="text_classification",\
                         timestamp=time(),\
                     clientid=request.sid, message="emit to the client.")

    emit("classification_results", results, to=request.sid)

@socketio.on('json_classification')
def handle_json_classify(data: str) -> None:

    if not isinstance(data, str) or len(data) > config.FLASK_MAX_INPUT_LENGTH:
        config.debug_wrapper(event="json_classification", timestamp=time(),\
                             typeof=type(data), clientid=request.sid,\
                             length=len(data), message="send 400")
        abort(400)  # Invalid input

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

    config.debug_wrapper(event="json_classification", timestamp=time(),\
                         clientid=request.sid, doi=doi,\
                         parsed_data=parsed_data[300:])
    # </Parse json data>

    # <Get the prompt result>
    config.debug_wrapper(event="json_classification", timestamp=time(),\
                         clientid=request.sid,\
                         message="calling classifier.prompt_generic()")

    results: dict[str, list[str]] =\
        classifier.add_extra_class(classifier.prompt_generic(parsed_data))

    results['DOI'] = doi

    config.debug_wrapper(event="json_classification", timestamp=time(),\
                         clientid=request.sid,\
                         message="classifier.prompt_generic() returned",\
                         output={str(results)[:300]})
    # </Get the prompt result>

    config.debug_wrapper(event="json_classification",\
                         timestamp=time(),\
                     clientid=request.sid, message="emit to the client.")

    emit("classification_results", results, to=request.sid)

@socketio.on('dataset_classification')
def handle_dataset_classify(data: str) -> None:

    if not isinstance(data, str) or len(data) > config.FLASK_MAX_INPUT_LENGTH:
        config.debug_wrapper(event="dataset_classification", timestamp=time(),\
                             typeof=type(data), clientid=request.sid,\
                             length=len(data), message="send 400")
        abort(400)  # Invalid input

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

    config.debug_wrapper(event="dataset_classification", timestamp=time(),\
                         clientid=request.sid, doi=doi,\
                         parsed_data=str(data_dict)[300:])
    # </Parse json data>

    # <Get the prompt result>
    config.debug_wrapper(event="dataset_classification", timestamp=time(),\
                         clientid=request.sid,\
                         message="calling classifier.prompt_generic()")

    results: dict[str, list[str]] =\
        classifier.add_extra_class(
            classifier.prompt_generic(classifier.parsing_by_line(data))
        )

    results['DOI'] = doi

    config.debug_wrapper(event="dataset_classification", timestamp=time(),\
                         clientid=request.sid,\
                         message="classifier.prompt_generic() returned",\
                         output={str(results)[:300]})
    # </Get the prompt result>

    config.debug_wrapper(event="dataset_classification",\
                         timestamp=time(),\
                     clientid=request.sid, message="emit to the client.")

    emit("classification_results", results, to=request.sid)

@socketio.on("disconnect")
def disconnected(data: str = None):
    config.debug_wrapper(event="connect", timestamp=time(),\
                     clientid=request.sid,\
                     message="client is disconnected.")

app: Flask = create_app()

# <Development mode>
if __name__ == '__main__':
    config.debug_wrapper(timestamp=time(),\
                         message="Development mode initialized.")

    socketio.run(
        app,
        debug=config.FLASK_DEBUG,
        host=config.FLASK_FRONTEND_HOST,
        port=config.FLASK_BACKEND_PORT
    )
# </Development mode>

