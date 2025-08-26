from generic_app import Service

import re
import json

from habanero import Crossref, RequestError

# <Rate limit>
xrate_limit: str = "X-Rate-Limit-Limit: 25"
xrate_interval: str = "X-Rate-Limit-Interval: 1s"
ua_string: str = xrate_limit + "; " + xrate_interval
# </Rate limit>

class CrossrefClient(Service):
    def __init__(self, apiurl: str = None, apikey: str = None,
                 mailto: str = None, timeout: int = 20):
        """
        There is:

        ```python
        HABANERO_BASEURL=https://api.crossref.org
        HABANERO_APIKEY=<apikey>
        HABANERO_MAILTO=<mail@gmail.com>
        HABANERO_TIMEOUT=15
        ```
        """

        self.name = "Habanero(Crossref)"
        super().__init__(apiurl=apiurl, apikey=apikey,
                         mailto=mailto, timeout=timeout)

        self._cr = Crossref(
            base_url    = apiurl,
            api_key     = apikey,
            mailto      = mailto,
            ua_string   = ua_string,
            timeout     = timeout
        )

    def query(self, query: str, limit: int = 10, client_id: str = None,\
              cursor_max: int = 100, sort: str = "relevance",\
              isRetriever: bool = False) -> list[dict[str, str | dict | int]]:
        """
        :param query: `Title, author, DOI, ORCID iD, etc..`
        :param limit: The maximum number of results for this searching query.
            The default is 20, more will slow the response time.
        :param cursor_max: The maximum number of publications on all pages
            at the same time.
        :param sort: The sorting type. It could be "relevance", "score",
            "deposited", "indexed", "published", "published-print",
            "published-online", "issued", "is-referenced-by-count",
            "references-count".
        See `https://habanero.readthedocs.io/en/latest/modules/crossref.html`.
        :param client_id: This is needed to identify which client is asking
            for the next cursor. It is the SID of the client given by FLASK.
        :param isRetriever: True ==> only returns DOIs and abstracts.
                            False ==> basic search, with all info.
        :return: the result of ``habanero.Crossref.works()``. It is various *json*.
                 the result is a string from `json.dumps()`.

        This is parsed in the *Crossref Style*, sorted by *relevance*
        in *desc* order.

        Example:

        ```python
        {
          "status": "ok",
          "message-type": "work-list",
          "message": {
            "facets": {},
            "total-results": 521699,
            "items": [] # various publications.
          }
        }
        ```

        An item has these keys:

        ```
        [
          "DOI",
          "ISSN",
          "OPENALEX",
          "URL",
          "abstract",
          "author",
          "container-title",
          "container-url",
          "publication_date",
          "publisher",
          "reference",
          "title",
          "type"
        ]
        ```
        """

        filtering: dict = {
            #'type': 'journal-article',
        }

        # <Get ORCID>
        regex_orcid: str = r'^\d{4}-\d{4}-\d{4}-\d{3}[0-9X]$'
        first_orcid: list[str] =\
            re.findall(string=query, pattern=regex_orcid)

        if first_orcid != [] and first_orcid != None:
            filtering['orcid'] = first_orcid[0]
            query = None
        # </Get ORCID>

        # "Don't use *rows* and *offset* in the */works* route.
        # They are very expansive and slow. Use cursors instead."
        offset: float = None
        sample: float = None

        limit = limit # Default is 20

        sort: str = sort
        order: str = "desc"

        facet: str | bool | None = None # "relation-type:5"

        select: list[str] | str | None = [
            "DOI",
            "type",
            "container-title",
            "issn-type",
            "subject",
            "title",
            "abstract",
            "publisher",
            "author",
            "created", # for publication date
            "URL",
            "references-count", # ]
            "reference",        # ] what the publication is citing.
        ]

        if isRetriever:
            select = [
                "DOI",
                "abstract",
            ]

        progress_bar: bool = False

        cursor: str = "*"
        cursor_max: float = cursor_max

        def func_query(query: str) -> list[dict[str, str | dict]]:
            return self._cr.works(
                query = query,
                filter = filtering,
                offset = offset,
                limit = limit,
                sample = sample,
                sort = sort,
                order = order,
                facet = facet,
                select = select,
                cursor = cursor,
                cursor_max = cursor_max,
                progress_bar = progress_bar
            )

        return self.generic_query(func_query, query)

