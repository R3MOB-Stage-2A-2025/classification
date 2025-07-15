import socketio
import json

import config
from Labelliser import Labelliser

sio = socketio.Client()
labellator = Labelliser()

@sio.event
def connect():
    print("Connected.")

@sio.event
def disconnect():
    print("Disconnected.")

@sio.on("search_results")
def on_search_results(data):
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
    print("Error from server:")
    print(data)

def main():
    sio.connect(config.RETRIEVER_URL)

    query_data = {
        'query' : 'https://doi.org/10.36227/techrxiv.23979117',
        "offset": 0,
        "limit": 1
    }

    sio.emit("search_query", json.dumps(query_data))
    sio.wait()
    sio.disconnect()

if __name__ == "__main__":
    main()

