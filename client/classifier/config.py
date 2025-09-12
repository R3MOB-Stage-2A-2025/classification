# classifier/config.py

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
CLASSIFIER_DEBUG: bool =\
    True if os.getenv("CLASSIFIER_DEBUG") == "TRUE" else False
MAX_WORKERS: int = 4
# </Flask + gevent + socketio>

# <LLM Labellizer>
CLASSIFIER_CATEGORIZER_USE: bool =\
    True if os.getenv("CLASSIFIER_CATEGORIZER_USE") == "TRUE" else False
# </LLM Labellizer>

# <Classification Models>
CLASSIFIER_TFIDF_USE: bool =\
    True if os.getenv("CLASSIFIER_TFIDF_USE") == "TRUE" else False
CLASSIFIER_TFIDF_INPUT_FILE: str=\
    os.getenv("CLASSIFIER_TFIDF_INPUT_FILE")
CLASSIFIER_TFIDF_TEST_SIZE: float =\
    float(os.getenv("CLASSIFIER_TFIDF_TEST_SIZE"))
CLASSIFIER_TFIDF_MAX_FEATURES: int =\
    int(os.getenv("CLASSIFIER_TFIDF_MAX_FEATURES"))
CLASSIFIER_TFIDF_NGRAM_RANGE: tuple =\
    tuple([ int(number) for number in\
           os.getenv("CLASSIFIER_TFIDF_NGRAM_RANGE")\
             .replace('(', '').replace(')', '').split(',')
    ])
CLASSIFIER_TFIDF_MULTILABEL_ALGORITHM: str =\
    os.getenv("CLASSIFIER_TFIDF_MULTILABEL_ALGORITHM")
CLASSIFIER_TFIDF_CLASS_WEIGHT: str =\
    os.getenv("CLASSIFIER_TFIDF_CLASS_WEIGHT")
CLASSIFIER_TFIDF_IGNORE_WARNINGS: bool =\
    True if os.getenv("CLASSIFIER_TFIDF_IGNORE_WARNINGS") == "TRUE" else False
CLASSIFIER_TFIDF_SAVE_TEXT_CLEAN: bool =\
    True if os.getenv("CLASSIFIER_TFIDF_SAVE_TEXT_CLEAN") == "TRUE" else False
CLASSIFIER_TFIDF_DISPLAY_CROSSVALIDATION: bool =\
    True if os.getenv("CLASSIFIER_TFIDF_DISPLAY_CROSSVALIDATION") == "TRUE" else False
# </Classification Models>

# <Tokenizer + Embeddings>
NLTK_DIRECTORY: str = os.getenv("NLTK_DIRECTORY")
SPACY_MODEL: str = os.getenv("SPACY_MODEL")
CLASSIFIER_MISCELLANEOUS_USE: bool =\
    True if os.getenv("CLASSIFIER_MISCELLANEOUS_USE") == "TRUE"\
    or CLASSIFIER_TFIDF_USE == True\
    else False
# </Tokenizer + Embeddings>

# </Environment variables>

# <Debug functions>
def debug_wrapper(**kwargs) -> None:
    result: str = ""

    if not CLASSIFIER_DEBUG:
        print(result)

    else:
        for k, val in kwargs.items():
            result += f'[{str(k)}={str(val)}]'
        print(result)
# </Debug functions>

