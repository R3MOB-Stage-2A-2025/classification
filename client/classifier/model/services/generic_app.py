import httpx
import json

class Service:
    def __init__(self, labels: dict[str, dict[str, list[str]]],
                 precisions: dict[str, dict[str, float | str]]):
        """
        :param labels: the content of `data/labels.json`.

        1. There are multiple vectors of classification,
            as for instance `challenges`, `axes`, mobilityTypes`...

        2. For a vector of classification, there are various possible labels.
            Example for `axes`:
                - "Accompagner le développement des systèmes de transports
                        décarbonés et sûrs",
                - "Peser sur les choix de modes de transport des voyageurs",
                - "Favoriser le report modal des marchandises vers le fer
                        et le maritime et améliorer la logistique urbaine
                        et rurale".

        3. For each label from a vector of classification, there are chosen
            keywords related to it, it improves the classification for the
            *Categorizer*.
            Example for "Accompagner le développement des systèmes de ...":
            ```python
            [
              "Decarbonization",
              "Transport safety",
              "Sustainable mobility",
              "Green infrastructure",
              "Vehicle electrification",
              "Alternative fuels",
              "Emission reduction",
              "Public transport",
              "Autonomous vehicles",
              "Traffic safety",
              "Smart mobility",
              "Energy transition",
              "Eco-design",
              "Safety standards"
            ]
            ```

        :param precisions: the content of `data/precisions.json`.

        For each vector of classification
            (`challenges`, `axes`, mobilityTypes`, ...), there are:

            1. "threshold": at first (before classification),
                all the keywords from all the labels are gathered into
                one big label, which can represent the set of what the current
                model can classify.
                The threshold is the min value (abs value) of the result
                of the classification model between the prompt
                and this big label.
                It prevents from bias, the classification is made only if
                the prompt could be related to the set of labels from
                the current vector of classification.

            2. "precision": the max gap (abs value) between the top score
                and the score of another possible label. There are at most
                3 labels returned.
                One label is returned when the precision is low.
                2 or 3 labels are returned when the precision is high.

            3. "parent" (Optional): The key of the vector of classification
                that is related to the current one.
                Example: if we want to classify by `usages`
                    (related to cars and traffic) but the classification by
                    `transport` returned nothing (the publication does not
                    talk about transport), then the `usages` will also
                    return nothing, because it is not relevant to classify
                    by `usages`.
                    It prevents from classifying something that is not talking
                    about transport, when the vector of classification is
                    about to be biased.
        """

        self.name = "GenericModel"

        self._labels = labels
        self._precisions = precisions

    def generic_prompt(self, func_prompt, prompt: str):
        """
        :param func_prompt: a method like `model_tfidf.prompt()`.
        :param: prompt: The input argument of *func_prompt*.

        It returns `func_prompt(prompt)` but wrapped to catch errors
            and exceptions.

        If there is an error, it returns something as
        { 'error': 'message': "message error" }.
        """
        try:
            return func_prompt(prompt)

        except httpx.HTTPStatusError as e:
            print(f'\nHTTPStatusError: {e}\nResponse: {e.response.text}\n')
            name_func: str = func_query.__name__
            name_mod: str= func_query.__module__
            error_payload = {
                'error': {
                    'type': 'HTTPStatusError',
                    'message': f"From {name_func}() in {name_mod}:\
                        {e.response.status_code} {e.response.reason_phrase}",
                    'status_code': e.response.status_code,
                    'details': str(e.response.text)[:200]
                }
            }
            return error_payload

        except Exception as e:
            print(f'\nRuntimeError or other unhandled exception: {e}\n')
            error_payload = {
                'error': {
                    'type': 'ServerError',
                    'message': f"An unexpected error occurred \
                                on the server: {str(e)}"
                }
            }
            return error_payload

