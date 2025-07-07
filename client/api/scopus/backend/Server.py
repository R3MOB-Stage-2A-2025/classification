import httpx
import re
import json
from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# Retrieve environment variables.
import os
from dotenv import load_dotenv, dotenv_values

load_dotenv()
BACKEND_PORT: int = int(os.getenv("BACKEND_PORT"))
BACKEND_SECRETKEY: str = os.getenv("BACKEND_SECRETKEY")
FRONTEND_HOST: str = os.getenv("FRONTEND_HOST")
PYBLIOMETRICS_APIKEY: str = os.getenv("PYBLIOMETRICS_APIKEY")
# </Retrieve environment variables>

# pyblometrics Initialization
import pybliometrics

pybliometrics.scopus.utils.init(keys=[PYBLIOMETRICS_APIKEY])

def pybliometrics_query(query: str) -> str:
    """
    :param query: `Title, author, DOI, ORCID iD, etc..`
    :return: the result of ``pybliometrics.scopus.*()``. It is various *json*.
             the result is a string from `json.dumps()`.
    """

    query: str = query
    refresh: bool | int = False
    verbose: bool = True
    download: bool = False
    integrity_fields: list[str] | tuple(str) = None
    integrity_action: str = 'raise'

    qq = pybliometrics.scopus.AuthorSearch(
        query=query,
        refresh=refresh,
        verbose=verbose,
        download=download,
        integrity_fields=integrity_fields,
        integrity_action=integrity_action
    )

    qq.__str__()
    return ""

pybliometrics_query("mohamed mosbah")

# </pybliometrics Initialization>

app = Flask(__name__)
app.config['SECRET_KEY'] = BACKEND_SECRETKEY
CORS(app, resources={r"/*": { "origins": "*" }})
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on("connect")
def connected():
    """event listener when client connects to the backend"""
    print(f'client number {request.sid} is connected')

@socketio.on('data')
def handle_message(data):
    """event listener when client types a message"""
    print("data from the front end: ", str(data))

@socketio.on("search_query")
def handle_search_query(data: str) -> None:
    """
    :param data: A *json* file.
    The parameters of this *json* file are:

        - `query`.

    Nothing more.

    The thing sent using `emit()` is:

        - a dictionary if it is an error, on `search_error` event.
        Example:
            ```
            {
                "error":
                {
                    "type": "ServerError",
                    "message": "blablabla"
                }
            }
            ```

        - a string using `json.stringify()` on `cr.works()`.
    """

    # <Parse json data>
    data_dict: dict[str, int | str] = json.loads(data)

    # `data.get() returns None if it does not find the key.`
    query: str = data_dict.get('query')
    offset: int = data_dict.get('offset')

    print(f"Search query received: {query}")
    # </Parse json data>

    # <Send query to pybliometrics>
    results_str: str = pybliometrics_query(query, publisher)
    print(f"Raw results from pybliometrics_query: \n{results_str}")
    # </Send query to pybliometrics>

    # <Send the pybliometrics result>
    parsed_output: dict = json.loads(results_str)

    if 'error' in parsed_output:
        emit("search_results", { 'results': None }, to=request.sid)
        emit("search_error", json.loads(results_str), to=request.sid)
    else:
        emit("search_results", { 'results': results_str }, to=request.sid)
    # </Send the pybliometrics result>

@socketio.on("disconnect")
def disconnected():
    """event listener when client disconnects to the backend"""
    print(f'client number {request.sid} is disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True, host=FRONTEND_HOST, port=BACKEND_PORT)

