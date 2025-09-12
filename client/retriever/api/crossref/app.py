from generic_app import Service

import re
import json

from habanero import Crossref, RequestError

# <Rate limit>
xrate_limit: str = "X-Rate-Limit-Limit: 50"
xrate_interval: str = "X-Rate-Limit-Interval: 1s"
ua_string: str = xrate_limit + " " + xrate_interval
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
            at the same time. If it is set to -1, then the cursors
            will not be used.
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

        # "Don't use *rows* and *offset* in the */works* route.
        # They are very expansive and slow. Use cursors instead."
        offset: float = None
        sample: float = None

        limit = limit # Default is 20

        sort: str = sort if sort != "None" else "relevance"
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

        cursor: str = "*" if 0 <= cursor_max else None
        cursor_max: float = cursor_max

        def func_query_cursor(query: str) -> list[dict[str, str | dict]]:
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

        def func_query_no_cursor(query: str)\
                                    -> dict[str, dict[str, str | dict]]:
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
                progress_bar = progress_bar
            )

        if cursor != None:
            return self.generic_query(func_query_cursor, query)

        """ Output example of `func_query_no_cursor()`:

        ```json
        {
          "status": "ok",
          "message-type": "work-list",
          "message-version": "1.0.0",
          "message": {
            "facets": {},
            "total-results": 554,
            "items": [],
            "items-per-page": 100,
            "query": {
              "start-index": 0,
              "search-terms": "jambon"
            }
          }
        }
        ```

        Desired output:

        ```python
        [
            {
              "status": "ok",
              "message-type": "work-list",
              "message-version": "1.0.0",
              "message": {
                "facets": {},
                "total-results": 554,
                "items": [],
                "items-per-page": 10,
                "query": {
                  "start-index": 0,
                  "search-terms": "jambon"
                }
              }
            },
            # ... 10 times.
        ]
        ```

        """

        def wrapper_func_query(query: str) -> list[dict[str, str | dict]]:
            output: dict[str, dict[str, str | dict]] =\
                func_query_no_cursor(query=query)

            result: list[dict[str, str | dict]] = []
            message = output.get("message", {})
            items = message.get('items', [])

            if len(items) == 0:
                return [ output ]

            chunk_size = 10
            for i in range(0, len(items), chunk_size):
                chunk = items[i:i+chunk_size]

                new_json = {
                    "status": output.get("status", "ko"),
                    "message-type": output.get("message-type", None),
                    "message-version": output.get("message-version", None),
                    "message": {
                        "facets": message.get("facets", {}),
                        "total-results": message.get("total-results", 0),
                        "items": chunk,
                        "items-per-page": len(chunk),
                        "query": message.get("query", None),
                    }
                }
                result.append(new_json)

            return result

        return self.generic_query(wrapper_func_query, query)

