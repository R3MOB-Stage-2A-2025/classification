from generic_app import Service

import re
import json

from pyalex import config
#from pyalex import Works, Authors, Sources, Institutions, Topics, Publishers, Funders
from pyalex import Works

class OpenAlexClient(Service):
    def __init__(self, apiurl: str = None, apikey: str = None,
                 mailto: str = None, timeout: int = 20):

        self.name = "PyAlex(OpenAlex)"
        super().__init__(apiurl=apiurl, apikey=apikey,
                         mailto=mailto, timeout=timeout)

        config.email = mailto
        config.max_retries = 0
        config.retry_backoff_factor = 0.1
        config.retry_http_codes = [429, 500, 503]

    def query(self, query: str) -> str:
        """
        :param query: `Title, author, DOI, ORCID iD, etc..`
        :return: the result of ``pyalex.Works['query']``.
                 the result is a string from `json.dumps()`.
                 It retrieves one publication at a time.
        """

        def func_query(query: str) -> str:
            w = Works()
            result = w[query]
            return self.parse_single(result, result['abstract'])

        return self.generic_query(func_query, query)

    def parse_single(self, publication: str, TLDR: str = "") -> dict[str, str | dict]:
        """
        :param publication: a single json file for this publication.
        :param TLDR: sometimes *OpenAlex* could generate the TLDR.
        :return: the json file but parsed in the *Crossref* style.
        """

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
            "reference": reference,
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

