from generic_app import Service

from pyorcid import orcid_scrapper

class OrcidClient(Service):
    def __init__(self, apiurl: str = None, apikey: str = None,
                 mailto: str = None, timeout: int = 20):

        self.name = "PyOrcid(ORCID)"
        super().__init__(apiurl=apiurl, apikey=apikey,
                         mailto=mailto, timeout=timeout)

    def orcid_query(self, orcid_id: str) -> dict[str, dict]:
        orcid_data = orcid_scrapper.OrcidScrapper(orcid_id=orcid_id)
        return orcid_data.activities()

