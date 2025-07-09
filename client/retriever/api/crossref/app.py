# <Import the generic api class>
import os
import sys

dir_path_current: str = os.path.dirname(os.path.abspath(__file__))
sys.path.append(dir_path_current)
sys.path.append(
    dir_path_current.removesuffix("/crossref") + \
    "/services")

from generic_app import Service
# </Import the generic api class>

import re
import httpx
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

    def generic_habanero_output(self, results: dict[str, dict] | list) -> dict[str, dict]:
        """
        Imagine if a single publication is retrieved, there is no "items".
        I want `results['message']['items']` to be here to be more generic.

        :param results: something returned by `cr.works()`.
        Besides, if there were multiple `ids`, `cr.works()` returns a list. WTF.

        :return: results but it is sure that `result['message']['items']` exists.
        """

        def genericity(result: dict[str, dict]) -> dict[str, dict]:
            generic_result: dict[str, dict] = result

            if 'message' in result and 'items' not in result['message']:
                generic_result = {
                    'message': {
                        'items': [ result['message'] ]
                    }
                }

            return generic_result

        if not type(results) == list:
            return genericity(results)

        # Habanero returns a list if multiple DOI's were given...
        generic_results: dict[str, dict] = genericity(results[0])
        for result in results[1:]:
            generic_results['message']['items'].append(result['message'])

        return generic_results

    def generic_dates(self, results: dict[str, dict]) -> dict[str, dict]:
        """
        :param: something returned by `cr.works()`.
        This something is not an error. It contains `results['message']['items']`.

        Something with this type of date: `YYYY-MM-DD`.
        """
        results_with_better_date: dict[str, dict] = results

        for item in results_with_better_date['message']['items']:
            if 'created' in item and 'date-parts' in item['created']:
                date_parts = item['created']['date-parts'][0]

                # Format date as YYYY-MM-DD for consistency and easier sorting
                item['publication_date'] = \
                    f"{date_parts[0]:04d}-{date_parts[1]:02d}-{date_parts[2]:02d}"

        return results_with_better_date

    def query(self, query: str, publisher: str = None, offset: int = 0, limit: int = 10) -> str:
        """
        :param query: `Title, author, DOI, ORCID iD, etc..`
        :param publisher: special parameter to find related publications.
            This parameter is usually the `container-title` of the response.
        :return: the result of ``habanero.Crossref.works()``. It is various *json*.
                 the result is a string from `json.dumps()`.
        """
        # Detect if the query is actually a concatenation of *DOI*s.
        regex: str = r'10\.\d{4,9}/[\w.\-;()/:]+'
        ids: list[str] = re.findall(regex, query)

        filtering: dict = {
            #'type': 'journal-article',
        }

        # TODO: this thing does not work I don't know why.
        if publisher != None:
            filtering['container-title'] = publisher
        # </TODO>

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

        # TODO: add cursors on the *frontend*.
        cursor: str = "*"
        cursor: str = None # Cursor can't be combined with *offset* or *sample*.
        cursor_max: float = 10
        # <TODO>

        progress_bar: bool = False

        try:
            if len(ids) > 0:
                return json.dumps(self.generic_dates(self.generic_habanero_output(
                            self._cr.works(ids=ids)
                        )))

            return json.dumps(self.generic_dates(self.generic_habanero_output(
                        self._cr.works(
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
                    )))

        except httpx.HTTPStatusError as e:
            print(f'\nHTTPStatusError: {e}\nResponse: {e.response.text}\n')
            error_payload = {
                'error': {
                    'type': 'HTTPStatusError',
                    'message': f"Crossref API request failed:\
                            {e.response.status_code} {e.response.reason_phrase}",
                    'status_code': e.response.status_code,
                    'details': str(e.response.text)[:200]
                }
            }
            return json.dumps(error_payload)

        except RequestError as e:
            print(f'\nRequestError: {e}\n')
            error_payload = {
                'error': {
                    'type': 'RequestError',
                    'message': f"Habanero library request error: {str(e)}"
                }
            }
            return json.dumps(error_payload)

        except Exception as e:
            print(f'\nRuntimeError or other unhandled exception: {e}\n')
            error_payload = {
                'error': {
                    'type': 'ServerError',
                    'message': f"An unexpected error occurred on the server: {str(e)}"
                }
            }
            return json.dumps(error_payload)

