from time import sleep
import re
import json
import uuid
import rispy
import datetime

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
            if cursor_max == None or 2000 < cursor_max else cursor_max

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

        # <Retrieve current cached results and statuses>
        results_current: list[dict] = self._cursor_hashmap.get(client_id, [])
        list_status_current: list[int] = self._cursor_status.get(client_id, [])
        # </Retrieve current cached results and statuses>

        # <If id_cursor exists in cache>
        if 0 <= id_cursor < len(results_current):
            # <If already done>, this is cache.
            if list_status_current[id_cursor] == 2:
                return json.dumps(results_current[id_cursor])
            # </If already done>

            # <OpenAlex enhances metadata> for this cursor
            openalex_results: dict[str, str | dict] = \
                self._openalex_enhance_metadata(results_current[id_cursor])
            # </OpenAlex enhances metadata>

            # <Add the current query to the cache hashmap>
            results_current[id_cursor] = openalex_results
            self._cursor_hashmap[client_id] = results_current

            list_status_current[id_cursor] = 2
            # </Add the current query to the cache hashmap>

            return json.dumps(openalex_results)
        # </If id_cursor exists in cache>

        raise Exception(f'No result found for the cursor={id_cursor} !')
        return ""

    def convert_from_openalex(self, openalex_item: dict[str, str | dict])\
                                                                    -> str:
        """
        Just a parsing function for the Retriever module.
        See `self._openalex.parse_single()`.
        """

        return json.dumps(parse_items(
            [ self._openalex.parse_single(openalex_item) ], total_results=1
        ))

    def convert_from_ris(self, data: str) -> dict[str, str | dict]:
        """
        Just a parsing function for the Retriever module.

        :param data: The text retrieved with `file.readlines()`.
        :return: The results parsed in the crossref style.

        It uses RISPY.
        """

        # <Write the data in a temporary file>
        filepath: str = config.RISPY_WORKING_FOLDER + str(uuid.uuid4())

        with open(filepath, 'w') as file:
            file.writelines(data)
        # </Write the data in a temporary file>

        # <Read this temporary file>
        results: list[dict] = []
        with open(filepath, 'r') as file:
            results = rispy.load(file)
        # </Read this temporary file>

        # <Delete the temporary file>
        os.remove(filepath)
        # </Delete the temporary file>

        # <Need to parse the Results to the Crossref Style>
        desired_results: list[dict] = []
        for current_result in results:

            current_desired_result: dict = {
                "title": [ current_result.get("title") ],
                "abstract": current_result.get("abstract", None),
                "TL;DR": None,
                "DOI": current_result.get("doi", None),
                "URL": current_result["urls"][0]\
                        if current_result.get("urls") else None,
                "OPENALEX": None,
                "type": "journal-article"\
                        if current_result.get("type_of_reference") == "JOUR"\
                        else None,
                "ISSN": [],
                "publisher": None,
                "publication_date": current_result.get("date", None),
                "container-title": [ current_result.get("secondary_title") ]\
                    if current_result.get("secondary_title", None) else [],
                "container-url": current_result.get("urls", []),
                "author": [],
                "reference": [],
                "related": [],
                "topics": [],
                "keywords": [
                    {"id": None, "display_name": kw, "score": None}
                    for kw in current_result.get("keywords", [])
                ],
                "concepts": [],
                "sustainable_development_goals": [],
                "abstract_inverted_index": None
            }

            # <Add metadatas if possible, when openalex finds it>
            current_openalex_query: dict =\
                json.loads(
                    self.query_openalex(current_desired_result.get("URL", {})))
            current_openalex_message: dict =\
                current_openalex_query.get('message', {})
            current_openalex_items: list[dict]=\
                current_openalex_message.get('items', [{}])
            current_openalex_result: dict = current_openalex_items[0]

            for i, a in enumerate(current_result.get("authors", [])):
                current_desired_result.get("author", []).append(
                    ris_parse_author(
                         a,
                         current_result.get("custom1", {})\
                             if i == 0 else None,
                         current_desired_result.get("author", [])))

            if current_desired_result.get("title", []) == []:
                current_desired_result["title"] =\
                    current_openalex_result.get("title", [])

            if current_desired_result.get("abstract", None) == None:
                current_desired_result["abstract"] =\
                    current_openalex_result.get("abstract", None)

            current_desired_result["TL;DR"] =\
                current_openalex_result.get("TL;DR", None)

            current_desired_result["OPENALEX"] =\
                current_openalex_result.get("OPENALEX", None)

            if current_desired_result.get("type", None) == None:
                current_desired_result["type"] =\
                    current_openalex_result.get("type", None)

            if current_desired_result.get("ISSN", []) == []:
                current_desired_result["ISSN"] =\
                    current_openalex_result.get("ISSN", [])

            if current_desired_result.get("publisher", None) == None:
                current_desired_result["publisher"] =\
                    current_openalex_result.get("publisher", None)

            if current_desired_result.get("publication_date", None) == None:
                current_desired_result["publication_date"] =\
                    current_openalex_result.get("publication_date", None)

            if current_desired_result.get("container-title", []) == []:
                current_desired_result["container-title"] =\
                    current_openalex_result.get("container-title", [])

            if current_desired_result.get("container-url", []) == []:
                current_desired_result["container-url"] =\
                    current_openalex_result.get("container-url", [])

            if current_desired_result.get("abstract_inverted_index",\
                                                                None) == None:
                current_desired_result["abstract_inverted_index"] =\
                    current_openalex_result.get("abstract_inverted_index", None)

            current_desired_result.get("reference", [])\
                            .extend(current_openalex_result.get("reference", []))

            current_desired_result.get("related", [])\
                            .extend(current_openalex_result.get("related", []))

            current_desired_result.get("topics", [])\
                            .extend(current_openalex_result.get("topics", []))

            current_desired_result.get("keywords", [])\
                            .extend(current_openalex_result.get("reference", []))

            current_desired_result.get("keywords", [])\
                            .extend(current_openalex_result.get("keywords", []))

            current_desired_result.get("concepts", [])\
                            .extend(current_openalex_result.get("concepts", []))

            current_desired_result.get("sustainable_development_goals", [])\
                        .extend(
            current_openalex_result.get("sustainable_development_goals", []))
            # </Add metadatas if possible, when openalex finds it>

            desired_results.append(current_desired_result)
        # </Need to parse the Result to the Crossref Style>

        return parse_items(desired_results, total_results=len(desired_results))

    def convert_from_crossref_style_to_ris(self,
                               publication: dict[str, str | dict]) -> str:
        """
        Just a parsing function for the Retriever module.

        :param publication: A publication in the Crossref Style..
        :return: A RIS instance.
        """

        type_map = {
            "journal-article": "JOUR",
            "book-chapter": "CHAP",
            "book": "BOOK"
        }
        type_of_reference: str = type_map.get(publication.get("type"), "GEN")

        authors: list[str] = [ f"{a['family']}, {a['given']}"\
                   for a in publication.get("author", []) ]

        pub_date = publication.get("publication_date", None)
        year = None

        if pub_date:
            try:
                year = datetime.strptime(pub_date, "%Y-%m-%d").strftime("%Y")
            except Exception:
                year = pub_date.split("-")[0]

        ris_entry = {
            "type_of_reference": type_of_reference,
            "title": publication.get("title", [None])[0]\
                    if publication.get("title") else None,
            "year": year,
            "publisher": publication.get("publisher", None),
            "secondary_title": publication.get("container-title", [None])[0]\
                    if publication.get("container-title") else None,
            "date": pub_date,
            "authors": authors,
            "custom1": None,
            "language": "en",
            "keywords": [ kw.get("display_name")\
                         for kw in publication.get("keywords", []) ],
        }

        ris_entry["doi"] = publication.get("DOI", None)
        ris_entry["urls"] = [ publication.get("URL", None) ]

        if publication.get('ISSN'):
            ris_entry["issn"] = publication.get("ISSN")[0]

        return rispy.dumps([ris_entry])

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
# Functions for the RIS format.
#############################################################################

