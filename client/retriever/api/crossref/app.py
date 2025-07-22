from generic_app import Service

import re
import json

from habanero import Crossref, RequestError

# <Rate limit>
xrate_limit: str = "X-Rate-Limit-Limit: 100"
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

    def query(self, query: str, offset: int = 0, limit: int = 10, isRetriever: bool = False) -> dict[str, str | dict | int]:
        """
        :param query: `Title, author, DOI, ORCID iD, etc..`
        :param limit: The maximum number of results for this searching query.
            The default is 20, more will slow the response time.
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
        offset = None # offset

        limit = limit # Default is 20

        sort: str = "relevance"
        order: str = "desc"

        # TODO: find a way to retrieve the publication abstract,
        #       there are too many retrieved publications for which only
        #       the title is public.
        #       Need to recursively retrieve publications from references etc..
        facet: str | bool | None = None # "relation-type:5"
        # </TODO>

        # What could happen:
        #   - the *abstract* is located in the *title* section.
        #   - *subject* is almost never present.
        #   - there could be A LOT of authors. (too many).
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

        # TODO: add cursors on the *frontend*.
        cursor: str = "*"
        cursor: str = None # Cursor can't be combined with *offset* or *sample*.
        cursor_max: float = 10
        # <TODO>

        progress_bar: bool = False

        def func_query(query: str) -> dict[str, str | dict]:
            return  self._cr.works(
                query = query,
                filter = filtering,
                offset = offset,
                limit = limit,
                sort = sort,
                order = order,
                facet = facet,
                select = select,
                cursor = cursor,
                cursor_max = cursor_max,
                progress_bar = progress_bar
            )

        return self.generic_query(func_query, query)

