from generic_app import Service

import re
import json

import pybliometrics

class ScopusClient(Service):
    def __init__(self, apiurl: str = None, apikey: str = None,
                 mailto: str = None, timeout: int = 20):

        """
        There is:

        ```python
        PYBLIOMETRICS_APIKEY=<apikey>
        ```

        There is not `mailto`, *semanticscholar* does not
            have a polite pool.
        There is not `apiurl`, it is hardcoded in *pybliometrics*.
        There is not `timeout`.
        """

        self.name = "Pybliometrics(Scopus)"
        super().__init__(apiurl=apiurl, apikey=apikey,
                         mailto=mailto, timeout=timeout)

        pybliometrics.scopus.utils.init(keys=[apikey])

    def query_author(self, query: str) -> str:
        """
        :param query: `author, ORCID iD, etc..`
        :return: the result of ``pybliometrics.scopus.AuthorSearch()``.
                 the result is a string from `json.dumps()`.

        This is not parsed in the *Crossref Style*.
        """

        query: str = query
        refresh: bool | int = False
        verbose: bool = True
        download: bool = False
        integrity_fields: list[str] | tuple(str) = None
        integrity_action: str = 'raise'

        result = pybliometrics.scopus.AuthorSearch(
            query=query,
            refresh=refresh,
            verbose=verbose,
            download=download,
            integrity_fields=integrity_fields,
            integrity_action=integrity_action
        )

        return result.__str__()

