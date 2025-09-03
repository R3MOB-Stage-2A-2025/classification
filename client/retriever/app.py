from flask import Flask, request, abort
from flask_socketio import SocketIO, emit
from flask_cors import CORS

import json
import re

from Retriever import Retriever
import config

socketio = SocketIO(async_mode="gevent", path="/socket.io/")
retriever = Retriever()

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
    if not isinstance(data, str) or len(data) > config.FLASK_MAX_INPUT_LENGTH:
        abort(400)  # Invalid input

#@socketio.on_error()
def handle_error(e):
    error_str: str = e.__str__()
    error_json_dict: dict[str, dict] = { 'error': { 'message': error_str } }

    emit("search_results", { 'results': None }, to=request.sid)
    emit("search_error", error_json_dict, to=request.sid)
    print("ERROR:\n " + error_str + "\n/ERROR")

@socketio.on("search_query")
def handle_search_query(data: str) -> None:
    if not isinstance(data, str) or len(data) > config.FLASK_MAX_INPUT_LENGTH:
        print('data:')
        print(data)
        abort(400)  # Invalid input

    # <Parse json data>
    def safe_object_hook(obj):
        # Only allow known keys to prevent hefty exploitations
        allowed_keys = [ 'query', 'limit', 'sort', 'cursor_max' ]
        return {key: obj[key] for key in obj if key in allowed_keys}

    data_dict: dict[str, int | str] =\
        json.loads(data, object_hook=safe_object_hook)

    query: str = str(data_dict.get('query', ""))
    limit: int = int(data_dict.get('limit', 10))
    sort: str = str(data_dict.get('sort', ""))
    cursor_max: int = int(data_dict.get('cursor_max', 100))

    print(f"Search query received: {query[:100]}")
    # </Parse json data>

    # <Send query to the API cluster>
    regex_openalex: str = r'https:\/\/openalex\.org\/W\d+'
    OPENALEX_query: str = re.match(string=query, pattern=regex_openalex)

    if OPENALEX_query != None:
        results_str: str = retriever.query_openalex(query=query)

    else:
        results_str: str =\
            retriever.query(query, limit=limit, sort=sort,\
                            cursor_max=cursor_max, client_id=request.sid)
    # </Send query to API cluster>

    # <Send the API cluster result>
    send_api_cluster_result(results_str=results_str)
    # </Send the API cluster result>

@socketio.on("convert_from_openalex")
def handle_convert_from_openalex(data: str) -> None:
    if not isinstance(data, str) or len(data) > config.FLASK_MAX_INPUT_LENGTH:
        abort(400)  # Invalid input

    # <Parse json data>
    data_dict: dict[str, int | str] =\
        json.loads(data)

    print(f"Conversion query from Openalex received: {data[:100]}")
    # </Parse json data>

    # <Send query to the API cluster>
    results_str: str =\
        retriever.convert_from_openalex(data_dict)
    # </Send query to API cluster>

    # <Send the API cluster result>
    send_api_cluster_result(results_str=results_str)
    # </Send the API cluster result>

def send_api_cluster_result(results_str: str = "") -> None:
    potential_error_in_dict: dict = json.loads(results_str)
    if "error" in potential_error_in_dict:
        emit("search_results", { 'results': None }, to=request.sid)
        emit("search_error", potential_error_in_dict, to=request.sid)
        print("ERROR:\n " + results_str + "\n/ERROR")
    else:
        print(f"Raw results from query(): \n{results_str}")
        emit("search_results", { 'results': results_str }, to=request.sid)

@socketio.on("search_query_cursor")
def handle_search_query_cursor(data: str = None) -> None:
    if not isinstance(data, str) or len(data) > config.FLASK_MAX_INPUT_LENGTH:
        abort(400)  # Invalid input

    # <Parse json data>
    def safe_object_hook(obj):
        # Only allow known keys to prevent hefty exploitations
        allowed_keys = [ 'id_cursor' ]
        return {key: obj[key] for key in obj if key in allowed_keys}

    data_dict: dict[str, int | str] =\
        json.loads(data, object_hook=safe_object_hook)

    id_cursor: int = int(data_dict.get('id_cursor', 0))
    print(f"Client {request.sid}: Next Cursor={id_cursor} Query received.")
    # </Parse json data>

    try:
        # <Send query to the API cluster>
        results_str: str =\
        retriever.query_cursor(client_id=request.sid, id_cursor=id_cursor)
        # </Send query to API cluster>

        # <Send the API cluster result>
        send_api_cluster_result(results_str=results_str)
        # </Send the API cluster result>

    except Exception as e:
        emit("search_results", { 'results': None }, to=request.sid)
        emit("search_error", { "error": { "message": str(e) } }, to=request.sid)
        print(f"ERROR in query_cursor: {e}")

@socketio.on("disconnect")
def disconnected(data: str = None) -> None:
    print(f'client number {request.sid} is disconnected')
    retriever.clear_cache_hashmap(client_id=request.sid)

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

