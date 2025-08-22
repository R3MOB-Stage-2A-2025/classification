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

labels: dict[str, dict[str, list[str]]] =\
    load_json('data/labels.json')
precisions: dict[str, dict[str, float | str]] =\
    load_json('data/precisions.json')
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

    #########################################################################
    #### Generic Prompt
    #########################################################################

    def _threaded_prompt_generic(self, prompt: str) -> dict[str, str]:
        """
        :param prompt: a text, see `self.prompt_generic()`.
        :return: What `self.model_xxxx.prompt(prompt)` returns.

        Here is the order of which model is taken:

        1. TFIDF (CLASSIFIER_TFIDF_USE == TRUE).
        2. Hierarchical (CLASSIFIER_HIERARCHICAL_USE == TRUE\
                        && CLASSIFIER_TFIDF_USE == FALSE)
        3. Categorizer (CLASSIFIER_HIERARCHICAL_USE == FALSE\
                        && CLASSIFIER_TFIDF_USE == FALSE)

        Even if `CLASSIFIER_CATEGORIZER_USE == FALSE`, it will be chosen
        if no model is taken, but it will create an error because the packages
        from `requirements/categorizer_requirements.txt` are not downloaded.
        """

        if config.CLASSIFIER_TFIDF_USE:
            return self._model_tfidf.prompt(prompt)
        elif config.CLASSIFIER_HIERARCHICAL_USE:
            return self._model_hierarchical.prompt(prompt)
        return self._model_categorizer.prompt(prompt)

    def prompt_generic(self, prompt: str) -> dict[str, str]:
        """
        :param prompt: it is a text.
        This is better if it is already parsed, as for instance:

        ```
        Model–Ship Extrapolation, A, summary, is, not, available, for, this,
        content, so, a, preview, has, been, provided., Please, use, the,
        Get, access, link, above, information, on, how, to, content.,
        Marine and Offshore Engineering Studies, Ocean Engineering, Engineering,
        Physical Sciences, Maritime Transport Emissions and Efficiency,
        Environmental Engineering, Environmental Science, Physical Sciences,
        Content (measure theory), Extrapolation, Computer science,
        Content (measure theory), Mathematics, Statistics,
        Mathematical analysis,
        ```

        :return: The results of the chosen model
            (see `self._threaded_prompt_generic`).

        An example of a result for the prompt above
            (there is usually no line jumps):

        ```python
        {'challenges': '["Strat\\u00e9giques", "Economiques"]',
        'themes': '["Logistique"]',
        'scientificThemes': '["Sciences juridiques, R\\u00e8glementations
            et Assurances", "Sciences \\u00e9conomique, \\u00c9valuation
            des politiques publiques, Mod\\u00e8les \\u00e9conomiques",
            "Marketing, Durabilit\\u00e9, Chaine d\\u2019approvisionnement,
            Logistiques, Inter & Multimodalit\\u00e9"]',
        'mobilityTypes': '["Fluvial/Maritime"]',
        'axes': '["Favoriser le report modal des marchandises vers le fer et
            le maritime et am\\u00e9liorer la logistique urbaine et rurale"]',
        'usages': '[]'}
        ```

        If there is an error, it returns `self.error_payload()`.
        """
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=config.MAX_WORKERS) as executor:

            future = executor.submit(self._threaded_prompt_generic, prompt)
            result: dict[str, str] = future.result(timeout=25)

            if 'error' in result:
                return self.error_payload()
            return result

    #########################################################################
    #### Model - Categorizer
    #########################################################################

    def _threaded_prompt_categorizer(self, prompt: str) -> dict[str, str]:
        """
        See `self._threaded_prompt_generic()`.
        """
        return self._model_categorizer.prompt(prompt)

    def prompt_categorizer(self, prompt: str) -> dict[str, str]:
        """
        See `self.prompt_generic()`.
        """
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=config.MAX_WORKERS) as executor:

            future = executor.submit(self._threaded_prompt_categorizer, prompt)
            result: dict[str, str] = future.result(timeout=25)

            if 'error' in result:
                return self.error_payload()
            return result

    #########################################################################
    #### Model - TFIDF
    #########################################################################

    def _threaded_prompt_tfidf(self, prompt: str) -> dict[str, str]:
        """
        See `self._threaded_prompt_generic()`.
        """
        return self._model_tfidf.prompt(prompt)

    def prompt_tfidf(self, prompt: str) -> dict[str, str]:
        """
        See `self.prompt_generic()`.
        """
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=config.MAX_WORKERS) as executor:

            future = executor.submit(self._threaded_prompt_tfidf, prompt)
            result: dict[str, str] = future.result(timeout=25)

            if 'error' in result:
                return self.error_payload()
            return result

    def train_tfidf(self, input_file: str = "") -> None:
        """
        See `model/tfidf/app.py`.
        """
        self._model_tfidf.train(input_file=input_file)

    #########################################################################
    #### Model - Hierarchical
    #########################################################################

    def _threaded_prompt_hierarchical(self, prompt: str) -> dict[str, str]:
        """
        See `self._threaded_prompt_generic()`.
        """
        return self._model_hierarchical.prompt(prompt)

    def prompt_hierarchical(self, prompt: str) -> dict[str, str]:
        """
        See `self.prompt_generic()`.
        """

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=config.MAX_WORKERS) as executor:

            future = executor.submit(self._threaded_prompt_hierarchical, prompt)
            result: dict[str, str] = future.result(timeout=25)

            if 'error' in result:
                return self.error_payload()
            return result

    #########################################################################
    #### Specific Payloads
    #########################################################################

    def error_payload(self) -> dict[str, str]:
        """
        :return: A blank payload in case there is an error, so returned
        payload by `self.prompt_xxx()` is always something correct.
        """
        return self._error_payload

    def add_extra_class(self, results: dict[str, str]) -> dict[str, str]:
        """
        :param results: something returned by `self.model_xxx.prompt()`.
        :return: *results* where all the blank labels are replaced by the
            extra label, in order to get an "extra class" when training
            a model.

        Example:

            Something from *results* could be:
            ```python
            {
            # ...
            'usages': '[]'
            # ...
            }

            Something that will be returned:
            ```python
            {
            # ...
            'usages': '[ "Other" ]'
            # ...
            }
            ```
        """

        return { key: "[ \"" + self._extra_class + "\" ]"\
                if value == '[]' else value\
                for key, value in results.items()\
        }

    #########################################################################
    #### Parsing
    #########################################################################

    def parsing_by_publication(self, data: str) -> str:
        """
        :param data: a publication from `json.dumps()`
            in the *Crossref style*.
        Example: See the `/parsing/README.md` file.

        :return: the result of `JsonParserCrossref(data).classify_me()`
            from the *parsing* module.
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

        :param data: a json line from `json.dumps()`.
        Example: See the `/parsing/README.md` file.

        :return: the result of
            `JsonParserCrossref().classify_me(line_json=data_dict)`
            from the *parsing* module.
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

#############################################################################

