import socketio
import json
import csv
import pandas as pd
import os
import random

import config
import functions
from Labelliser import Labelliser

file_csv: str = 'request/european_transport_from_2018/works-2025-09-02T18-08-53.csv'
file_output: str = './processing/european_transport_from_2018.json'

sio = socketio.Client()
labellator = Labelliser(processingFilepath=file_output)

@sio.event
def connect():
    print("Connected.")

@sio.event
def disconnect():
    print("Disconnected.")

@sio.on("search_results")
def on_search_results(data):
    print("\n")
    print("Search results received:")

    try:
        publications_str: str = data.get('results', '{}')

        publications: dict = json.loads(publications_str)
        message: dict = publications.get('message', {})
        items: list[dict] = message.get('items', [])

        for i in range(len(items)):
            publication_str: str = json.dumps(items[i])

            print(items[i].get('title', ""))
            labellator.store_publication(publication=publication_str)

            if random.randint(0, 20) == 16:
                labellator.checkpoint_processing()

    except Exception as e:
        labellator.checkpoint_processing()
        print(f'{e}')
        exit(0)

@sio.on("search_error")
def on_search_error(data):
    labellator.checkpoint_processing()
    print("Error from server:")
    print(data)

def construct(inputf: str) -> dict[str, dict[str, str | list[str]]]:
    sio.connect(config.RETRIEVER_URL)

    if not os.path.exists(file_csv):
        print(f'ERROR: {file_csv} not found.')

    try:
        file_csv_df = pd.read_csv(inputf)
        all_dois: list[str] = list(set([
            elt if not pd.isna(elt) else None for elt in file_csv_df.get('doi')
        ]))
        all_dois.remove(None)

        offset: int = 25
        print(f'Number of DOIs found: {len(all_dois)}')

        while len(all_dois) > 0:
            current_dois: list[str] = all_dois[:offset]
            print(f'Current query:\n{current_dois}')
            all_dois = all_dois[offset:]

            query: dict[str] = {
                'query': ' '.join(current_dois),
            }

            sio.emit("search_query", json.dumps(query))
            sio.sleep(3)

        sio.sleep(200)

    except Exception as e:
        labellator.checkpoint_processing()
        print(f'{e}')
        exit(0)

    labellator.checkpoint_processing()
    disconnect()

    return resultJsonDict

if __name__ == '__main__':
    resultJsonDict: dict[str, dict[str, str | list[str]]] =\
        construct(inputf=file_csv)

