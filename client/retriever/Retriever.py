import config

from api.openalex.app import OpenAlexClient
#from api.semanticscholar.app import SemanticScholarClient
#from api.crossref.app import CrossrefClient
#from api.orcid.app import OrcidClient
#from api.scopus.app import ScopusClient

class Retriever:
    def __init__(self):
        print("Retriever initializing...")

        self._openalex = OpenAlexClient(
            apiurl  = None,
            apikey  = None,
            mailto  = config.PYALEX_MAILTO,
            timeout = None
        )

        #self._semanticscholar = SemanticScholarClient(
            #apiurl  = config.SEMANTICSCHOLAR_APIURL,
            #apikey  = config.SEMANTICSCHOLAR_APIKEY,
            #mailto  = None,
            #timeout = config.SEMANTICSCHOLAR_TIMEOUT
        #)

        #self._crossref = CrossrefClient(
            #apiurl  = config.HABANERO_APIURL,
            #apikey  = config.HABANERO_APIKEY,
            #mailto  = config.HABANERO_MAILTO,
            #timeout = config.HABANERO_TIMEOUT
        #)

        #self._orcid = OrcidClient(
            #apiurl  = None,
            #apikey  = None,
            #mailto  = None,
            #timeout = None
        #)

        #self._scopus = ScopusClient(
            #apiurl  = None,
            #apikey  = config.PYBLIOMETRICS_APIKEY,
            #mailto  = None,
            #timeout = None
        #)

        print("Retriever initialized.")

    def query(self, query: str) -> str:
        return self._openalex.query(query)

