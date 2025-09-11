from generic_app import Service

import re
import json

from pyalex import config
#from pyalex import Authors, Sources, Institutions, Topics, Publishers, Funders
from pyalex import Works

class OpenAlexClient(Service):
    def __init__(self, apiurl: str = None, apikey: str = None,
                 mailto: str = None, timeout: int = 20):
        """
        There is:

        ```python
        PYALEX_MAILTO=<mail@gmail.com>
        ```

        There is not a *timeout* variable. However, there is a *max_retries*
            variable which is set to 0 in this project.
        """

        self.name = "PyAlex(OpenAlex)"
        super().__init__(apiurl=apiurl, apikey=apikey,
                         mailto=mailto, timeout=timeout)

        config.email = mailto
        config.max_retries = 0
        config.retry_backoff_factor = 0.1
        config.retry_http_codes = [429, 500, 503]

    def query(self, query: str) -> dict[str, str | dict]:
        """
        :param query: `Title, author, DOI, ORCID iD, etc..`
        :return: the result of ``pyalex.Works['query']``.
                 It retrieves one publication at a time.

        This is parsed in the *Crossref Style*.

        The "TL;DR" (generated abstract by Openalex)
            is set to 1300 characters max.

        Example:

        ```json
        {
            "title": [
                "PROBABILISTIC GRAPH GRAMMARS"
            ],
            "abstract": null,
            "TL;DR": "In a probabilistic graph grammar, ...",
            "DOI": "10.3233/fi-1996-263406",
            "URL": "https://doi.org/10.3233/fi-1996-263406",
            "OPENALEX": "https://openalex.org/W35991460",
            "type": "journal-article",
            "ISSN": [
                "0169-2968",
                "1875-8681"
            ],
            "publisher": "IOS Press",
            "publication_date": "1996-01-01",
            "container-title": [
                "Fundamenta Informaticae"
            ],
            "container-url": [
                "https://doi.org/10.3233/fi-1996-263406"
            ],
            "author": [
            {
                "given": "Mohamed",
                "family": "Mosbah",
                "ORCID": "https://orcid.org/0000-0001-6031-4237",
                "OPENALEX": "https://openalex.org/A5067540221",
                "affiliation": [
                {
                    "name": "Laboratoire Bordelais de Recherche en Informatique",
                    "openalex": "https://openalex.org/I4210142254",
                    "ror": "https://ror.org/03adqg323",
                    "country": "FR"
                },
                {
                    "name": "Institut Polytechnique de Bordeaux",
                    "openalex": "https://openalex.org/I4210160189",
                    "ror": "https://ror.org/054qv7y42",
                    "country": "FR"
                },
                {
                    "name": "Université de Bordeaux",
                    "openalex": "https://openalex.org/I15057530",
                    "ror": "https://ror.org/057qpr032",
                    "country": "FR"
                }
                ]
            }
            ],
            "reference": [
            {
                "key": 1,
                "OPENALEX": "https://openalex.org/W2962838298"
            }
            ],
            "related": [
            {
                "key": 1,
                "OPENALEX": "https://openalex.org/W4391375266"
            },
            {
                "key": 2,
                "OPENALEX": "https://openalex.org/W3002753104"
            }
            ],
            "topics": [
            {
                "id": "https://openalex.org/T10181",
                "display_name": "Natural Language Processing Techniques",
                "score": 0.9998,
                "subfield": {
                    "id": "https://openalex.org/subfields/1702",
                    "display_name": "Artificial Intelligence"
                },
                "field": {
                    "id": "https://openalex.org/fields/17",
                    "display_name": "Computer Science"
                },
                "domain": {
                    "id": "https://openalex.org/domains/3",
                    "display_name": "Physical Sciences"
                }
            }
            ],
            "keywords": [],
            "concepts": [
            {
                "id": "https://openalex.org/C49937458",
                "wikidata": "https://www.wikidata.org/wiki/Q2599292",
                "display_name": "Probabilistic logic",
                "level": 2,
                "score": 0.7071239
            }
            ],
            "sustainable_development_goals": [],
            "abstract_inverted_index": {
                "In": [
                    0
                ],
                "a": [
                    1,
                8,
                15,
                34
                ],
                "probabilistic": [
                    2,
                35
                ],
                "graph": [
                    3
                ],
                "grammar,": [
                    4
                ]
            }
        }
        ```
        """

        def func_query(query: str) -> dict[str, str | dict]:
            w = Works()
            result = w[query]

            # ! Do not consider if they <don't have DOI's>...
            if result != None and result.get('doi') == None:
                return self.parse_single(None, None)
            # </don't have DOI's>

            return self.parse_single(result, result['abstract'])

        return self.generic_query(func_query, query)

    def query_filter_doi(self, query_filter: str)\
                                                -> list[dict[str, str | dict]]:
        """
        :param query: A concatenation of DOI such as `"DOI1|DOI2|DOI3"`.
            see the official doc of *pyalex* on Work filters.

        :return: the result of ``pyalex.Works().filter(query_filter).get()``,
            but parsed to in the *Crossref Style*.
                 It can retrieve various publications at a time.

        """

        def func_query(query_filter: str) -> list[dict[str, str | dict]]:
            w = Works()
            publications: list[dict] =\
                w.filter(doi=query_filter).get()

            results: list[dict[str, str | dict]] = []

            for publication in publications:

                # ! Do not consider if they <don't have DOI's>...
                if publication.get('doi', None) != None:
                    current_result: dict =\
                        self.parse_single(publication, publication['abstract'])
                    results.append(current_result)

            if results == {}:
                return self.parse_single(None, None)
            return results

        return self.generic_query(func_query, query_filter)

    def query_filter_orcid(self, query_filter: str)\
                                                -> list[dict[str, str | dict]]:
        """
        :param query: A concatenation of ORCID IDs such as `"ORCID1|ORCID2|ORCID3"`.
            see the official doc of *pyalex* on Work filters.

        :return: the result of ``pyalex.Works().filter(query_filter).get()``,
            but parsed to in the *Crossref Style*.
                 It can retrieve various publications at a time.

        """

        def func_query(query_filter: str) -> list[dict[str, str | dict]]:
            w = Works()
            publications: list[dict] =\
                w.filter(**{"authorships.author.orcid": query_filter}).get()

            results: list[dict[str, str | dict]] = []

            for publication in publications:

                # ! Do not consider if they <don't have DOI's>...
                if publication.get('doi', None) != None:
                    current_result: dict =\
                        self.parse_single(publication, publication['abstract'])
                    results.append(current_result)

            if results == {}:
                return self.parse_single(None, None)
            return results

        return self.generic_query(func_query, query_filter)

    def parse_single(self, publication: dict, TLDR: str = "")\
                                                    -> dict[str, str | dict]:
        """
        :param publication: a single json file for this publication,
            in the *Openalex Style*.
        :param TLDR: sometimes *OpenAlex* could generate the abstract,
            which I call a "TL;DR".

        :return: the json file but parsed in the *Crossref* style.

            The references are not returned otherwise the *json* file returned
                will be too long and it will require more disk space.
            A publication could have up to 50 references (max set by Openalex),
                and it is usually the case.
        """

        if (publication == None):
            return {}

        # <Human Readable>
        title: list[str] = [ publication.get("title") ]
        abstract: str = None
        TLDR_parsed: str = None
        if TLDR != None:
            TLDR_parsed: str = TLDR[:1300] + ' ...'
        # </Human Readable>

        # <Identifiers>
        DOI: str = publication.get("doi", "").removeprefix("https://doi.org/")
        URL: str = publication.get("doi")
        OPENALEX: str = publication.get("id")
        # </Identifiers>

        # <Publisher>
        TYPE: str = publication.get("type_crossref", publication.get("type"))

        source = publication.get("primary_location", {}).get("source", {})
        if source == None or source == {}:
            ISSN: str = None
            publisher: str = None
            container_title: str = None

        else:
            ISSN: str = source.get("issn", [])
            container_title: list[str] = [
                source.get("display_name"),
            ]
            publisher: str = source.get("host_organization_name")


        container_url: list[str] = [
                publication.get("primary_location", {}).get("landing_page_url")
            ]
        publication_date: str = publication.get("publication_date", "")
        # </Publisher>

        # <People>
        author: list[dict] = extract_author_data(
            publication.get("authorships", [])
        )
        # </People>

        # <Similarities>
        reference: list[dict] = [
                {"key": i + 1, "OPENALEX": ref}\
                for i, ref in enumerate(publication.get("referenced_works", []))
            ]
        related: list[dict] = [
                {"key": i + 1, "OPENALEX": ref}\
                for i, ref in enumerate(publication.get("related_works", []))
            ]
        # </Similarities>

        # <Keywords>
        topics: list[dict] = publication.get("topics", [])
        keywords: list[dict] = publication.get("keywords", [])
        concepts: list[dict] = publication.get("concepts", [])
        # </Keywords>

        # <Miscellenaous>
        sustainable_development_goals: list[dict] =\
            publication.get("sustainable_development_goals", [])

        abstract_inverted_index: list[dict] =\
            publication.get("abstract_inverted_index", {})
        # </Miscellenaous>

        crossref_style = {
            "title": title,
            "abstract": abstract,
            "TL;DR": TLDR_parsed,
            "DOI": DOI,
            "URL": URL,
            "OPENALEX": OPENALEX,
            "type": TYPE,
            "ISSN": ISSN,
            "publisher": publisher,
            "publication_date": publication_date,
            "container-title": container_title,
            "container-url": container_url,
            "author": author,
            "reference": [], # Increases the size of the json file.
            "related": related,
            "topics": topics,
            "keywords": keywords,
            "concepts": concepts,
            "sustainable_development_goals": sustainable_development_goals,
            "abstract_inverted_index": abstract_inverted_index,
        }

        return crossref_style

