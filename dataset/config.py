# dataset/config.py

# <Environment variables>
import os
from dotenv import load_dotenv, dotenv_values

load_dotenv()

# <Retriever>
RETRIEVER_HOST: str = os.getenv("RETRIEVER_HOST")
RETRIEVER_PORT: str = os.getenv("RETRIEVER_PORT")
RETRIEVER_SCHEME: str = os.getenv("RETRIEVER_SCHEME")

RETRIEVER_URL: str = RETRIEVER_SCHEME +\
                     RETRIEVER_HOST +\
               ":" + RETRIEVER_PORT
# </Retriever>

# <Classifier>
CLASSIFIER_HOST: str = os.getenv("CLASSIFIER_HOST")
CLASSIFIER_PORT: str = os.getenv("CLASSIFIER_PORT")
CLASSIFIER_SCHEME: str = os.getenv("CLASSIFIER_SCHEME")

CLASSIFIER_URL: str = CLASSIFIER_SCHEME +\
                     CLASSIFIER_HOST +\
               ":" + CLASSIFIER_PORT
# </Classifier>

# </Environment variables>

