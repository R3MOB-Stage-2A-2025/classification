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
FRONTEND_HOST: str = os.getenv("FRONTEND_HOST")
# </Retrieve environment variables>

# Retrieve functions from the parsing module.
import sys
import os

dir_path_current: str = os.path.dirname(os.path.abspath(__file__))
sys.path.append(dir_path_current)
sys.path.append(
    dir_path_current.removesuffix("/client/classifier/backend") + \
    "/parsing/python/json/")

from JsonParserCrossref import JsonParserCrossref
# </Retrieve functions from the parsing module>

# Retrieve keywords.
from functions import load_json
from functions import unsupervised_cosine_similarity

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

# Retrieve Classification Results
def classification_results(data: str) -> dict[str, list[str]]:
    """
    :param data: It is not already parsed.
    """

    # <Parsing>
    data_parsed: str = JsonParserCrossref(data)
    doi: str = data_parsed.ID().get("DOI", "")
    data_to_classify_generic: str = data_parsed.classify_me()
    # </Parsing>

    # <debug>
    print("Extracted DOI:", doi)
    print(data_to_classify_generic)
    # </debug>

    challenges: str = json.dumps(
        unsupervised_cosine_similarity(data_to_classify_generic,
                                       challenge_keywords,
                                       precision_utility=0.10,
                                       precision=0.05)
    )

    themes: str = json.dumps(
        unsupervised_cosine_similarity(data_to_classify_generic,
                                       theme_keywords,
                                       precision_utility=0.20,
                                       precision=0.05)
    )

    scientificThemes: str = json.dumps(
        unsupervised_cosine_similarity(data_to_classify_generic,
                                       scientificTheme_keywords,
                                       precision_utility=0.10,
                                       precision=0.4)
    )

    mobilityTypes: str = json.dumps(
        unsupervised_cosine_similarity(data_to_classify_generic,
                                       mobilityType_keywords,
                                       precision_utility=0.20,
                                       precision=0.002)
    )

    if mobilityTypes == "[]":
        axes: str = "[]"
    else:
        axes: str = json.dumps(
            unsupervised_cosine_similarity(data_to_classify_generic,
                                           axe_keywords,
                                           precision_utility=0.10,
                                           precision=0.009)
        )

    if mobilityTypes == "[]":
        usages: str = "[]"
    else:
        usages: str = json.dumps(
            unsupervised_cosine_similarity(data_to_classify_generic,
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
        results['challenges'] = '[ "No challenges found" ]'

    if 'themes' in results and results['themes'] == "[]":
        results['themes'] = '[ "No themes found" ]'

    if 'scientificThemes' in results and results['scientificThemes'] == "[]":
        results['scientificThemes'] = '[ "No scientific themes found" ]'

    if 'mobilityTypes' in results and results['mobilityTypes'] == "[]":
        results['mobilityTypes'] = '[ "No mobility types found" ]'

    if 'axes' in results and results['axes'] == "[]":
        results['axes'] = '[ "No axes found" ]'

    if 'usages' in results and results['usages'] == "[]":
        results['usages'] = '[ "No usages found" ]'

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

    if classification_error(results):
        return

    emit(
        "classification_results",
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
    results = classification_results(data)

    if classification_error(results):
        return

    emit(
        "json_classification_results",
        {
            'doi': doi,
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
    """event listener when client disconnects to the classification module"""
    print(f'client number {request.sid} is disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True, host=FRONTEND_HOST, port=BACKEND_PORT)

