# retriever/config.py

# <Environment variables>
import os
from dotenv import load_dotenv, dotenv_values

load_dotenv()

# <Flask + gevent + socketio>
BACKEND_PORT: int = int(os.getenv("BACKEND_PORT"))
BACKEND_SECRETKEY: str = os.getenv("BACKEND_SECRETKEY")
FRONTEND_HOST: str = os.getenv("FRONTEND_HOST")
# </Flask + gevent + socketio>

# <OpenAlex>
PYALEX_MAILTO: str = os.getenv("PYALEX_MAILTO")
# </OpenAlex>

# <SemanticScholar>
SEMANTICSCHOLAR_APIURL: str = os.getenv("SEMANTICSCHOLAR_APIURL")
SEMANTICSCHOLAR_APIKEY: str = os.getenv("SEMANTICSCHOLAR_APIKEY")
SEMANTICSCHOLAR_TIMEOUT: int = int(os.getenv("SEMANTICSCHOLAR_TIMEOUT")) # seconds
# </SemanticScholar>

# <Crossref>
HABANERO_APIURL: str = os.getenv("HABANERO_BASEURL")
HABANERO_APIKEY: str = os.getenv("HABANERO_APIKEY")
HABANERO_MAILTO: str = os.getenv("HABANERO_MAILTO")
HABANERO_TIMEOUT: int = int(os.getenv("HABANERO_TIMEOUT")) # seconds
# </Crossref>

# <Orcid>

# </Orcid>

# <Scopus>
PYBLIOMETRICS_APIKEY: str = os.getenv("PYBLIOMETRICS_APIKEY")
# </Scopus>

# </Environment variables>

