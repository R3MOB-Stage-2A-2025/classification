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
        :return: the result of ``pyalex.Works.search()``. It is various *json*.
                 the result is a string from `json.dumps()`.
        """

        def func_query(query: str) -> str:
            w = Works()
            return json.dumps(w[query])

        return self.generic_query(func_query, query)

