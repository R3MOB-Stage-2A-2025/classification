from flask import Flask, request, abort
from flask_socketio import SocketIO, emit
from flask_cors import CORS

import json
import re
from time import time

from Retriever import Retriever
import config

socketio = SocketIO(async_mode="gevent", path="/socket.io/")
retriever = Retriever()

def create_app() -> Flask:
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config.FLASK_BACKEND_SECRETKEY
    CORS(app, resources={r"/*": { "origins": "*" }})
    socketio.init_app(app, cors_allowed_origins=config.FLASK_ALLOWED_ORIGINS)

    config.debug_wrapper(timestamp=time(), message="Retriever app created.")
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

    emit("search_results", { 'results': None }, to=request.sid)
    emit("search_error", error_json_dict, to=request.sid)

    config.debug_wrapper(event="error", timestamp=time(),\
                         clientid=request.sid,\
                         message=f'ERROR\n{error_str}\n/ERROR')

@socketio.on("search_query")
def handle_search_query(data: str) -> None:
    if not isinstance(data, str) or len(data) > config.FLASK_MAX_INPUT_LENGTH:
        config.debug_wrapper(event="search_query", timestamp=time(),\
                     clientid=request.sid,\
                     typeof=type(data), length=len(data), message="send 400")
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

    config.debug_wrapper(event="search_query", timestamp=time(), limit=limit,\
                         clientid=request.sid,\
                         sort=sort, cursor_max=cursor_max, query=query)
    # </Parse json data>

    # <Send query to the API cluster>
    regex_openalex: str = r'https:\/\/openalex\.org\/W\d+'
    OPENALEX_query: str = re.match(string=query, pattern=regex_openalex)

    if OPENALEX_query != None:
        config.debug_wrapper(event="search_query", timestamp=time(),\
                             clientid=request.sid,\
                             OPENALEX={OPENALEX_query},\
         message="detected OPENALEX ids, launching retriever.query_openalex()")

        results_str: str = retriever.query_openalex(query=query)

    else:
        config.debug_wrapper(event="search_query", timestamp=time(),\
                             clientid=request.sid,\
                             message="calling retriever.query()")

        results_str: str =\
            retriever.query(query, limit=limit, sort=sort,\
                            cursor_max=cursor_max, client_id=request.sid)
    # </Send query to API cluster>

    # <Send the API cluster result>
    config.debug_wrapper(event="search_query",\
                         timestamp=time(),\
                     clientid=request.sid, message="emit to the client.")

    send_api_cluster_result(results_str=results_str)
    # </Send the API cluster result>

@socketio.on("convert_from_openalex")
def handle_convert_from_openalex(data: str) -> None:
    if not isinstance(data, str) or len(data) > config.FLASK_MAX_INPUT_LENGTH:
        config.debug_wrapper(event="convert_from_openalex", timestamp=time(),\
                     clientid=request.sid,\
                     typeof=type(data), length=len(data), message="send 400")
        abort(400)  # Invalid input

    # <Parse json data>
    data_dict: dict[str, int | str] =\
        json.loads(data)

    config.debug_wrapper(event="convert_from_openalex", timestamp=time(),\
                         length=f'{len(data)} characters', head={data[:50]})
    # </Parse json data>

    # <Send query to the API cluster>
    config.debug_wrapper(event="convert_from_openalex", timestamp=time(),\
                         clientid=request.sid,\
                         message="calling retriever.convert_from_openalex()")

    results_str: str =\
        retriever.convert_from_openalex(data_dict)
    # </Send query to API cluster>

    # <Send the API cluster result>
    send_api_cluster_result(results_str=results_str)
    # </Send the API cluster result>

@socketio.on("convert_from_ris")
def handle_convert_from_ris(data: str) -> None:
    if not isinstance(data, str) or len(data) > config.FLASK_MAX_INPUT_LENGTH:
        config.debug_wrapper(event="convert_from_ris", timestamp=time(),\
                     typeof=type(data), length=len(data), message="send 400")
        abort(400)

    config.debug_wrapper(event="convert_from_ris", timestamp=time(),\
                         clientid=request.sid,\
                         length=f'{len(data)} characters', head={data[:50]})

    try:
        config.debug_wrapper(event="convert_from_ris", timestamp=time(),\
                             clientid=request.sid,\
                             message="calling retriever.convert_from_ris()")
        results_dict: dict[str, str | dict] = retriever.convert_from_ris(data)

        config.debug_wrapper(event="convert_from_ris", timestamp=time(),\
                             clientid=request.sid,\
                             message="retriever.convert_from_ris() returned",\
                             output={str(results_dict)[:300]})

        config.debug_wrapper(event="convert_from_ris", timestamp=time(),\
                         clientid=request.sid, message="emit to the client.")
        emit("conversion_ris_results", { "results": json.dumps(results_dict) },\
                                                                to=request.sid)

    except Exception as e:
        error_json_dict = { 'error': { 'message': f'Error conversion RIS: {str(e)}' } }
        emit("search_error", error_json_dict, to=request.sid)

        config.debug_wrapper(event="convert_from_ris", timestamp=time(),\
                             clientid=request.sid,
                             message=f'ERROR:\n{e}\n/ERROR')

