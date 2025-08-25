import json
import re

from generic_app import Service

# <Transformers>
from sentence_transformers import SentenceTransformer, util
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')
# </Transformers>

class Categorizer(Service):
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
            (`challenges`, `axes`, `mobilityTypes`, ...), there are:

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

        self.name = "LLM sentence-transformers HuggingFace"
        super().__init__(labels=labels, precisions=precisions)

    def prompt(self, prompt: str) -> dict[str, str]:
        """
        :param prompt: it is a text, see `Classifier.prompt_generic()`.
        :return: The classification result over all the labels,
            see `Classifier.prompt_generic()`.

        It merely calls `unsupervised_cosine_similarity()`
            for every label.
        """
        def func_prompt(prompt):
            results: dict[str, str] = {}

            for label in self._labels:
                label_keywords: list[str] = self._labels[label]

                label_precisions: dict[str, float | str] =\
                    self._precisions.get(label, [])

                label_precision: float =\
                    label_precisions.get('precision', None)

                label_threshold: float =\
                    label_precisions.get('threshold', None)

                # <Utility Check> if the parent label is not the *extra class*.
                label_parent: str =\
                    label_precisions.get('parent', None)

                if label_parent != None:
                    if results.get(label_parent, "[]") == "[]":
                        results[label] = "[]"
                        continue
                # </Utility Check>

                results[label] = json.dumps(
                    unsupervised_cosine_similarity(prompt, label_keywords,\
                        threshold=label_threshold, precision=label_precision)
                )

            return results

        return self.generic_prompt(func_prompt, prompt)

#############################################################################

def unsupervised_cosine_similarity(text: str, themes_keywords: dict[str, list],
            threshold: float = 0.10, precision: float = 0.08) -> list[str]:
    """
    :param text: a text, it is better if it is already parsed.
        Anyway, it is given to a llm, it could understand sentences.
    :param themes_keywords: a label set and its keywords
        from `data/labels.json`. see `service()`.
    :param threshold: see `Service()`.
    :param precision: see `Service()`.

    :return: the labels with a good score.
    """

    themes: list[str] = list(themes_keywords.keys())

    # <debug>
    print("\n")
    print(f'Possible themes: {themes}')
    # </debug>

    enhanced_themes: list[str] = []
    for theme, keywords in themes_keywords.items():
        concatenation: str = '[ ' + theme + ' ] ' +  ' '.join(keywords)
        enhanced_themes.append(concatenation)

    # <Utility Check>
    utility_check = model.encode(', '.join(enhanced_themes))
    publication_utility_check = model.encode(text)
    cosine_scores_utility_check =\
        util.cos_sim(publication_utility_check, utility_check)[0]
    indices_utility_check: list[int] =\
        np.argsort(-cosine_scores_utility_check)[:3].tolist()
    scores_utility_check: list[float] =\
        np.sort(-cosine_scores_utility_check)[:3].tolist()

    # <debug>
    print(f'Current Threshold: {scores_utility_check}')
    print(f'Min absolute Threshold: {threshold}')
    # </debug>

    if -threshold < scores_utility_check[0]:
        return []
    # </Utility Check>

    theme_embeddings = model.encode(enhanced_themes)

    # Publication text is a concatenation of the title, the abstract and
    # sometimes extra metadata.
    publication_text: str = text
    publication_embedding = model.encode(publication_text)

    # Compute similarities.
    cosine_scores = util.cos_sim(publication_embedding, theme_embeddings)[0]

    # Here, I set up the max number of themes.
    # For something like a "thematique scientifique", let's consider max=3.
    top_indices: list[int] = np.argsort(-cosine_scores)[:3].tolist()

    # Then, if there is a score gap, let's remove the last or the 2 last ones.
    top_scores: list[float] = np.sort(-cosine_scores)[:3].tolist()

    # <debug>
    print(f'Top scores: {top_scores}')
    print(f'Top themes: {[ themes[i] for i in top_indices ]}')
    print(f'Min absolute Score: {0.10}')
    print(f'Max absolute Gap (precision): {precision}')
    # </debug>

    # <Threshold Check>
    for i in range(len(top_indices) - 1, -1, -1):
        if i == 0 and -0.10 < top_scores[i]:
            top_indices.pop(i)
        elif abs(top_scores[i] - top_scores[0]) > precision or\
                -0.10 < top_scores[i]:
            top_indices.pop(i)

    top_themes: list[str] = []
    for i in top_indices:
        top_themes.append(themes[i])
    # </Threshold Check>

    # <debug>
    print(f'Themes as a result: {top_themes}')
    # </debug>

    return top_themes

#############################################################################

