import json
import re

import nltk
# This one is searching in the `nltk_data/` dir.
from nltk.corpus import stopwords, wordnet

from nltk.stem import PorterStemmer

# Retrieve environment variables.
import os
from dotenv import load_dotenv, dotenv_values

load_dotenv()
NLTK_DIRECTORY: str = os.getenv("NLTK_DIRECTORY")
# </Retrieve environment variables>

# Download *nltk* tools.
nltk.download(info_or_id='wordnet', download_dir=NLTK_DIRECTORY)
nltk.download(info_or_id='stopwords', download_dir=NLTK_DIRECTORY)
# </Download *nltk* tools>

# Transformers
from sentence_transformers import SentenceTransformer, util
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')
# </Transformers>

def load_json(file_path: str) -> str:
    with open(file_path, 'r') as f:
        return json.load(f)

##############################################################################
## CLASSIFY WITHOUT A DATASET
##############################################################################

def unsupervised_cosine_similarity(text: str, themes_keywords: dict[str, list], precision: float = 0.08) -> list[str]:
    """
    If you worry about the "-" in the `np.sort()` or `np.argsort()`,
    it is just to get a *descending order*.
    In fact, all the scores are negatives. The strongest match is the
    highest score given its absolute value.
    """
    themes: list[str] = list(themes_keywords.keys())

    # This one will be given to the model. It enhances, using keywords.
    enhanced_themes: list[str] = []
    for theme, keywords in themes_keywords.items():
        concatenation: str = '[ ' + theme + ' ] ' +  ' '.join(keywords)
        enhanced_themes.append(concatenation)

    theme_embeddings = model.encode(enhanced_themes)

    # Publication text is a concatenation of the title, the abstract and
    # sometimes extra metadata.
    publication_text: str = text
    publication_embedding = model.encode(publication_text)

    # Compute similarities.
    cosine_scores = util.cos_sim(publication_embedding, theme_embeddings)[0]

    # Here, I set up the max number of themes.
    # For something like a "thematique scientifique", let's consider max=3.
    top_indices: list[float] = np.argsort(-cosine_scores)[:3].tolist()

    # Then, if there is a score gap, let's remove the last or the 2 last ones.
    top_scores: list[float] = np.sort(-cosine_scores)[:3].tolist()

    # TODO: debug.
    print(top_scores)
    # </debug>

    for i in range(len(top_scores) - 1, 0, -1):
        if abs(top_scores[i] - top_scores[0]) > precision:
            top_indices.pop(i)

    top_themes: list[str] = [themes[i] for i in top_indices]

    # TODO: debug.
    print(top_themes)
    # </debug>

    return top_themes

###############################################################################
### INPUT NORMALIZATION FUNCTIONS
###############################################################################


def preprocess_text(text: str) -> dict[str, list[str | list[str]]]:
    """
            !!! Works only for English text. !!!

    1. lowercase the text.
    2. remove punctuation and noise.
    3. remove white spaces.
    4. tokenize by word.
    5. remove stop words like "and".
    6. stemming: transform each token/word into its base form.

    :return: something like a dataframe.
    """
    # Cleaning and normalizing the text.
    lowercased_text: str = text.lower()
    remove_punctuation: str = re.sub(r'[^\w\s]', '', lowercased_text)
    remove_white_space: str = remove_punctuation.strip()

    # Tokenization.
    tokenized_text = nltk.word_tokenize(remove_white_space)

    # `set()` builds an unordered collection of unique elements.
    stop_words: set[str] = set(stopwords.words('english'))

    # Remove stopwords from the text i.e irrelevant words like "and".
    stop_words_removed: list[str] = list(set([
        word for word in tokenized_text \
        if word not in stop_words
    ]))

    # Stemming.
    ps = PorterStemmer()
    stemmed_text: list[str] = set(list(ps.stem(word) for word in stop_words_removed))

    dataframe = {
        'DOCUMENT': [text],
        'LOWERCASE' : [lowercased_text],
        'CLEANING': [remove_white_space],
        'TOKENIZATION': [tokenized_text],
        'STOP-WORDS': [stop_words_removed],
        'STEMMING': [stemmed_text]
    }

    return dataframe