def ris_parse_author(author_str: str, affiliation: list[dict] = None,\
        openalex_author: list[dict] = None) -> dict[str, str | list[dict]]:
    """
    Used by `self.convert_from_ris()`.

    :param author_str: example: "Toufik, Ahmed", from the RIS file.
    :param affiliation: "Institute of Energy Economics, Technical ...",
                    from the RIS file.
    :param openalex_author: The "author" from OPENALEX retriever in the
                            Crossref Style.

    :return: The publication's "author" parsed in the Crossref style.
    """

    parts = [ p.strip() for p in author_str.split(",") ]

    if len(parts) == 2:
        family, given = parts
    else:
        family, given = parts[0], " ".join(parts[1:])

    author_openalex: dict = {}
    for author in openalex_author:
        if author.get('family', "") in family\
                and author.get('given', "") in given:
            author_openalex = author

    affiliation_author: list[dict] = [
            {
                "name": affiliation,
                "openalex": None,
                "ror": None,
                "country": "FR" if affiliation else None
            }
        ] if affiliation else []

    affiliation_openalex: list[dict] = author_openalex.get('affiliation', [])
    for an_affiliation in affiliation_openalex:
        current_name: str = an_affiliation.get('name', "")

        if current_name == affiliation:
            current_openalex: str = an_affiliation.get('openalex', None)
            current_ror: str = an_affiliation.get('ror', None)
            current_country: str = an_affiliation.get('country', None)

            affiliation_author[0]["openalex"] = current_openalex
            affiliation_author[0]["ror"] = current_ror
            affiliation_author[0]["country"] = current_country

    return {
        "given": given,
        "family": family,
        "ORCID": author_openalex.get('ORCID', None),
        "OPENALEX": author_openalex.get('OPENALEX', None),
        "affiliation": affiliation_author,
    }

#############################################################################

