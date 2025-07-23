from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

import json
import re

#from Retriever import Retriever
from functions import unsupervised_cosine_similarity
import config

# Retrieve functions from the parsing module.
import sys
import os

dir_path_current: str = os.path.dirname(os.path.abspath(__file__))
sys.path.append(dir_path_current)
sys.path.append(
    dir_path_current.removesuffix("/client/classifier") + \
    "/parsing/python/json/")

from JsonParserCrossref import JsonParserCrossref
# </Retrieve functions from the parsing module>

# <Retrieve keywords>
from functions import load_json

challenge_keywords: dict[str, list[str]]= \
    load_json('data/challenge_keywords.json')
theme_keywords: dict[str, list[str]] = \
    load_json('data/theme_keywords.json')
scientificTheme_keywords: dict[str, list[str]] = \
    load_json('data/scientificTheme_keywords.json')
mobilityType_keywords: dict[str, list[str]] = \
    load_json('data/mobilityType_keywords.json')
axe_keywords: dict[str, list[str]] = \
    load_json('data/axe_keywords.json')
usage_keywords: dict[str, list[str]] = \
    load_json('data/usage_keywords.json')
# </Retrieve keywords>

socketio = SocketIO()
#retriever = Retriever()

# <Classification to labellize dataset>
def dataset_parsing(data: str) -> str:

    # <Parsing>
    data_dict = json.loads(data)
    data_to_classify_generic: str = JsonParserCrossref(jsonfile=None)\
                                        .classify_me(line_json=data_dict)
    # </Parsing>

    # <debug>
    doi: str = data_dict.get("DOI", "")
    print("Extracted DOI:", doi)
    print(data_to_classify_generic)
    # </debug>

    return data_to_classify_generic
# </Classification to labellize dataset>

# <Live Classification>
def live_parsing(data: str) -> str:

    # <Parsing>
    data_parsed: str = JsonParserCrossref(data)
    doi: str = data_parsed.ID().get("DOI", "")
    data_to_classify_generic: str = data_parsed.classify_me()
    # </Parsing>

    # <debug>
    print("Extracted DOI:", doi)
    print(data_to_classify_generic)
    # </debug>

    return data_to_classify_generic
# </Live Classification>

# <Classification Response>
def classification_results(data: str) -> dict[str, list[str]]:
    """
    :param data: It is not already parsed.
    """

    challenges: str = json.dumps(
        unsupervised_cosine_similarity(data,
                                       challenge_keywords,
                                       precision_utility=0.10,
                                       precision=0.05)
    )

    themes: str = json.dumps(
        unsupervised_cosine_similarity(data,
                                       theme_keywords,
                                       precision_utility=0.20,
                                       precision=0.05)
    )

    scientificThemes: str = json.dumps(
        unsupervised_cosine_similarity(data,
                                       scientificTheme_keywords,
                                       precision_utility=0.10,
                                       precision=0.4)
    )

    mobilityTypes: str = json.dumps(
        unsupervised_cosine_similarity(data,
                                       mobilityType_keywords,
                                       precision_utility=0.20,
                                       precision=0.002)
    )

    if mobilityTypes == "[]":
        axes: str = "[]"
    else:
        axes: str = json.dumps(
            unsupervised_cosine_similarity(data,
                                           axe_keywords,
                                           precision_utility=0.10,
                                           precision=0.009)
        )

    if mobilityTypes == "[]":
        usages: str = "[]"
    else:
        usages: str = json.dumps(
            unsupervised_cosine_similarity(data,
                                           usage_keywords,
                                           precision_utility=0.25,
                                           precision=0.009)
        )

    return {
        'challenges': challenges,
        'themes': themes,
        'scientificThemes': scientificThemes,
        'mobilityTypes': mobilityTypes,
        'axes': axes,
        'usages': usages,
    }

def classification_error(results: dict[str, list[str]]) -> bool:

    if 'challenges' in results and results['challenges'] == "[]":
        #results['challenges'] = '[ "No challenges found" ]'
        results['challenges'] = '[ "Other"]'

    if 'themes' in results and results['themes'] == "[]":
        #results['themes'] = '[ "No themes found" ]'
        results['themes'] = '[ "Other" ]'

    if 'scientificThemes' in results and results['scientificThemes'] == "[]":
        #results['scientificThemes'] = '[ "No scientific themes found" ]'
        results['scientificThemes'] = '[ "Other" ]'

    if 'mobilityTypes' in results and results['mobilityTypes'] == "[]":
        #results['mobilityTypes'] = '[ "No mobility types found" ]'
        results['mobilityTypes'] = '[ "Other" ]'

    if 'axes' in results and results['axes'] == "[]":
        #results['axes'] = '[ "No axes found" ]'
        results['axes'] = '[ "Other" ]'

    if 'usages' in results and results['usages'] == "[]":
        #results['usages'] = '[ "No usages found" ]'
        results['usages'] = '[ "Other" ]'

    return False
# </Classification Response>

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
    results = classification_results(data)

    if classification_error(results):
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
    results = classification_results(live_parsing(data))

    if classification_error(results):
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
    results = dataset_classification_results(dataset_parsing(data))

    if classification_error(results):
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

