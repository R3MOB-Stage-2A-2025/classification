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
                 precisions: dict[str, list[float]]):
        """
        """

        self.name = "LLM sentence-transformers HuggingFace"
        super().__init__(labels=labels, precisions=precisions)

    def prompt(self, prompt: str) -> dict[str, str]:
        """
        For Live Classification.
        """
        def func_prompt(prompt):
            results: dict[str, str] = {}

            for label in self._labels:
                label_keywords: list[str] = self._labels[label]

                label_precisions: list[float] = self._precisions.get(label, [])
                label_precision: float =\
                    label_precisions[0] if len(label_precisions) >= 1 else None
                label_threshold: float =\
                    label_precisions[1] if len(label_precisions) >= 2 else None

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

