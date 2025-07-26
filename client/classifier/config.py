# classifier/config.py

# <Environment variables>
import os
from dotenv import load_dotenv, dotenv_values

load_dotenv()

# <Flask + gevent + socketio>
BACKEND_PORT: int = int(os.getenv("BACKEND_PORT"))
BACKEND_SECRETKEY: str = os.getenv("BACKEND_SECRETKEY")
FRONTEND_HOST: str = os.getenv("FRONTEND_HOST")
MAX_WORKERS: int = 4
# </Flask + gevent + socketio>

# <LLM Labellizer>
CLASSIFIER_CATEGORIZER_USE: bool =\
    True if os.getenv("CLASSIFIER_CATEGORIZER_USE") == "TRUE" else False
# </LLM Labellizer>

# <Classification Models>
CLASSIFIER_TFIDF_USE: bool =\
    True if os.getenv("CLASSIFIER_TFIDF_USE") == "TRUE" else False
CLASSIFIER_HIERARCHICAL_USE: bool =\
    True if os.getenv("CLASSIFIER_HIERARCHICAL_USE") == "TRUE" else False
# </Classification Models>

# <Tokenizer + Embeddings>
NLTK_DIRECTORY: str = os.getenv("NLTK_DIRECTORY")
SPACY_MODEL: str = os.getenv("SPACY_MODEL")
CLASSIFIER_MISCELLANEOUS_USE: bool =\
    True if os.getenv("CLASSIFIER_MISCELLANEOUS_USE") == "TRUE" else False
# </Tokenizer + Embeddings>

# </Environment variables>

