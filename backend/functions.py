import json
import re
import spacy

import nltk
# This one is searching in the `nltk_data/` dir.
from nltk.corpus import stopwords, wordnet

from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Retrieve environment variables.
import os
from dotenv import load_dotenv, dotenv_values

load_dotenv()
NLTK_DIRECTORY: str = os.getenv("NLTK_DIRECTORY")
SPACY_MODEL: str = os.getenv("SPACY_MODEL")
# </Retrieve environment variables>

nltk.download(info_or_id='punkt_tab', download_dir=NLTK_DIRECTORY)
nltk.download(info_or_id='wordnet', download_dir=NLTK_DIRECTORY)
nltk.download(info_or_id='stopwords', download_dir=NLTK_DIRECTORY)

nlp = spacy.load(SPACY_MODEL)

def load_json(file_path: str) -> str:
    with open(file_path, 'r') as f:
        return json.load(f)


##############################################################################
## INPUT NORMALIZATION FUNCTIONS
##############################################################################


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


##############################################################################
## CLASSIFICATION FUNCTIONS
##############################################################################

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

def classify_abstract_TF_IDF(text: str, themes_keywords: dict[str, str]) -> list[str]:
    dataframe = preprocess_text(text)
    stemming: str = ' '.join(dataframe['STEMMING'][0])

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(stemming)

    feature_names = vectorizer.get_feature_names_out()

# Similarity Cosine
def classify_cosine_similarity(abstract_text: list[str], themes_keywords):
    abstract_themes = classify_abstract_TF_IDF(abstract_text, themes_keywords)

    # Get the TF-IDF vector for the first item (index 0)
    vector1: str = abstract_themes[0]

    # Get the TF-IDF vector for all items except the first item
    vectors: str = abstract_themes[1:]

    cosim = cosine_similarity(vector1, vectors)
    cosim = pd.DataFrame(cosim) # Not 1D array dataframe.
    cosim = cosim.values.flatten() # 1D array dataframe.
    print("EHOH")
    print(cosim)

    # Convert the results into a dataframe.
    #df_cosim = pd.DataFrame(cosim, columns=['COSIM'])
    #df_cosim = pd.concat([df_tfidf, df_cosim], axis=1)

    print(cosim)
    return cosim #df_cosim
# </Similarity Cosine>


##############################################################################
## METRIC FUNCTIONS
##############################################################################

def update_metrics_for_theme(theme, true_themes, classified_themes, tp, fp, fn, tn):
    if theme in true_themes and theme in classified_themes:
        tp[theme] += 1
    elif theme in true_themes and theme not in classified_themes:
        fn[theme] += 1
    elif theme not in true_themes and theme in classified_themes:
        fp[theme] += 1
    else:
        tn[theme] += 1


def get_metrics_for_each_theme(tp, fp, fn, tn, theme_counts, theme_correct_count):
    precisions = {}
    recalls = {}
    f1_scores = {}
    accuracies = {}

    for theme in tp.keys():
        if tp[theme] + fp[theme] > 0:
            precision = tp[theme] / (tp[theme] + fp[theme])
        else:
            precision = 0.0

        if tp[theme] + fn[theme] > 0:
            recall = tp[theme] / (tp[theme] + fn[theme])
        else:
            recall = 0.0

        if precision + recall > 0:
            f1 = 2 * (precision * recall) / (precision + recall)
        else:
            f1 = 0.0

        if theme_counts[theme] > 0:
            accuracy = theme_correct_count[theme] / theme_counts[theme]
        else:
            accuracy = 0.0

        precisions[theme] = precision
        recalls[theme] = recall
        f1_scores[theme] = f1
        accuracies[theme] = accuracy

    return precisions, recalls, f1_scores, accuracies


def get_all_metrics(tp, fp, fn, tn):
    all_tp = sum(tp.values())
    all_fp = sum(fp.values())
    all_fn = sum(fn.values())
    all_tn = sum(tn.values())

    total_predictions = all_tp + all_fp + all_fn + all_tn

    if all_tp + all_fp > 0:
        global_precision = all_tp / (all_tp + all_fp)
    else:
        global_precision = 0.0

    if all_tp + all_fn > 0:
        global_recall = all_tp / (all_tp + all_fn)
    else:
        global_recall = 0.0

    if global_precision + global_recall > 0:
        global_f1 = 2 * (global_precision * global_recall) / (global_precision + global_recall)
    else:
        global_f1 = 0.0

    if total_predictions > 0:
        global_accuracy = (all_tp + all_tn) / total_predictions
    else:
        global_accuracy = 0.0

    return global_precision, global_recall, global_f1, global_accuracy

