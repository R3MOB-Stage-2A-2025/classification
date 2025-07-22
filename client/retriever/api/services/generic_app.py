import httpx
import json

class Service:
    def __init__(self, apiurl: str = None, apikey: str = None,
                 mailto: str = None, timeout: int = 20):
        self.name = "GenericService"

        self._apiurl = apiurl
        self._apikey = apikey
        self._mailto = mailto
        self._timeout = timeout

    def generic_query(self, func_query, query: str) -> dict[str, str | dict]:
        """
        This function is used to handle exceptions over a *query function*
        from an *api*.

        :param func_query: the function from the sub class.
            Example: from `Crossref.query()`:
            ```python
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
            ```

        :param query: The query to give to the function `func_query()`.
        :return: for the example above, something in that format:

        ```python
        {
          "status": "ok",
          "message-type": "work-list",
          "message": {
            "facets": {},
            "total-results": 521699,
            "items": [] # contains publications
          }
        }
        ```
        """
        try:
            return func_query(query)

        except httpx.HTTPStatusError as e:
            print(f'\nHTTPStatusError: {e}\nResponse: {e.response.text}\n')
            name_func: str = func_query.__name__
            name_mod: str= func_query.__module__
            error_payload = {
                'error': {
                    'type': 'HTTPStatusError',
                    'message': f"From {name_func}() in {name_mod}:\
                        {e.response.status_code} {e.response.reason_phrase}",
                    'status_code': e.response.status_code,
                    'details': str(e.response.text)[:200]
                }
            }
            return error_payload

        except Exception as e:
            print(f'\nRuntimeError or other unhandled exception: {e}\n')
            error_payload = {
                'error': {
                    'type': 'ServerError',
                    'message': f"An unexpected error occurred \
                                on the server: {str(e)}"
                }
            }
            return error_payload