#############################################################################
# Some parsing functions from *OpenAlex* style to *Crossref* style.
#############################################################################

def extract_author_data(authorships: list[dict]) -> list[dict]:
    """
    :param authorships: What *Openalex* returns for the authors.
    :return: *authorships* but in the *Crossref style*.

    Example:
        Author names:
        `raw_author_name` (Openalex) -->
                [ `given_names`, `family_name` ] (Crossref style)

        Affiliations:
        `display_name` (Openalex) --> `name` (Crossref style)
        `country_code` (Openalex) --> `country` (Crossref style)
    """
    authors: list[dict] = []

    for author in authorships:
        # <For the name> "Ahmed Toufik" --> "Ahmed", "Toufik".
        name_parts: list[str] = author["raw_author_name"].split(' ')
        given_names: str = " ".join(name_parts[:-1])
        family_name: str = name_parts[-1]
        # </For the name>

        # <IDs>
        orcid: str = author.get("author", {}).get("orcid") # Url.
        openalex: str = author.get("author", {}).get("id") # Url.
        # </IDs>

        # <Affiliations> *Affiliations* and *Institutions* are almost the same.
        affiliations: list[dict] = []
        for institution in author.get("institutions"):
            affiliations.append({
                'name': institution['display_name'], # str.
                'openalex': institution['id'], # str.
                'ror': institution['ror'], # str.
                'country': institution['country_code'], # str.
            })
        # </Affiliations>

        authors.append({
            "given": given_names,
            "family": family_name,
            "ORCID": orcid,
            "OPENALEX": openalex,
            "affiliation": affiliations
        })

    return authors

