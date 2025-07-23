# classifier/config.py

# <Environment variables>
import os
from dotenv import load_dotenv, dotenv_values

load_dotenv()

# <Flask + gevent + socketio>
BACKEND_PORT: int = int(os.getenv("BACKEND_PORT"))
BACKEND_SECRETKEY: str = os.getenv("BACKEND_SECRETKEY")
FRONTEND_HOST: str = os.getenv("FRONTEND_HOST")
# </Flask + gevent + socketio>

# <LLM Labellizer>
CLASSIFIER_LABELLIZER_USE: bool =\
    True if os.getenv("CLASSIFIER_LABELLIZER_USE") == "TRUE" else False
# </LLM Labellizer>

# <Classification Models>
CLASSIFIER_TFIDF_USE: bool =\
    True if os.getenv("CLASSIFIER_TFIDF_USE") == "TRUE" else False
CLASSIFIER_HIERARCHICAL_USE: bool =\
    True if os.getenv("CLASSIFIER_HIERARCHICAL_USE") == "TRUE" else False
# </Classification Models>

# </Environment variables>

