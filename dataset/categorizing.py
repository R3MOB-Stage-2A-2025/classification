import socketio
import json
import random

import config
import functions
from Labelliser import Labelliser

# <file path>
filePath: str = "european_transport_from_2018.json"
processingFilepath: str = "./processing/" + filePath
labelledFilePath: str = "./labelled/" + filePath
# </file path>

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

@sio.on("classification_results")
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
        doi: str = results.get('DOI', "")
        print(f'DOI: {doi}')
        print(f'results: {results}')
        # </debug>

        labellator.store_publication(labels=metadata_str)

        if random.randint(0, 20) == 16:
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
    list_dois: list[str] = list(set([ url_doi.removeprefix(base_url)\
                            for url_doi in list_url_dois
                            ]))
    if '' in list_dois:
        list_dois.remove('')

    total_queries = len(list_dois)

    # <debug>
    print(f'All the DOIs found (N={total_queries}): ')
    print(', '.join(list_dois))
    # </debug>

    try:
        for doi in list_dois:
            doi_metadata: dict = metadata.retrieve_data_from_doi(doi)

            if doi_metadata != {}:
                doi_metadata['DOI'] = doi

                query_data: str = json.dumps(doi_metadata)
                sio.emit("dataset_classification", query_data)
                sio.sleep(5)

        while responses_received < total_queries:
            sio.sleep(0.1)

    except Exception as e:
        labellator.checkpoint_processing()
        print(f'{type(e)}: {e}')
        exit(0)

    labellator.checkpoint_processing()
    disconnect()

if __name__ == "__main__":
    main(inputf=processingFilepath)

