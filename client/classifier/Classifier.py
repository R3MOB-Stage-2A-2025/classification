import concurrent.futures
from time import sleep
import re
import json

import config

# <Retrieve functions from the parsing module>
import sys
import os

dir_path_current: str = os.path.dirname(os.path.abspath(__file__))
sys.path.append(dir_path_current)
sys.path.append(
    dir_path_current.removesuffix("/client/classifier") + \
    "/parsing/python/json/")

from JsonParserCrossref import JsonParserCrossref
# </Retrieve functions from the parsing module>

# <Generic Model>
import sys
import os

dir_path_current: str = os.path.dirname(os.path.abspath(__file__))
sys.path.append(dir_path_current + "/model/services")
# </Generic Model>

# <Models>
if config.CLASSIFIER_CATEGORIZER_USE:
    from model.categorizer.app import Categorizer

if config.CLASSIFIER_TFIDF_USE:
    from model.tfidf.app import Tfidf

if config.CLASSIFIER_HIERARCHICAL_USE:
    from model.hierarchical.app import Hierarchical
# </Models>

# <Retrieve keywords>
from functions import load_json

#   <Labels>
labels: dict[str, dict[str, list[str]]] = {
    'challenges': load_json('data/challenge_keywords.json'),
    'themes': load_json('data/theme_keywords.json'),
    'scientificThemes': load_json('data/scientificTheme_keywords.json'),
    'mobilityTypes': load_json('data/mobilityType_keywords.json'),
    'axes': load_json('data/axe_keywords.json'),
    'usages': load_json('data/usage_keywords.json'),
}
#   </Labels>

#   <Label Precisions>
precisions: dict[str, list[float | str]] = {
    'challenges': [ 0.05, 0.10 ],
    'themes': [ 0.05, 0.20 ],
    'scientificThemes': [ 0.40, 0.10 ],
    'mobilityTypes': [ 0.002, 0.20 ],
    'axes': [ 0.009, 0.10, "mobilityTypes" ],
    'usages': [ 0.009, 0.25, "mobilityTypes" ],
}
#   </Label Precisions>

# </Retrieve keywords>

class Classifier:
    def __init__(self):
        print("Classifier initializing...")

        # <Models>
        if config.CLASSIFIER_CATEGORIZER_USE:
            self._model_categorizer =\
                Categorizer(labels=labels, precisions=precisions)

        if config.CLASSIFIER_TFIDF_USE:
            self._model_tfidf =\
                Tfidf(labels=labels, precisions=precisions)

        if config.CLASSIFIER_HIERARCHICAL_USE:
            self._model_hierarchical =\
                Hierarchical(labels=labels, precisions=precisions)
        # </Models>

        self._extra_class: str = "Other"

        # <Error Payload>
        self._error_payload: dict[str, list[str]] = {
            key: "[]" for key in labels
        }
        # </Error Payload>

        print("Classifier initialized.")

    # <Categorizer Model>
    def threaded_prompt_categorizer(self, prompt: str) -> dict[str, str]:
        return self._model_categorizer.prompt(prompt)

    def prompt_categorizer(self, prompt: str) -> dict[str, str]:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future = executor.submit(self.threaded_prompt_categorizer, prompt)
            result: dict[str, str] = future.result(timeout=25)
            return result
    # </Categorizer Model>

    def error_payload(self) -> dict[str, str]:
        return self._error_payload

    def add_extra_class(self, results: dict[str, str]) -> dict[str, str]:
        """
        """
        return { key: "[ \"" + self._extra_class + "\" ]"\
                if value == '[]' else value\
                for key, value in results.items()\
        }

    def parsing_by_publication(self, data: str) -> str:
        """
        Live Classification.
        """

        # <Parsing>
        data_parsed: str = JsonParserCrossref(data)
        doi: str = data_parsed.ID().get("DOI", "")
        data_to_classify_generic: str = data_parsed.classify_me()
        # </Parsing>

        # <debug>
        print("Extracted DOI:", doi)
        print(data_to_classify_generic)
        # </debug>

        return data_to_classify_generic

    def parsing_by_line(self, data: str) -> str:
        """
        Dataset Classification.
        """

        # <Parsing>
        data_dict = json.loads(data)
        data_to_classify_generic: str =\
            JsonParserCrossref(jsonfile=None).classify_me(line_json=data_dict)
        # </Parsing>

        # <debug>
        doi: str = data_dict.get("DOI", "")
        print("Extracted DOI:", doi)
        print(data_to_classify_generic)
        # </debug>

        return data_to_classify_generic

