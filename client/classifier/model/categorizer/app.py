import json
import re

from generic_app import Service

# <Transformers>
from sentence_transformers import SentenceTransformer, util
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')
# </Transformers>

class Categorizer(Service):
    def __init__(self, labels: dict[str, dict[str, list[str]]]):
        """
        """

        self.name = "LLM sentence-transformers HuggingFace"
        super().__init__(labels=labels)

    def prompt(self, prompt: str) -> dict[str, dict]:
        """
        For Live Classification.
        """
        def func_prompt(prompt):
            return self._classification_results(prompt)

        return self.generic_prompt(func_prompt, prompt)

    def _classification_results(self, data: str) -> dict[str, list[str]]:
        """
        :param data: It is not already parsed.
        """

        challenge_keywords: dict[str, list[str]] =\
            self._labels.get('challenge_keywords', {})
        theme_keywords: dict[str, list[str]] =\
            self._labels.get('theme_keywords', {})
        scientificTheme_keywords: dict[str, list[str]] =\
            self._labels.get('scientificTheme_keywords', {})
        mobilityType_keywords: dict[str, list[str]] =\
            self._labels.get('mobilityType_keywords', {})

        challenges: str = json.dumps(
            unsupervised_cosine_similarity(data,
                                           challenge_keywords,
                                           precision_utility=0.10,
                                           precision=0.05)
        )

        themes: str = json.dumps(
            unsupervised_cosine_similarity(data,
                                           theme_keywords,
                                           precision_utility=0.20,
                                           precision=0.05)
        )

        scientificThemes: str = json.dumps(
            unsupervised_cosine_similarity(data,
                                           scientificTheme_keywords,
                                           precision_utility=0.10,
                                           precision=0.4)
        )

        mobilityTypes: str = json.dumps(
            unsupervised_cosine_similarity(data,
                                           mobilityType_keywords,
                                           precision_utility=0.20,
                                           precision=0.002)
        )

        if mobilityTypes == "[]": # If it is not a transport, there is no axes.
            axes: str = "[]"
        else:
            axes: str = json.dumps(
                unsupervised_cosine_similarity(data,
                                               axe_keywords,
                                               precision_utility=0.10,
                                               precision=0.009)
            )

        if mobilityTypes == "[]": # If not a transport, there is no usages.
            usages: str = "[]"
        else:
            usages: str = json.dumps(
                unsupervised_cosine_similarity(data,
                                               usage_keywords,
                                               precision_utility=0.25,
                                               precision=0.009)
            )

        return {
            'challenges': challenges,
            'themes': themes,
            'scientificThemes': scientificThemes,
            'mobilityTypes': mobilityTypes,
            'axes': axes,
            'usages': usages,
        }

#############################################################################

def unsupervised_cosine_similarity(text: str, themes_keywords: dict[str, list],
            precision_utility: float = 0.10, precision: float = 0.08) -> list[str]:
    """

    """
    themes: list[str] = list(themes_keywords.keys())

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
    print("\n")
    print(scores_utility_check)
    # </debug>

    if -precision_utility < scores_utility_check[0]:
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
    print(top_scores)
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
    print(top_themes)
    # </debug>

    return top_themes

#############################################################################

