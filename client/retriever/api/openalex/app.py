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
PYALEX_MAILTO: str = os.getenv("PYALEX_MAILTO")
# </Retrieve environment variables>

# OpenAlex Initialization
from pyalex import config

config.email = PYALEX_MAILTO
config.max_retries = 0
config.retry_backoff_factor = 0.1
config.retry_http_codes = [429, 500, 503]

#from pyalex import Works, Authors, Sources, Institutions, Topics, Publishers, Funders
from pyalex import Works

def generic_dates(results: dict[str, dict]) -> dict[str, dict]:
    """
    :param: something returned by `Works.search()`.
    :return: Something with this type of date: `YYYY-MM-DD`.
    """
    results_with_better_date: dict[str, dict] = results

    # TODO if necessary.

    #for item in results_with_better_date['message']['items']:
        #if 'created' in item and 'date-parts' in item['created']:
            #date_parts = item['created']['date-parts'][0]

            ## Format date as YYYY-MM-DD for consistency and easier sorting
            #item['publication_date'] = \
                #f"{date_parts[0]:04d}-{date_parts[1]:02d}-{date_parts[2]:02d}"

    # </TODO if necessary>

    return results_with_better_date

def openalex_query(query: str) -> str:
    """
    :param query: `Title, author, DOI, ORCID iD, etc..`
    :return: the result of ``pyalex.Works.search()``. It is various *json*.
             the result is a string from `json.dumps()`.
    """
    # Detect if the query is actually a concatenation of *DOI*s.
    regex: str = r'10\.\d{4,9}/[\w.\-;()/:]+'
    ids: list[str] = re.findall(regex, query)

    w = Works()

    try:
        return json.dumps(generic_dates(
                    w[query]
                ))

    except httpx.HTTPStatusError as e:
        print(f'\nHTTPStatusError: {e}\nResponse: {e.response.text}\n')
        error_payload = {
            'error': {
                'type': 'HTTPStatusError',
                'message': f"OpenAlex API request failed:\
                        {e.response.status_code} {e.response.reason_phrase}",
                'status_code': e.response.status_code,
                'details': str(e.response.text)[:200]
            }
        }
        return json.dumps(error_payload)

    except Exception as e:
        print(f'\nRuntimeError or other unhandled exception: {e}\n')
        error_payload = {
            'error': {
                'type': 'ServerError',
                'message': f"An unexpected error occurred on the server: {str(e)}"
            }
        }
        return json.dumps(error_payload)

# </OpenAlex Initialization>

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

        - a string using `json.stringify()` on `pyalex.Works()`.
    """

    # <Parse json data>
    data_dict: dict[str, int | str] = json.loads(data)

    # `data.get() returns None if it does not find the key.`
    query: str = data_dict.get('query')

    print(f"Search query received: {query}")
    # </Parse json data>

    # <Send query to OpenAlex>
    results_str: str = openalex_query(query)
    print(f"Raw results from openalex_query: \n{results_str}")
    # </Send query to OpenAlex>

    # <Send the OpenAlex result>
    parsed_output: dict = json.loads(results_str)

    if 'error' in parsed_output:
        emit("search_results", { 'results': None }, to=request.sid)
        emit("search_error", json.loads(results_str), to=request.sid)
    else:
        emit("search_results", { 'results': results_str }, to=request.sid)
    # </Send the OpenAlex result>

@socketio.on("disconnect")
def disconnected():
    """event listener when client disconnects to the backend"""
    print(f'client number {request.sid} is disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True, host=FRONTEND_HOST, port=BACKEND_PORT)

