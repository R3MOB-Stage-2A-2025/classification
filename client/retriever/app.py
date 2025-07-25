from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

import json
import re

from Retriever import Retriever
import config

socketio = SocketIO()
retriever = Retriever()

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

    emit("search_results", { 'results': None }, to=request.sid)
    emit("search_error", error_json_dict, to=request.sid)
    print("ERROR:\n " + error_str + "\n/ERROR")

@socketio.on("search_query")
def handle_search_query(data: str) -> None:
    # <Parse json data>
    data_dict: dict[str, int | str] = json.loads(data)
    query: str = data_dict.get('query', "")
    offset: int = data_dict.get('offset', 0)
    limit: int = data_dict.get('limit', 10)
    print(f"Search query received: {query}")
    # </Parse json data>

    # <Send query to the API cluster>
    regex_openalex: str = r'"https:\/\/openalex\.org\/W\d+"'
    OPENALEX_query: str = re.match(string=query, pattern=regex_openalex)

    if OPENALEX_query != None:
        results_str: str = retriever.query_openalex(query=query)

    else:
        results_str: str = retriever.query(query, offset=offset, limit=limit)
    # </Send query to API cluster>

    # <Send the API cluster result>
    potential_error_in_dict: dict = json.loads(results_str)
    if "error" in potential_error_in_dict:
        emit("search_results", { 'results': None }, to=request.sid)
        emit("search_error", potential_error_in_dict, to=request.sid)
        print("ERROR:\n " + results_str + "\n/ERROR")
    else:
        print(f"Raw results from query(): \n{results_str}")
        emit("search_results", { 'results': results_str }, to=request.sid)
    # </Send the API cluster result>

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

