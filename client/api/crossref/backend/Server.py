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

HABANERO_BASEURL: str = os.getenv("HABANERO_BASEURL")
HABANERO_APIKEY: str = os.getenv("HABANERO_APIKEY")
HABANERO_MAILTO: str = os.getenv("HABANERO_MAILTO")
HABANERO_TIMEOUT: int = int(os.getenv("HABANERO_TIMEOUT")) # seconds
# </Retrieve environment variables>

# Habanero Initialization
from habanero import Crossref, RequestError

xrate_limit: str = "" "X-Rate-Limit-Limit: 100"
xrate_interval: str = "" "X-Rate-Limit-Interval: 1s"
ua_string: str = xrate_limit + ";" + xrate_interval

cr: Crossref = Crossref(
    base_url = HABANERO_BASEURL,
    api_key = HABANERO_APIKEY,
    mailto = HABANERO_MAILTO,
    ua_string = ua_string,
    timeout = HABANERO_TIMEOUT
)

def generic_habanero_output(results: dict[str, dict] | list) -> dict[str, dict]:
    """
    Imagine if a single publication is retrieved, there is no "items".
    I want `results['message']['items']` to be here to be more generic.

    :param results: something returned by `cr.works()`.
    Besides, if there were multiple `ids`, `cr.works()` returns a list. WTF.

    :return: results but it is sure that `result['message']['items']` exists.
    """

    def genericity(result: dict[str, dict]) -> dict[str, dict]:
        generic_result: dict[str, dict] = result

        if 'message' in result and 'items' not in result['message']:
            generic_result = {
                'message': {
                    'items': [ result['message'] ]
                }
            }

        return generic_result

    if not type(results) == list:
        return genericity(results)

    # Habanero returns a list if multiple DOI's were given...
    generic_results: dict[str, dict] = genericity(results[0])
    for result in results[1:]:
        generic_results['message']['items'].append(result['message'])

    return generic_results

def generic_dates(results: dict[str, dict]) -> dict[str, dict]:
    """
    :param: something returned by `cr.works()`.
    This something is not an error. It contains `results['message']['items']`.

    Something with this type of date: `YYYY-MM-DD`.
    """
    results_with_better_date: dict[str, dict] = results

    for item in results_with_better_date['message']['items']:
        if 'created' in item and 'date-parts' in item['created']:
            date_parts = item['created']['date-parts'][0]

            # Format date as YYYY-MM-DD for consistency and easier sorting
            item['publication_date'] = \
                f"{date_parts[0]:04d}-{date_parts[1]:02d}-{date_parts[2]:02d}"

    return results_with_better_date

def habanero_query(query: str, publisher: str = None, offset: int = 0, limit: int = 10) -> str:
    """
    :param query: `Title, author, DOI, ORCID iD, etc..`
    :param publisher: special parameter to find related publications.
        This parameter is usually the `container-title` of the response.
    :return: the result of ``habanero.Crossref.works()``. It is various *json*.
             the result is a string from `json.dumps()`.
    """
    # Detect if the query is actually a concatenation of *DOI*s.
    regex: str = r'10\.\d{4,9}/[\w.\-;()/:]+'
    ids: list[str] = re.findall(regex, query)

    filtering: dict = {
        #'type': 'journal-article',
    }

    # TODO: this thing does not work I don't know why.
    if publisher != None:
        filtering['container-title'] = publisher
    # </TODO>

    # "Don't use *rows* and *offset* in the */works* route.
    # They are very expansive and slow. Use cursors instead."
    offset = offset

    limit = limit # Default is 20
    sort: str = "relevance"
    order: str = "desc"

    # TODO: find a way to retrieve the publication abstract,
    #       there are too many retrieved publications for which only
    #       the title is public.
    #       Need to recursively retrieve publications from references etc..
    facet: str | bool | None = None # "relation-type:5"
    # </TODO>

    # What could happen:
    #   - the *abstract* is located in the *title* section.
    #   - *subject* is almost never present.
    #   - the *issn-value*: is too generic. (ex: "Electronic")
    #   - there could be A LOT of authors. (too many).
    select: list[str] | str | None = [
        "DOI",
        "type",
        "container-title",
        "issn-type",
        "subject",
        "title",
        "abstract",
        "publisher",
        "author",
        "created", # for publication date
        "URL",
        "references-count", # ]
        "reference",        # ] what the publication is citing.
    ]

    # TODO: add cursors on the *frontend*.
    cursor: str = "*"
    cursor: str = None # Cursor can't be combined with *offset* or *sample*.
    cursor_max: float = 10
    # <TODO>

    progress_bar: bool = False

    try:
        if len(ids) > 0:
            return json.dumps(generic_dates(generic_habanero_output(
                        cr.works(ids=ids)
                    )))

        return json.dumps(generic_dates(generic_habanero_output(
                    cr.works(
                        query = query,
                        filter = filtering,
                        offset = offset,
                        limit = limit,
                        sort = sort,
                        order = order,
                        facet = facet,
                        select = select,
                        cursor = cursor,
                        cursor_max = cursor_max,
                        progress_bar = progress_bar
                    )
                )))

    except httpx.HTTPStatusError as e:
        print(f'\nHTTPStatusError: {e}\nResponse: {e.response.text}\n')
        error_payload = {
            'error': {
                'type': 'HTTPStatusError',
                'message': f"Crossref API request failed:\
                        {e.response.status_code} {e.response.reason_phrase}",
                'status_code': e.response.status_code,
                'details': str(e.response.text)[:200]
            }
        }
        return json.dumps(error_payload)

    except RequestError as e:
        print(f'\nRequestError: {e}\n')
        error_payload = {
            'error': {
                'type': 'RequestError',
                'message': f"Habanero library request error: {str(e)}"
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
# </Habanero Initialization>

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
        - `offset`.
        - `publisher`.

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
    publisher: str = data_dict.get('publisher')

    print(f"Search query received: {query} - Offset: {offset}")
    if publisher != None:
        print(f"Publisher received: {publisher}")
    # </Parse json data>

    # <Send query to Habanero>
    results_str: str = habanero_query(query, publisher, offset)
    print(f"Raw results from habanero_query: \n{results_str}")
    # </Send query to Habanero>

    # <Send the Habanero result>
    parsed_output: dict = json.loads(results_str)

    if 'error' in parsed_output:
        emit("search_results", { 'results': None }, to=request.sid)
        emit("search_error", json.loads(results_str), to=request.sid)
    else:
        emit("search_results", { 'results': results_str }, to=request.sid)
    # </Send the Habanero result>

@socketio.on("disconnect")
def disconnected():
    """event listener when client disconnects to the backend"""
    print(f'client number {request.sid} is disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True, host=FRONTEND_HOST, port=BACKEND_PORT)

