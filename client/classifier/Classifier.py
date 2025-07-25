import concurrent.futures
from time import sleep
import re
import json

import config

# <Retrieve keywords>
from functions import load_json

challenge_keywords: dict[str, list[str]]=\
    load_json('data/challenge_keywords.json')
theme_keywords: dict[str, list[str]] =\
    load_json('data/theme_keywords.json')
scientificTheme_keywords: dict[str, list[str]] =\
    load_json('data/scientificTheme_keywords.json')
mobilityType_keywords: dict[str, list[str]] =\
    load_json('data/mobilityType_keywords.json')
axe_keywords: dict[str, list[str]] =\
    load_json('data/axe_keywords.json')
usage_keywords: dict[str, list[str]] =\
    load_json('data/usage_keywords.json')
# </Retrieve keywords>

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

class Classifier:
    def __init__(self):
        print("Classifier initializing...")

        labels: dict[str, dict[str, list[str]]] = {
            'challenge_keywords': challenge_keywords,
            'theme_keywords': theme_keywords,
            'scientificTheme_keywords': scientificTheme_keywords,
            'mobilityType_keywords': mobilityType_keywords,
            'axe_keywords': axe_keywords,
            'usage_keywords': usage_keywords,
        }

        if config.CLASSIFIER_CATEGORIZER_USE:
            self._model_categorizer = Categorizer(labels=labels)

        if config.CLASSIFIER_TFIDF_USE:
            self._model_tfidf = Tfidf(labels=labels)

        if config.CLASSIFIER_HIERARCHICAL_USE:
            self._model_hierarchical = Hierarchical(labels=labels)

        print("Classifier initialized.")

    def threaded_prompt(self, prompt: str) -> dict[str, list[str]]:
        return self._model_categorizer.prompt(prompt)

    def prompt(self, prompt: str) -> dict[str, list[str]]:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future = executor.submit(self.threaded_prompt, prompt)
            result: dict[str, list[str]] = future.result(timeout=25)
            return result

    def classification_error(self, results: dict[str, list[str]]) -> bool:
        """
        Classification Response.
        """

        if 'challenges' in results and results['challenges'] == "[]":
            #results['challenges'] = '[ "No challenges found" ]'
            results['challenges'] = '[ "Other"]'

        if 'themes' in results and results['themes'] == "[]":
            #results['themes'] = '[ "No themes found" ]'
            results['themes'] = '[ "Other" ]'

        if 'scientificThemes' in results and results['scientificThemes'] == "[]":
            #results['scientificThemes'] = '[ "No scientific themes found" ]'
            results['scientificThemes'] = '[ "Other" ]'

        if 'mobilityTypes' in results and results['mobilityTypes'] == "[]":
            #results['mobilityTypes'] = '[ "No mobility types found" ]'
            results['mobilityTypes'] = '[ "Other" ]'

        if 'axes' in results and results['axes'] == "[]":
            #results['axes'] = '[ "No axes found" ]'
            results['axes'] = '[ "Other" ]'

        if 'usages' in results and results['usages'] == "[]":
            #results['usages'] = '[ "No usages found" ]'
            results['usages'] = '[ "Other" ]'

        return False

    def dataset_parsing(self, data: str) -> str:
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

    def live_parsing(self, data: str) -> str:
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

