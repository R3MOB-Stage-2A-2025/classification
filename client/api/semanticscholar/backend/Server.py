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

SEMANTICSCHOLAR_TIMEOUT: int = int(os.getenv("SEMANTICSCHOLAR_TIMEOUT")) # seconds
SEMANTICSCHOLAR_APIKEY: str = os.getenv("SEMANTICSCHOLAR_APIKEY")
SEMANTICSCHOLAR_APIURL: str = os.getenv("SEMANTICSCHOLAR_APIURL")
# </Retrieve environment variables>

# Semantic Scholar Initialization
import semanticscholar

sch = semanticscholar.SemanticScholar(
    timeout = SEMANTICSCHOLAR_TIMEOUT,
    api_key = SEMANTICSCHOLAR_APIKEY,
    api_url = SEMANTICSCHOLAR_APIURL,
    debug = False, # This parameter seems deprecated.
    retry = False
)

def semanticscholar_query(query: str, limit: int = 10) -> str:
    """
    :param query: `Title, author, DOI, ORCID iD, etc..`
    :param publisher: special parameter to find related publications.
        This parameter is usually the `container-title` of the response.
    :return: the result of ``semanticscholar.sch.get_paper()``. It is various *json*.
             the result is a string from `json.dumps()`.
    """

    query: str = query
    year: str = None
    publication_types: list[str] = None
    open_access_pdf: bool = None

    # See this website: `https://aclanthology.org/venues/`.
    venue: list[str] = None

    fields_of_study: list[str] = None
    fields: list[str] = None
    publication_date_or_year: str = None
    min_citation_count: int = None

    # `limit` must be <= 100.
    limit: int = limit

    # Sort only if `bulk` is actived.
    # If bulk is actived, `limit` is ignored, and returns
    # up to 1000 results on each page.
    bulk: bool = True

    # - *field*: can be paperId, publicationDate, or citationCount.
    # - *order*: can be asc (ascending) or desc (descending).
    sort: str = "citationCount:desc"

    # Retrieve a single paper whose
    # title best matches with the query.
    match_title: bool = False

    # The type of "struct_results" could be:
    # - `semanticscholar.PaginatedResults.PaginatedResults`.
    # - `semanticscholar.Paper.Paper`.
    struct_results = sch.search_paper(
        query = query,
        year = year,
        publication_types = publication_types,
        open_access_pdf = open_access_pdf,
        venue = venue,
        fields_of_study = fields_of_study,
        fields = fields,
        publication_date_or_year = publication_date_or_year,
        min_citation_count = min_citation_count,
        limit = limit,
        bulk = bulk,
        sort = sort,
        match_title = match_title
    )

    if type(struct_results) == semanticscholar.Paper.Paper:
        json_results: dict = struct_results.raw_data
    else:
        json_results: list[dict] = struct_results.raw_data

    print(json_results)
    return ""

#semanticscholar_query("mohamed mosbah")

# <Testing if the abstract is here>
paper_id: str = "" # "10.1109/iccias.2006.294189"
fields: list[str] = None

struct_results: semanticscholar.Paper.Paper = sch.get_paper(
    paper_id = paper_id,
    fields = fields
)

json_results: dict = struct_results.raw_data
print(json_results)
# </Testing if the abstract is here>

# </Semantic Scholar Initialization>

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
        - `limit`.

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

        - a string using `json.stringify()` on `sch.get_paper()`.
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

    # <Send query to Semantic Scholar>
    results_str: str = semanticscholar_query(query, publisher, offset)
    print(f"Raw results from semanticscholar_query: \n{results_str}")
    # </Send query to Semantic Scholar>

    # <Send the Semantic Scholar result>
    parsed_output: dict = json.loads(results_str)

    if 'error' in parsed_output:
        emit("search_results", { 'results': None }, to=request.sid)
        emit("search_error", json.loads(results_str), to=request.sid)
    else:
        emit("search_results", { 'results': results_str }, to=request.sid)
    # </Send the Semantic Scholar result>

@socketio.on("disconnect")
def disconnected():
    """event listener when client disconnects to the backend"""
    print(f'client number {request.sid} is disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True, host=FRONTEND_HOST, port=BACKEND_PORT)

