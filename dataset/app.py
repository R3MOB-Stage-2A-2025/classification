import socketio
import json

import config
import functions
from Labelliser import Labelliser

sio = socketio.Client()
labellator = Labelliser()

total_queries = 0
responses_received = 0

@sio.event
def connect():
    print("Connected.")

@sio.event
def disconnect():
    print("Disconnected.")

@sio.on("search_results")
def on_search_results(data):
    global responses_received
    responses_received += 1

    print("Search results received:")
    results: dict = json.loads(data.get('results', {}))

    if results.get('status', "ko") == "ok":
        message: dict = results.get('message', {})
        items: dict = message.get('items', [{}])

        publication: dict = items[0]
        print(publication.get('title', ""))

        publication_str: str = json.dumps(publication)
        labellator.store_publication(publication_str)
    else:
        print("None, status==ko")

@sio.on("search_error")
def on_search_error(data):
    global responses_received
    responses_received += 1

    labellator.checkpoint_processing()
    print("Error from server:")
    print(data)

def main():
    sio.connect(config.RETRIEVER_URL)

    url_dois: list[str] =\
        functions.find_dois_dataset('./raw/r3mob_150725.csv')

    total_queries = len(url_dois)

    # <debug>
    print(f'All the DOIS found (N={total_queries}): ')
    print(', '.join(url_dois))
    # </debug>

    for url_doi in url_dois:
        query_data = {
            'query' : url_doi,
            "offset": 0,
            "limit": 1
        }

        sio.emit("search_query", json.dumps(query_data))
        sio.sleep(1)

    while responses_received < total_queries:
        sio.sleep(0.1)

    labellator.checkpoint_processing()
    sio.disconnect()

if __name__ == "__main__":
    main()

