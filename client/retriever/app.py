from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

import json

from Retriever import Retriever
import config

socketio = SocketIO()

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
    print("ERROR:\n " + error_str + "\n/ERROR")

    error_json_str: str = { 'error': { 'message': error_str } }
    emit("search_results", { 'results': None }, to=request.sid)
    emit("search_error", error_json_str, to=request.sid)

@socketio.on("search_query")
def handle_search_query(data: str) -> None:
    # <Parse json data>
    data_dict: dict[str, int | str] = json.loads(data)

    # `data.get()` returns None if it does not find the key.
    query: str = data_dict.get('query')

    print(f"Search query received: {query}")
    # </Parse json data>

    # <Send query to the API cluster>
    results_str: str = Retriever().query(query)
    print(f"Raw results from query(): \n{results_str}")
    # </Send query to API cluster>

    # <Send the API cluster result>
    parsed_output: dict = json.loads(results_str)
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

