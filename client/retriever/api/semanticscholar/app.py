from generic_app import Service

import re
import json

import semanticscholar

class SemanticScholarClient(Service):
    def __init__(self, apiurl: str = None, apikey: str = None,
                 mailto: str = None, timeout: int = 20):

        self.name = "SemanticScholar"
        super().__init__(apiurl=apiurl, apikey=apikey,
                         mailto=mailto, timeout=timeout)

        self._sch = semanticscholar.SemanticScholar(
            timeout = timeout,
            api_key = apikey,
            api_url = apiurl,
            debug   = False, # This parameter seems deprecated.
            retry   = False # This parameter could overuse the thread.
        )

    def query_paper(self, query: str, limit: int = 10) -> str:
        """
        :param query: `Title, author, DOI, ORCID iD, etc..`
        :return: the result of ``semanticscholar.sch.get_paper()``. It is various *json*.
                 the result is a string from `json.dumps()`.
        """

        query: str = query
        year: str = None
        publication_types: list[str] = None
        open_access_pdf: bool = None

        # See this website: `https://aclanthology.org/venues/`.
        venue: list[str] = None

        fields_of_study: list[str] = None
        fields: list[str] = None
        publication_date_or_year: str = None
        min_citation_count: int = None

        # `limit` must be <= 100.
        limit: int = limit

        # Sort only if `bulk` is actived.
        # If bulk is actived, `limit` is ignored, and returns
        # up to 1000 results on each page.
        bulk: bool = True

        # - *field*: can be paperId, publicationDate, or citationCount.
        # - *order*: can be asc (ascending) or desc (descending).
        sort: str = "citationCount:desc"

        # Retrieve a single paper whose
        # title best matches with the query.
        match_title: bool = False

        # The type of "struct_results" could be:
        # - `semanticscholar.PaginatedResults.PaginatedResults`.
        # - `semanticscholar.Paper.Paper`.
        struct_results = self._sch.search_paper(
            query = query,
            year = year,
            publication_types = publication_types,
            open_access_pdf = open_access_pdf,
            venue = venue,
            fields_of_study = fields_of_study,
            fields = fields,
            publication_date_or_year = publication_date_or_year,
            min_citation_count = min_citation_count,
            limit = limit,
            bulk = bulk,
            sort = sort,
            match_title = match_title
        )

        if type(struct_results) == semanticscholar.Paper.Paper:
            json_results: dict = struct_results.raw_data
        else:
            json_results: list[dict] = struct_results.raw_data

        return json.dumps(json_results)

    def semanticscholar_paper(self, paper_id: str) -> str:
        """
        :param paper_id: `DOI, ORCID iD, etc..`
        :return: the result of ``semanticscholar.sch.get_paper()``.
        It is various *json*. The result is a string from `json.dumps()`.
        """

        paper_id: str = paper_id

        fields: list[str] = None

        # The type of "struct_results" is:
        #   `semanticscholar.Paper.Paper`.
        struct_results = self._sch.get_paper(
            paper_id = paper_id,
            fields = fields
        )

        json_results: dict = struct_results.raw_data
        return json.dumps(json_results)

    def query(self, query: str, limit: int = 10) -> str:
        """
        :param query: `author, ORCID iD, etc..`
        :return: the result of ``semanticscholar.sch.search_author()``.
        It is various *json*. The result is a string from `json.dumps()`.
        """

        query: str = query

        fields: list[str] = None

        # `limit` must be <= 100.
        limit: int = limit

        # The type of "struct_results" is:
        #   `semanticscholar.PaginatedResults.PaginatedResults`.
        struct_results = self._sch.search_paper(
            query = query,
            fields = fields,
            limit = limit
        )

        json_results: list[dict] = struct_results.raw_data
        return json.dumps(json_results)

    def semanticscholar_recommendations(self, paper_id: str, limit: int = 10) -> str:
        """
        :param paper_id: `DOI, ArXivId, URL(not all URL)`.
        :return: the result of ``semanticscholar.sch.get_recommended_papers()``.
        It is various *json*. The result is a string from `json.dumps()`.
        """

        paper_id: str = paper_id

        fields: list[str] = None

        # `limit` must be <= 100.
        limit: int = limit

        # Choose between "recent" and "all-cs".
        pool_from: str = "recent"

        # The type of "struct_results" is:
        #   `list[semanticscholar.Paper.Paper]`.
        struct_results = self._sch.get_recommended_papers(
            paper_id = paper_id,
            fields = fields,
            limit = limit,
            pool_from = pool_from
        )

        json_results: list[str] = [ paper.raw_data for paper in struct_results ]
        return json.dumps(json_results)

    def semanticscholar_citations(self, paper_id: str, limit: int = 50) -> str:
        """
        :param paper_id: `DOI, ArXivId, URL(not all URL)`.
        :return: the result of ``semanticscholar.sch.get_paper_citations()``.
        It is various *json*. The result is a string from `json.dumps()`.
        """

        paper_id: str = paper_id

        fields: list[str] = None

        # `limit` must be <= 100.
        limit: int = limit

        # The type of "struct_results" is:
        #   `semanticscholar.PaginatedResults.PaginatedResults`.
        struct_results = self._sch.get_paper_citations(
            paper_id = paper_id,
            fields = fields,
            limit = limit
        )

        json_results: list[str] = struct_results.raw_data
        return json.dumps(json_results)

    def semanticscholar_references(self, paper_id: str, limit: int = 50) -> str:
        """
        :param paper_id: `DOI, ArXivId, URL(not all URL)`.
        :return: the result of ``semanticscholar.sch.get_paper_references()``.
        It is various *json*. The result is a string from `json.dumps()`.
        """

        paper_id: str = paper_id

        fields: list[str] = None

        # `limit` must be <= 100.
        limit: int = limit

        # The type of "struct_results" is:
        #   `semanticscholar.PaginatedResults.PaginatedResults`.
        struct_results = self._sch.get_paper_references(
            paper_id = paper_id,
            fields = fields,
            limit = limit
        )

        json_results: list[str] = struct_results.raw_data
        return json.dumps(json_results)

