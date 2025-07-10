from generic_app import Service

import re
import json

from habanero import Crossref, RequestError

xrate_limit: str = "" "X-Rate-Limit-Limit: 100"
xrate_interval: str = "" "X-Rate-Limit-Interval: 1s"
ua_string: str = xrate_limit + ";" + xrate_interval

class CrossrefClient(Service):
    def __init__(self, apiurl: str = None, apikey: str = None,
                 mailto: str = None, timeout: int = 20):

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
        :param isRetriever: True ==> only returns DOIs and abstracts.
                            False ==> basic search, with all info.
        :return: the result of ``habanero.Crossref.works()``. It is various *json*.
                 the result is a string from `json.dumps()`.
        """

        filtering: dict = {
            #'type': 'journal-article',
        }

        # "Don't use *rows* and *offset* in the */works* route.
        # They are very expansive and slow. Use cursors instead."
        offset = offset

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
        #   - the *issn-value*: is too generic. (ex: "Electronic")
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

        def func_query(query: str) -> str:
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

