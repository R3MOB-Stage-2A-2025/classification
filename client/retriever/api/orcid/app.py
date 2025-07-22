from generic_app import Service

from pyorcid import orcid_scrapper

class OrcidClient(Service):
    def __init__(self, apiurl: str = None, apikey: str = None,
                 mailto: str = None, timeout: int = 20):
        """
        There is:

        ```python
        # There is no environment variables.
        ```

        It uses `pyorcid.OrcidScrapper()` which does not require any
            environment variables to be set.
        """

        self.name = "PyOrcid(ORCID)"
        super().__init__(apiurl=apiurl, apikey=apikey,
                         mailto=mailto, timeout=timeout)

    def orcid_query(self, orcid_id: str) -> dict[str, dict]:
        """
        :param orcid_id: The ORCID id of an author.
            Example: `0000-0001-6643-9567`.
                From `https://orcid.org/`

        :return: The result of `pyorcid.OrcidScrapper.activities()`.
        This should contain affiliations and other stuff related to the author.

        This is not parsed in the *Crossref Style*.
        """
        orcid_data = orcid_scrapper.OrcidScrapper(orcid_id=orcid_id)
        return orcid_data.activities()

