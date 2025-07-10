import concurrent.futures
from time import sleep
import re
import json

import config

# <Generic API>
import sys
import os

dir_path_current: str = os.path.dirname(os.path.abspath(__file__))
sys.path.append(dir_path_current + "/api/services")
# </Generic API>

from api.openalex.app import OpenAlexClient
from api.semanticscholar.app import SemanticScholarClient
from api.crossref.app import CrossrefClient
#from api.orcid.app import OrcidClient
from api.scopus.app import ScopusClient

class Retriever:
    def __init__(self):
        print("Retriever initializing...")

        self._openalex = OpenAlexClient(
            apiurl  = None,
            apikey  = None,
            mailto  = config.PYALEX_MAILTO,
            timeout = None
        )

        # The developer of this client will internaly replace `net_asyncio`
        # which has unexpected side effects with `flask socketio`.
        # For now, it is not usable.
        #self._semanticscholar = SemanticScholarClient(
            #apiurl  = config.SEMANTICSCHOLAR_APIURL,
            #apikey  = config.SEMANTICSCHOLAR_APIKEY,
            #mailto  = None,
            #timeout = config.SEMANTICSCHOLAR_TIMEOUT
        #)

        self._crossref = CrossrefClient(
            apiurl  = config.HABANERO_APIURL,
            apikey  = config.HABANERO_APIKEY,
            mailto  = config.HABANERO_MAILTO,
            timeout = config.HABANERO_TIMEOUT
        )

        # Its version is not compatible with *Habanero* (Crossref Client).
        #self._orcid = OrcidClient(
            #apiurl  = None,
            #apikey  = None,
            #mailto  = None,
            #timeout = None
        #)

        self._scopus = ScopusClient(
            apiurl  = None,
            apikey  = config.PYBLIOMETRICS_APIKEY,
            mailto  = None,
            timeout = None
        )

        print("Retriever initialized.")

    def threaded_query(self, query: str, offset: int, limit: int) -> str:

        # Detect if the query is actually a concatenation of *DOI*s.
        regex: str = r'10\.\d{4,9}/[\w.\-;()/:]+'
        dois: list[str] = re.findall(regex, query)

        if len(dois) > 0:
            return parse_items([
                self._openalex.query("https://doi.org/" + doi)\
                for doi in dois
            ])
        # </Detect DOIs>

        # <Crossref Query> Just retrieve the *DOI*s and the *abstract*.
        crossref_results: dict = self._crossref.query(query, offset=offset,
                        limit=limit, isRetriever=True)

        total_results: int = crossref_results['message']['total-results']
        # </Crossref Query>

        # <OpenAlex enhances metadata>
        openalex_results: list[str] = []
        for item in crossref_results['message']['items']: # item is a list.
            doi_item: str = item['DOI']
            abstract_item: str = parse_tag(item['abstract'])\
                if 'abstract' in item else None

            openalex_results.append(
                self._openalex.query("https://doi.org/" + doi_item)
            )

            openalex_results[-1]['abstract'] = abstract_item
        # </OpenAlex enhances metadata>

        return parse_items(openalex_results, total_results=total_results)

    def query(self, query: str, offset: int, limit: int) -> str:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future = executor.submit(self.threaded_query, query, offset, limit)
            result: str = future.result(timeout=25)
            return result

#############################################################################
# Some functions to parse the results, need a specific json format.
#############################################################################

def parse_items(publications: list[str], total_results: int = 0) -> str:
    """
    :param publication: a list of json files, each is a publication.
    :return: a json file but parsed in the *Crossref* style.
    """
    if len(publications) >= 1 and 'error' in publications[0]:
        return publications[0]

    crossref_style = {
        "status": "ok",
        "message-type": "work-list",
        "message": {
            "facets": {},
            "total-results": max(total_results, len(publications)),
            "items": publications,
        }
    }

    return json.dumps(crossref_style)

def parse_tag(textraw: str) -> str:
    """
    :param textraw: something that can have tags like ``<jats:p>``.
    """
    regex_tags: str = r'</?[^>]+>'
    return re.sub(regex_tags, '', textraw)

#############################################################################

