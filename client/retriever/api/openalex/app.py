# <Import the generic api class>
import os
import sys

dir_path_current: str = os.path.dirname(os.path.abspath(__file__))
sys.path.append(dir_path_current)
sys.path.append(
    dir_path_current.removesuffix("/openalex") + \
    "/services")

from generic_app import Service
# </Import the generic api class>

import re
import httpx
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
        :return: the result of ``pyalex.Works.search()``. It is various *json*.
                 the result is a string from `json.dumps()`.
        """
        # Detect if the query is actually a concatenation of *DOI*s.
        regex: str = r'10\.\d{4,9}/[\w.\-;()/:]+'
        ids: list[str] = re.findall(regex, query)

        w = Works()

        try:
            return json.dumps(
                        w[query]
                    )

        except httpx.HTTPStatusError as e:
            print(f'\nHTTPStatusError: {e}\nResponse: {e.response.text}\n')
            error_payload = {
                'error': {
                    'type': 'HTTPStatusError',
                    'message': f"OpenAlex API request failed:\
                            {e.response.status_code} {e.response.reason_phrase}",
                    'status_code': e.response.status_code,
                    'details': str(e.response.text)[:200]
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

