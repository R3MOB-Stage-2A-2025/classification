from time import sleep
import re
import json

import config

# <If you want to parallelize something>
import concurrent.futures

# Example of code:
#list_queries: list[str] = [ "Example 1", "Example 2" ]

#with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
#    running_tasks = [
#        executor.submit(self.threaded_query, query=query, limit=limit,\
#                    sort=sort, cursor_max=cursor_max, client_id=client_id)
#        for query in list_queries
#    ]

#    # keys: index in the `list_queries` (0, 1, 2 ...).
#    results: dict[str, str] = {}

#    for i in range(len(running_tasks)):
#        current_task = running_tasks[i]
#        current_result: str = current_task.result()

#        if 'error' in current_result:
#            current_result = self.error_payload()

#        results[str(i)] = current_result

#    return results
# </If you want to parallelize something>

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

        # <Cursor Hashmap>, keys: client_id: Flask SID,
        #                   value: ith_cursor | cursor_max.
        self._cursor_hashmap: dict[str, list[dict[str, str | dict]]] = {}

        self._cursor_max_default: int = 50
        self._cursor_max_hashmap: dict[str, int] = {}

        # For each element, a value of
        #   - 0 means no metadata has been retrieved.
        #   - 1 means Crossref metadata has been retrieved.
        #   - 2 means both Crossref and OpenAlex metadata have been retrieved.
        self._cursor_status: dict[str, list[int]] = {}
        # </Cursor Hashmap>

        print("Retriever initialized.")

    def _threaded_query(self, query: str, limit: int = 10, sort: str = None,\
                       cursor_max: int = None, client_id: str = None) -> str:

        # Detect if the query is actually a concatenation of *DOI*s.
        regex: str = r'10\.\d{4,9}/[\w.\-;()/:]+'
        dois: list[str] = re.findall(regex, query)

        if len(dois) > 0:
            query_filter: str = '|'.join(dois)
            results: list[dict[str, str | dict]] =\
                self._openalex.query_filter(query_filter)

            return json.dumps(parse_items(results, total_results=len(dois)))
        # </Detect DOIs>

        # <Crossref Query> Just retrieve the *DOI*s and the *abstract*.
        cursor_max = self._cursor_max_default\
            if cursor_max == None or 200 < cursor_max else cursor_max

        crossref_results: list[dict] | dict =\
            self._crossref.query(query=query, limit=limit, sort=sort,\
                                 client_id=client_id, isRetriever=True,\
                                 cursor_max=cursor_max)

        # Here, crossref_results is a dict only if there is an error.
        if 'error' in crossref_results:
            return json.dumps(crossref_results)

        self._cursor_hashmap[client_id] = crossref_results
        self._cursor_status[client_id] =\
            [ 1 for i in range(len(crossref_results)) ]
        self._cursor_max_hashmap[client_id] =\
            min(self._cursor_max_default, len(crossref_results))
        # </Crossref Query>

        # <For id_cursor=0> i.e the first page.
        id_cursor: int = 0
        crossref_results_cursor: dict[str, str | dict] =\
            crossref_results[id_cursor]
        # </For id_cursor=0>

        # <OpenAlex enhances metadata> for id_cursor=0
        openalex_results: dict[str, str | dict] =\
            self._openalex_enhance_metadata(crossref_results_cursor)
        # </OpenAlex enhances metadata>

        # <Add the current query to the cache hashmap>
        enhanced_results_for_cursor: list[dict] =\
            [ openalex_results ] + crossref_results[1:]

        self._cursor_hashmap[client_id] = enhanced_results_for_cursor

        list_status_current: list[int] = self._cursor_status[client_id]
        list_status_current[id_cursor] = 2
        # </Add the current query to the cache hashmap>

        return json.dumps(enhanced_results_for_cursor[id_cursor])

    def _openalex_enhance_metadata(self,\
          crossref_results: dict[str, str | dict]) -> dict[str, str | dict]:
        """
        Something that enhance the metadatas using *Openalex*.

        :param crossref_results: given by
            `self._crossref.query(isRetriever=True)`.
        :return: More metadata in the *Crossref style*.
        """

        message : dict = crossref_results.get('message', {})
        total_results: int = message.get('total-results', 0)
        items: list[dict] = message.get('items', [])

        # <Retrieve all DOI's>, in the right order.
        list_doi: list[str] =\
            [ item.get('DOI', None) for item in items ]
        list_abstract: list[str] = [
            parse_tag(item['abstract']) if 'abstract' in item else None\
            for item in items
        ]
        # </Retrieve all DOI's>

        # <Enhance with openalex>
        query_filter: str = '|'.join(list_doi)
        openalex_results: list[dict[str, str | dict]] =\
            self._openalex.query_filter(query_filter)
        # </Enhance with openalex>

        # <Add the abstracts if necessary>
        for i in range(len(list_abstract)):
            if i < len(openalex_results):
                current_result: dict[str, str | dict] =\
                    openalex_results[i]

                if current_result.get('abstract', None) == None:
                    current_result['abstract'] =\
                        list_abstract[i]
        # </Add the abstracts if necessary>

        return parse_items(openalex_results, total_results=total_results)

    def query(self, query: str, limit: int, sort: str, cursor_max: int,\
                                                client_id: str = None) -> str:

        return self._threaded_query(query=query, limit=limit, sort=sort,
                                    cursor_max=cursor_max, client_id=client_id)

    def query_openalex(self, query: str) -> str:
        """
                                Only uses openalex.
        ! `query` must be a *DOI URL* or a *OPENALEX Work ID* (only one ID). !

        example: `"https://openalex.org/W1989375655"`.
        Returns something in the crossref style (json.dumps()).
        """

        openalex_result: dict[str, str | dict] = self._openalex.query(query)
        return json.dumps(parse_items([openalex_result], total_results=1))

    def query_cursor(self, client_id: str = None,\
                                    id_cursor: int = 0) -> str:
        """
        :param client_id: the Flask SID of the client.
        :param id_cursor: the id_cursor that should exist.
            By default, the max_cursor is `self._cursor_max_default`.

        Modifies the cache hashmap, and returns the associated page.
            id_cursor == 0 ==> page == 1, id_cursor == 1, page == 2, etc...
        """

        if id_cursor < self._cursor_max_hashmap.get(client_id, 0):
            results_current: list[dict] =\
                self._cursor_hashmap.get(client_id, [])

            # <If already done>, this is cache.
            list_status_current: list[int] =\
                self._cursor_status.get(client_id, [])

            if 0 <= id_cursor and id_cursor <= len(results_current) - 1:
                if list_status_current[id_cursor] == 2:
                    return json.dumps(results_current[id_cursor])
            # </If already done>

            if 0 <= id_cursor and id_cursor <= len(results_current) - 1:
                # <OpenAlex enhances metadata> for id_cursor=0
                openalex_results: dict[str, str | dict] =\
                    self._openalex_enhance_metadata(results_current[id_cursor])
                # </OpenAlex enhances metadata>

                # <Add the current query to the cache hashmap>
                current_results: list[dict] =\
                    self._cursor_hashmap.get(client_id, [])

                enhanced_results_for_cursor: list[dict] = current_results
                enhanced_results_for_cursor[id_cursor] = openalex_results

                self._cursor_hashmap[client_id] = enhanced_results_for_cursor

                list_status_current: list[int] = self._cursor_status[client_id]
                list_status_current[id_cursor] = 2
                # </Add the current query to the cache hashmap>

                return json.dumps(enhanced_results_for_cursor[id_cursor])

        raise Exception(f'No result found for the cursor={id_cursor} !')
        return ""

    def clear_cache_hashmap(self, client_id: str = None) -> None:
        """
        On disconnection from the FLASK server of `client_id`,
        this method is called to clear the cache generated by this client.

        :param client_id: the FLASK sid of the client, also the key in the
            hashmap of the query. Usually, 1 query <==> 1 client.
        """

        if client_id in self._cursor_hashmap:
            self._cursor_hashmap.pop(client_id)

        if client_id in self._cursor_max_hashmap:
            self._cursor_max_hashmap.pop(client_id)

        if client_id in self._cursor_status:
            self._cursor_status.pop(client_id)

#############################################################################
# Some functions to parse the results, need a specific json format.
#############################################################################

def parse_items(publications: list[dict[str, str | dict]],\
                            total_results: int = 0) -> dict[str, str | dict]:
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

    return crossref_style

def parse_tag(textraw: str) -> str:
    """
    :param textraw: something that can have tags like ``<jats:p>``.
    """
    if textraw != None:
        regex_tags: str = r'</?[^>]+>'
        return re.sub(regex_tags, '', textraw)

#############################################################################