def get_synonyms(word: str) -> set[str]:
    """
    :return: The synonyms of the given word, using *WordNet*.
    `word` is in the resulting set. However, all the words are
    in lowercase.

    - Example of execution:

    word: Law
    result: {
        'law_of_nature', 'police_force', 'police', 'law',
        'jurisprudence', 'constabulary', 'natural_law',
        'legal_philosophy', 'practice_of_law'
    }
    """
    synonyms: set[str] = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())

    return synonyms


def expand_keywords_with_synonyms(unique_keywords: dict[str, set[str]]):
    """
    Example of execution:

    Input:
    {
        'Sciences juridiques, Règlementations et Assurances':
        {
            'Compliance', 'Maritime law', 'Environmental law',
            'Legal framework', 'Contract', 'Public liability',
            'Liability', 'Insurance policy', 'Insurance', 'Law',
            'Risk management', 'Legislation', 'Policy', 'Regulation'
        }
    }

    Output:
    {
        'Sciences juridiques, Règlementations et Assurances':
        {
            'Compliance', 'constabulary', 'jurisprudence', 'regulating',
            'undertake', 'contract_bridge', 'cut', 'obligingness',
            'deference', 'sign', 'Legal framework', 'natural_law',
            'compliancy', 'Liability', 'contract', 'abbreviate',
            'sign_up', 'Policy', 'foreshorten', 'conformity', 'constrict',
            'regulation', 'statute_law', 'insurance_policy', 'get',
            'Environmental law', 'Contract', 'liability', 'condense',
            'abridge', 'legislating', 'complaisance', 'press', 'sign_on',
            'abidance', 'take', 'declaration', 'rule', 'financial_obligation',
            'legal_philosophy', 'squeeze', 'regularization', 'indebtedness',
            'conformation', 'insurance', 'practice_of_law', 'indemnity',
            'compact', 'Insurance policy', 'shorten', 'reduce',
            'Insurance', 'concentrate', 'compress', 'narrow', 'shrink',
            'Legislation', 'Regulation', 'compliance', 'Maritime law',
            'police', 'Public liability', 'regularisation', 'legislation',
            'Law', 'police_force', 'submission', 'policy', 'law_of_nature',
            'ordinance', 'law', 'lawmaking', 'Risk management'
        }
    }
    """
    expanded_keywords_with_synonyms: dict[str, set[str]] = {}

    for theme in unique_keywords:
        for keyword in unique_keywords[theme]:
            if theme not in expanded_keywords_with_synonyms:
                expanded_keywords_with_synonyms[theme] = get_synonyms(keyword)
            else:
                expanded_keywords_with_synonyms[theme].update(get_synonyms(keyword))

    return expanded_keywords_with_synonyms


def expand_and_preprocess_keywords(themes_keywords: dict[str, str]) -> dict[str, set[str]]:
    # `set()` builds an unordered collection of unique elements.
    unique_keywords: dict[str, set[str]] = {
        theme: set(keywords) \
        for theme, keywords in themes_keywords.items()
    }

    return expand_keywords_with_synonyms(unique_keywords)


###############################################################################
### CLASSIFY BY KEYWORDS
###############################################################################

def is_keyword_in_processed_text(keyword: str, processed_text: list[str]) -> bool:
    """
    dataframe['STEMMING'] i.e `processed_text` could be like that:

    [['energi', 'effici', 'remain', 'key', 'issu', 'wireless', 'sensor',
    'network', 'dutycycl', 'mechan', 'acquir', 'much', 'interest', 'due']]

    The words are not well written.
    """
    for elt in processed_text:
        if elt == keyword.lower():
            return True
    return False

def classify_abstract_by_keywords(text: str, themes_keywords: dict[str, str]) -> list[str]:
    dataframe = preprocess_text(text)
    processed_text: list[str] = dataframe['STEMMING'][0]

    themes_keywords = expand_and_preprocess_keywords(themes_keywords)
    abstract_themes: list[str] = []

    for theme, keywords in themes_keywords.items():
        for keyword in keywords:
            if is_keyword_in_processed_text(keyword, processed_text):
                abstract_themes.append(theme)
                break

    return abstract_themes


