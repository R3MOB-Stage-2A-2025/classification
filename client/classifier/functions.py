import json
import re

import config

# <Download *nltk* tools aka MISCELLANEOUS>
if config.CLASSIFIER_MISCELLANEOUS_USE:
    import nltk
    from nltk.stem import PorterStemmer
    # This one is searching in the `nltk_data/` dir.
    from nltk.corpus import stopwords, wordnet

    nltk.download(info_or_id='wordnet', download_dir=config.NLTK_DIRECTORY)
    nltk.download(info_or_id='stopwords', download_dir=config.NLTK_DIRECTORY)
# </Download *nltk* tools aka MISCELLANEOUS>

def load_json(file_path: str) -> str:
    with open(file_path, 'r') as f:
        return json.load(f)

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

    :param text: A text, everything.
    :return: something like a dataframe.
    """
    # <Cleaning and normalizing the text>
    lowercased_text: str = text.lower()
    remove_punctuation: str = re.sub(r'[^\w\s]', '', lowercased_text)
    remove_white_space: str = remove_punctuation.strip()
    # </Cleaning and normalizing the text>

    # <Tokenization>
    tokenized_text = nltk.word_tokenize(remove_white_space)
    # </Tokenization>

    # `set()` builds an unordered collection of unique elements.
    stop_words: set[str] = set(stopwords.words('english'))

    # <Remove stopwords> from the text i.e irrelevant words like "and".
    stop_words_removed: list[str] = list(set([
        word for word in tokenized_text \
        if word not in stop_words
    ]))
    # </Remove stopwords>

    # Stemming.
    ps = PorterStemmer()
    stemmed_text: list[str] =\
        set(list(ps.stem(word) for word in stop_words_removed))
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
    :param word: a single word.
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
    :param unique_keywords: See example.
    :return: unique_keywords enhanced.

    One keyword could not appear twice, except if there is one with an
    upcase letter. Example: 'Law' and 'law' bot appear below.

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

