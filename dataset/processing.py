import socketio
import json

import config
import functions
from Labelliser import Labelliser

# <file path>
inputFile: str = './raw/r3mob_150725_depth_1.json'
outputFile: str = './processing/data_depth_1.json'
# </file path>

sio = socketio.Client()
#labellator = Labelliser(processingFilepath=config.PROCESSING_FILEPAH)
labellator = Labelliser(outputFile)

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

    print("\n")
    print("Search results received:")
    results: dict = json.loads(data.get('results', {}))

    try:
        message: dict = results.get('message', {})
        items: dict = message.get('items', [{}])

        publication: dict = items[0]
        print(publication.get('title', ""))

        publication_str: str = json.dumps(publication)
        labellator.store_publication(publication_str)

    except Exception as e:
        labellator.checkpoint_processing()
        print(f'{e}')
        exit(0)

@sio.on("search_error")
def on_search_error(data):
    global responses_received
    responses_received += 1

    labellator.checkpoint_processing()
    print("Error from server:")
    print(data)

def r3mob(inputf: str = './raw/data.csv'):
    sio.connect(config.RETRIEVER_URL)

    list_url_openalex: list[str] =\
        functions.find_openalex_dataset(inputf)

    total_queries = len(list_url_openalex)

    # <debug>
    print(f'All the OPENALEX IDs found (N={total_queries}): ')
    print(', '.join(list_url_openalex))
    # </debug>

    try:
        for url_openalex in list_url_openalex:
            query_data = {
                'query' : url_openalex,
                "offset": 0,
                "limit": 1
            }

            sio.emit("search_query", json.dumps(query_data))
            sio.sleep(1)

        while responses_received < total_queries:
            sio.sleep(0.1)

    except Exception as e:
        labellator.checkpoint_processing()
        print(f'{e}')
        exit(0)

    labellator.checkpoint_processing()
    disconnect()

if __name__ == "__main__":
    r3mob(inputf=inputFile)

