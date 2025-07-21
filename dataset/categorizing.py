import socketio
import json

import config
import functions
from Labelliser import Labelliser

filePath: str = "data.json"
processingFilepath: str = "./processing/" + filePath
labelledFilePath: str = "./labelled/" + filePath

sio = socketio.Client()
metadata = functions.MetadataRetriever(processingFilepath)
labellator = Labelliser(labelledFilePath)

total_queries = 0
responses_received = 0

@sio.event
def connect():
    print("Connected.")

@sio.event
def disconnect():
    print("Disconnected.")

@sio.on("dataset_classification_results")
def on_search_results(data):
    global responses_received
    responses_received += 1

    print("\n")
    print("Classification results received:")
    results: dict = data

    try:
        metadata_str: str = json.dumps(results)

        # <debug>
        print("\n")
        print(f'DOI: {results.get('DOI', "")}')
        print(f'results: {results}')
        # </debug>

        labellator.store_publication(labels=metadata_str)
        labellator.checkpoint_processing()

    except Exception as e:
        labellator.checkpoint_processing()
        print(f'{e}')
        exit(0)

@sio.on("classification_error")
def on_search_error(data):
    global responses_received
    responses_received += 1

    labellator.checkpoint_processing()
    print("Error from server:")
    print(data)

def main(inputf: str = './processing/data.csv'):
    sio.connect(config.CLASSIFIER_URL)

    list_url_dois: list[str] =\
        functions.find_dois_dataset(inputf)

    base_url: str = "https://doi.org/"
    list_dois: list[str] = [ url_doi.removeprefix(base_url)\
                            for url_doi in list_url_dois
                            ]

    total_queries = len(list_dois)

    # <debug>
    print(f'All the DOIs found (N={total_queries}): ')
    print(', '.join(list_dois))
    # </debug>

    try:
        for doi in list_dois:
            if doi == '':
                continue

            doi_metadata: dict = metadata.retrieve_data_from_doi(doi)
            doi_metadata['DOI'] = doi

            query_data: str = json.dumps(doi_metadata)
            sio.emit("dataset_classification", query_data)
            sio.sleep(4)

        while responses_received < total_queries:
            sio.sleep(0.1)

    except Exception as e:
        labellator.checkpoint_processing()
        print(f'{e}')
        exit(0)

    labellator.checkpoint_processing()
    disconnect()

if __name__ == "__main__":
    main(inputf=processingFilepath)