@socketio.on("convert_from_crossref_style_to_ris")
def handle_convert_from_crossref_style_to_ris(data: str) -> None:
    if not isinstance(data, str) or len(data) > config.FLASK_MAX_INPUT_LENGTH:
        config.debug_wrapper(event="convert_from_crossref_style_to_ris",\
                             timestamp=time(), clientid=request.sid,\
                     typeof=type(data), length=len(data), message="send 400")
        abort(400)  # Invalid input

    # <Parse json data>
    data_dict: dict[str, int | str] =\
        json.loads(data)

    config.debug_wrapper(event="convert_from_crossref_style_to_ris",\
                         timestamp=time(), clientid=request.sid,\
                         length=f'{len(data)} characters', head={data[:50]})
    # </Parse json data>

    # <Send query to the API cluster>
    config.debug_wrapper(event="convert_from_crossref_style_to_ris",\
                         timestamp=time(), clientid=request.sid,\
             message="calling retriever.convert_from_crossref_style_to_ris()")

    try:
        results_str: str =\
            retriever.convert_from_crossref_style_to_ris(data_dict)

        config.debug_wrapper(event="convert_from_crossref_style_to_ris",\
                             timestamp=time(), clientid=request.sid,\
             message="retriever.convert_from_crossref_style_to_ris() returned",\
                             output_head={results_str[:50]})

        # </Send query to API cluster>

        # <Send the API cluster result>
        config.debug_wrapper(event="convert_from_crossref_style_to_ris",\
                             timestamp=time(),\
                         clientid=request.sid, message="emit to the client.")

        emit("conversion_ris_results", { 'results': results_str }, to=request.sid)
        # </Send the API cluster result>

    except Exception as e:
        error_json_dict = { 'error': { 'message': f'Erreur conversion to RIS: {str(e)}' } }
        emit("search_error", error_json_dict, to=request.sid)

        config.debug_wrapper(event="convert_from_crossref_style_to_ris",\
                             timestamp=time(), clientid=request.sid,\
                             message=f'ERROR\n{e}\n/ERROR')

@socketio.on("search_query_cursor")
def handle_search_query_cursor(data: str = None) -> None:
    if not isinstance(data, str) or len(data) > config.FLASK_MAX_INPUT_LENGTH:
        config.debug_wrapper(event="search_query_cursor",\
                             timestamp=time(), clientid=request.sid,\
                     typeof=type(data), length=len(data), message="send 400")
        abort(400)  # Invalid input

    # <Parse json data>
    def safe_object_hook(obj):
        # Only allow known keys to prevent hefty exploitations
        allowed_keys = [ 'id_cursor' ]
        return {key: obj[key] for key in obj if key in allowed_keys}

    data_dict: dict[str, int | str] =\
        json.loads(data, object_hook=safe_object_hook)

    id_cursor: int = int(data_dict.get('id_cursor', 0))

    config.debug_wrapper(event="search_query_cursor", timestamp=time(),\
                         id_cursor=id_cursor, clientid=request.sid,\
                         message="query received.")
    # </Parse json data>

    try:
        # <Send query to the API cluster>
        config.debug_wrapper(event="search_query_cursor", timestamp=time(),\
                 clientid={request.sid},\
                 message="calling retriever.query_cursor()")

        results_str: str =\
        retriever.query_cursor(client_id=request.sid, id_cursor=id_cursor)

        config.debug_wrapper(event="search_query_cursor", timestamp=time(),\
                             message="retriever.query_cursor() returned",\
                             clientid=request.sid,\
                             output_length=len(results_str),\
                             output_head={results_str[:50]})
        # </Send query to API cluster>

        # <Send the API cluster result>
        config.debug_wrapper(event="search_query_cursor",\
                             timestamp=time(),\
                         clientid=request.sid, message="emit to the client.")

        send_api_cluster_result(results_str=results_str)
        # </Send the API cluster result>

    except Exception as e:
        emit("search_results", { 'results': None }, to=request.sid)
        emit("search_error", { "error": { "message": str(e) } }, to=request.sid)

        config.debug_wrapper(event="search_query_cursor",\
                             timestamp=time(), clientid=request.sid,\
                             message=f'ERROR\n{e}\n/ERROR')

@socketio.on("disconnect")
def disconnected(data: str = None) -> None:
    config.debug_wrapper(event="connect", timestamp=time(),\
                     clientid=request.sid,\
                     message="client is disconnected. Also clearing his cache.")
    retriever.clear_cache_hashmap(client_id=request.sid)

def send_api_cluster_result(results_str: str = "") -> None:
    potential_error_in_dict: dict = json.loads(results_str)
    if "error" in potential_error_in_dict:
        emit("search_results", { 'results': None }, to=request.sid)
        emit("search_error", potential_error_in_dict, to=request.sid)
        print("ERROR:\n " + results_str + "\n/ERROR")
    else:
        emit("search_results", { 'results': results_str }, to=request.sid)

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

