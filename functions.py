import json
import spacy
import nltk

# This one is searching in the `nltk_data/` dir.
from nltk.corpus import stopwords, wordnet

from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer

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

# Charger un modèle de spaCy
nlp = spacy.load(SPACY_MODEL)

# Charger les fichiers JSON
def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


### FONCTIONS DE PRETRAITEMENTS ###


# Prétraitement du texte avec lemmatisation et suppression des stop-words
def preprocess_text(text):
    
    # Charger les stopwords en anglais
    stop_words = set(stopwords.words('english'))
    
    # Tokeniser le texte
    tokens = nltk.word_tokenize(text.lower())
    
    # Lemmatiser chaque mot et retirer les stopwords
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens if token.isalpha() and token not in stop_words]
    
    return tokens


# Prétraitement des mots-clés
def preprocess_keywords(keywords):
    lemmatizer = WordNetLemmatizer()
    return {lemmatizer.lemmatize(keyword) for keyword in keywords}


# Fonction pour obtenir les synonymes d'un mot (WordNet)
def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    return synonyms


# Extension des mots-clés avec des synonymes
def expand_keywords_with_synonyms(expanded_keywords, theme, keywords):
    for keyword in keywords:
        expanded_keywords[theme].update(get_synonyms(keyword))
    return expanded_keywords


# Prétraitement et Extension des mots-clés avec des synonymes
def expand_and_preprocess_keywords(themes_keywords):
    
    expanded_keywords = {}
    
    for theme, keywords in themes_keywords.items():

        # Prétraiter les mots-clés
        keywords = preprocess_keywords(keywords)
        
        expanded_keywords[theme] = set(keywords)
        
        # Etendre les mots-clés avec des synonymes
        """ expanded_keywords = expand_keywords_with_synonyms(expanded_keywords, theme, keywords) """
    
    return expanded_keywords



### FONCTIONS DE CLASSIFICATION ###


# Fonction pour classifier un abstract selon les mots-clés 
def classify_abstract(abstract_text, themes_keywords):
    
    # Prétraiter l'abstract
    abstract_text = preprocess_text(abstract_text)
    
    # Prétraiter et Étendre les mots-clés avec des synonymes
    themes_keywords = expand_and_preprocess_keywords(themes_keywords)
    
    abstract_themes = []
    
    for theme, keywords in themes_keywords.items():
        for keyword in keywords:
            if keyword.lower() in abstract_text:
                abstract_themes.append(theme)
                break
    
    return abstract_themes 


# Vectorisations de l'abstract avec SpaCy (modèle d'embeddings)
def classify_abstract_by_spaCy(abstract_text, themes_keywords):
    
    # Prétraiter l'abstract
    abstract_text = ' '.join(preprocess_text(abstract_text))
    
    # Prétraiter et Étendre les mots-clés avec des synonymes
    themes_keywords = expand_and_preprocess_keywords(themes_keywords)
    
    doc = nlp(abstract_text)
    abstract_themes = []
    for theme, keywords in themes_keywords.items():
        for keyword in keywords:
            keyword_vec = nlp(keyword)
            if doc.similarity(keyword_vec) > 0.85: # Seuil à ajuster
                abstract_themes.append(theme)
                break
    return abstract_themes


# Créer une représentation TF-IDF de l'abstract
def classify_abstract_TF_IDF(abstract_text, themes_keywords):
    
    # Prétraiter l'abstract
    abstract_text = ' '.join(preprocess_text(abstract_text))
    
    # Prétraiter et Étendre les mots-clés avec des synonymes
    themes_keywords = expand_and_preprocess_keywords(themes_keywords)
    
    vectorizer = TfidfVectorizer()
    abstract_tfidf = vectorizer.fit_transform([abstract_text])
    abstract_themes = []
    for theme, keywords in themes_keywords.items():
        theme_tfidf = vectorizer.transform(keywords)
        similarity = (abstract_tfidf * theme_tfidf.T).toarray()
        if similarity.max() > 0.15: # Seuil à ajuster
            abstract_themes.append(theme)
    return abstract_themes


# Combination des techniques TF-IDF et d'embeddings
def classify_abstract_combined(abstract_text, themes_keywords):
    # Prétraiter l'abstract
    abstract_text = ' '.join(preprocess_text(abstract_text))

    # Prétraiter et Étendre les mots-clés avec des synonymes
    themes_keywords = expand_and_preprocess_keywords(themes_keywords)

    # Représentation TF-IDF
    vectorizer = TfidfVectorizer()
    all_keywords = [keyword for keywords in themes_keywords.values() for keyword in keywords]
    vectorizer.fit(all_keywords + [abstract_text])
    abstract_tfidf = vectorizer.transform([abstract_text])

    abstract_themes = []

    for theme, keywords in themes_keywords.items():
        theme_tfidf = vectorizer.transform(keywords)
        tfidf_similarity = (abstract_tfidf * theme_tfidf.T).toarray().max()

        # Représentation SpaCy (embeddings)
        doc = nlp(abstract_text)
        theme_similarity = 0
        for keyword in keywords:
            keyword_vec = nlp(keyword)
            theme_similarity = max(theme_similarity, doc.similarity(keyword_vec))

        # Combiner les similarités
        combined_similarity = (tfidf_similarity + theme_similarity) / 2

        if combined_similarity > 0.45:  # Seuil à ajuster
            abstract_themes.append(theme)

    return abstract_themes



### FONCTIONS DE GESTION DE METRIQUES ###


# Fonction pour mettre à jour les compteurs (TP, FP, FN, TN)
def update_metrics_for_theme(theme, true_themes, classified_themes, tp, fp, fn, tn):
    if theme in true_themes and theme in classified_themes:
        tp[theme] += 1
    elif theme in true_themes and theme not in classified_themes:
        fn[theme] += 1
    elif theme not in true_themes and theme in classified_themes:
        fp[theme] += 1
    else:
        tn[theme] += 1


# Fonction pour obtenir les métriques par thème : précision, rappel, F1 et exactitude
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


# Fonction pour obtenir les métriques globales : précision, rappel, F1 et exactitude
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

