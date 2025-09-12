# retriever/config.py

# <Environment variables>
import os
from dotenv import load_dotenv, dotenv_values

load_dotenv()

# <Flask + gevent + socketio>
FLASK_BACKEND_PORT: int = int(os.getenv("FLASK_BACKEND_PORT"))
FLASK_BACKEND_SECRETKEY: str = os.getenv("FLASK_BACKEND_SECRETKEY")
FLASK_FRONTEND_HOST: str = os.getenv("FLASK_FRONTEND_HOST")
FLASK_DEBUG: bool=\
    True if os.getenv("FLASK_DEBUG") == "TRUE" else False
FLASK_ALLOWED_ORIGINS: str = os.getenv("FLASK_ALLOWED_ORIGINS")
FLASK_MAX_INPUT_LENGTH: int = int(os.getenv("FLASK_MAX_INPUT_LENGTH"))
RETRIEVER_DEBUG: bool =\
    True if os.getenv("RETRIEVER_DEBUG") == "TRUE" else False
MAX_WORKERS: int = 4
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

# <RISPY>
RISPY_WORKING_FOLDER: str = os.getenv("RISPY_WORKING_FOLDER")
# </RISPY>

# </Environment variables>

# <Debug functions>

def debug_wrapper(**kwargs) -> None:
    result: str = ""

    if not RETRIEVER_DEBUG:
        print(result)

    else:
        for k, val in kwargs.items():
            result += f'[{str(k)}={str(val)}]'
        print(result)
# </Debug functions>

