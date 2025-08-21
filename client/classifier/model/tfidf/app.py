import json
import re
import ast
from datetime import datetime
import random
import numpy as np
import pandas as pd

from generic_app import Service
from functions import load_json, preprocess_text

# <Machine Learning>
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, classification_report
from sklearn.metrics import hamming_loss, jaccard_score
# </Machine Learning>

# <Ignore warnings>, most of the time it's useless.
import warnings

warnings.filterwarnings('ignore')
# </Ignore warnings>

class Tfidf(Service):
    def __init__(self, labels: dict[str, dict[str, list[str]]],
                 precisions: dict[str, dict[str, float | str]]):
        """
        :param labels: see `Service()`.
        :param precisions: see `Service()`.
        """

        self.name = "TFIDF"
        super().__init__(labels=labels, precisions=precisions)

    def prompt(self, prompt: str) -> dict[str, str]:
        """
        :param prompt: it is a text, see `Classifier.prompt_generic()`.
        :return: The classification result over all the labels,
            see `Classifier.prompt_generic()`.


        """
        def func_prompt(prompt):
            return {}

        return self.generic_prompt(func_prompt, prompt)

    def train(self, output_file: str, input_file: str) -> None:
        """
        A Function to train the model.

        :param output_file: The path of the file that will store the model.
            This path is about to be extended with the name of the
            vector of classification because there will be a unique
            model for each of them. './model_tfidf' is fine.

        :param input_file: The path of the file with the labelled metadata.
            This one is a json file like this:

    ```json
    {
        'classification_vector_name (example: challenges, themes, etc..)': [
            { 'categories': ["tech"], 'text': "Once upon a time..." },
            { 'categories': ["business"], 'text': "In the Wilderness..." },
            { 'categories': ["sport"], 'text': "By Hugo Montenegro..." },
            { 'categories': ["sport"], 'text': "And Sergio Leone..." },
            { 'categories': ["entertainment"], 'text': "And Me..." }
        ],
        ...
    }
    ```

        Train data percentage: 70%.
        Test data percentage: 30%.

        Steps:
            1. Clean the texts: add 'text_clean' to each dictionary,
                it is text but tokenized, stemmed, lemmatisated.
            2. Train using logistics regression.
            The model is a pipeline consisting of vectorization and classifier.
            3. Display the top words for each category and the precision
                on train and test datasets, and the taken time to train.

        Repeat the process for each vector of classification.
        """

        dataset: dict[str, dict[str, str | list[dict]]] = load_json(input_file)

        # <Display>
        print("Formatting the texts, please wait...")
        # </Display>

        # <Format the texts>
        for publications in dataset.values():
            for publication in publications:
                text: str = publication.get('text', "")

                dataframe: dict[str, list[str | list[str]]] =\
                    preprocess_text(text)
                text_clean: str = ' '.join(dataframe['STOP-WORDS'][0])

                publication['text_clean'] = text_clean
        # </Format the texts>

        for vector_of_classification in self._labels:

            output_file_current: str = output_file\
                + "_"\
                + vector_of_classification\
                + ".pt"

            dataset_current = {
                vector_of_classification:\
                    dataset.get(vector_of_classification, {})
            }

            self._train_a_unique_label(output_file_current, dataset_current)

    def _train_a_unique_label(self, output_file: str,
                          dataset: dict[str, str | list[dict]]) -> None:
        """
        :param output_file: Something like `./model_tfidf_axes.pt`.
        :param dataset: this one is a json file like this:

    ```json
    {
        'classification_vector_name (example: challenges, themes, etc..)': [
            { 'categories': ["tech"], 'text': "Once upon a time..." },
            { 'categories': ["business"], 'text': "In the Wilderness..." },
            { 'categories': ["sport"], 'text': "By Hugo Montenegro..." },
            { 'categories': ["sport"], 'text': "And Sergio Leone..." },
            { 'categories': ["entertainment"], 'text': "And Me..." }
        ]
    }
    ```
        """

        classification_vector_name: str = ''.join(dataset.keys())
        publications: list[dict[str, str | list[str]]] =\
            dataset.get(classification_vector_name, [])

        # <Transform it into a pandas dataset>
        publications_df = pd.DataFrame(publications)

        publications_df['categories'] =\
            publications_df['categories'].apply(lambda x: ast.literal_eval(x))
        # </Transform it into a pandas dataset>

        # <Split by categories>
        pub_sorted_by_catego: dict[str, list[dict[str, str | list[str]]]] =\
            self._get_by_categories(classification_vector_name, publications)

        split_by_categories: list[str] = [
            catego + ": " + str(len(publications))\
            for catego, publications in pub_sorted_by_catego.items()
        ]
        # </Split by categories>

        # <Display>
        head_dataset = publications_df.head()
        nb_total_publications = len(publications_df)
        nb_unique_categories: int =\
            len(pub_sorted_by_catego.items())

        print(f'\n\
#############################################################################\n\
Beginning the training for TF IDF...\n\
Vector of classification: {classification_vector_name}\n\
Total number of publications: N={nb_total_publications}\n\
#############################################################################\n\
Number of unique categories: C={nb_unique_categories}\n\
Split by categories:\n\
{'\n'.join(split_by_categories)}\n\
#############################################################################\n\
head(Dataset):\n\
{head_dataset}\n\
\
        ')
        # </Display>

        # <Model Initialization>
        vectorizer_tfidf =\
            TfidfVectorizer(max_features=10000, ngram_range=(1,2))
        X = vectorizer_tfidf.fit_transform(publications_df['text_clean'])
        # </Model Initialization>

        # <Split into Train and Test data>
        y_numpy = publications_df['categories']
        multilabel = MultiLabelBinarizer()
        y = multilabel.fit_transform(y_numpy)

        # <The shuffle of sklearn>
        X_train, X_test, y_train, y_test =\
            train_test_split(X, y, test_size=0.3, random_state=42)
                                                #, stratify=y)
        # </The shuffle of sklearn>

        # <Display>
        display_percentage_train_test_data: list[dict[str, float]] = []

        ind_catego: int = 0
        for category in multilabel.classes_:
            y_count: int = sum(y[:, ind_catego])
            y_train_count: int =\
                sum(y_train[:, ind_catego])

            display_percentage_train_test_data.append({
                f'({ind_catego}) ' + category:\
                y_train_count / y_count if y_count != 0 else -1,
            })

            ind_catego += 1

        display_percentage_train_test_data_to_display: list[str] = {
            str(json.dumps(dictionary))\
            for dictionary in display_percentage_train_test_data
        }

        print(f'\
#############################################################################\n\
Percentage of training data:\n\
{'\n'.join(display_percentage_train_test_data_to_display)}\n\
        ')
        # </Display>

        # </Split into Train and Test data>

        # <Fit to the training data>
        algorithms: list = [
            LogisticRegression(solver='lbfgs', class_weight='balanced'),
            SGDClassifier(class_weight='balanced'),
            LinearSVC(class_weight='balanced')
        ]
        classifier_tfidf =\
            OneVsRestClassifier(algorithms[2])

        start_time = datetime.now()
        classifier_tfidf.fit(X_train, y_train)
        end_time = datetime.now()

        training_time_tfidf = (end_time - start_time).total_seconds()
        # </Fit to the training data>

        # <Results>
        predicted_train_tfidf = classifier_tfidf.predict(X_train)
        accuracy_train_tfidf = accuracy_score(y_train, predicted_train_tfidf)

        predicted_test_tfidf = classifier_tfidf.predict(X_test)
        accuracy_test_tfidf = accuracy_score(y_test, predicted_test_tfidf)
        accuracy_report =\
            classification_report(y_test, predicted_test_tfidf)

        hamming_train: float = hamming_loss(y_train, predicted_train_tfidf)
        hamming_test: float = hamming_loss(y_test, predicted_test_tfidf)

        jaccard_train: float =\
            jaccard_score(y_train, predicted_train_tfidf, average='micro')
        jaccard_test: float =\
            jaccard_score(y_test, predicted_test_tfidf, average='micro')
        # </Results>

        # <Display>
        print(f'\
#############################################################################\n\
Accuracy Training data: {accuracy_train_tfidf}\n\
Accuracy Test data: {accuracy_test_tfidf}\n\
Hamming Loss on Train data: {hamming_train}\n\
Hamming Loss on Test data: {hamming_test}\n\
Jaccard Score (micro) on Train data: {jaccard_train}\n\
Jaccard Score (micro) on Test data: {jaccard_test}\n\
Training time: {training_time_tfidf}\n\
#############################################################################\n\
Classification Report:\n\
======================================================\n\
{accuracy_report}\n\
        ')

        classes = classifier_tfidf.classes_
        estimators = classifier_tfidf.estimators_

        print("(categories x vocabulary size):", estimators[0].coef_.shape)
        print(80 * "-")

        NN = 20
        voc = vectorizer_tfidf.vocabulary_
        inv_voc = {v: k for k, v in voc.items()}

        for n, (cls, est) in enumerate(zip(classes, estimators)):
            coef = est.coef_[0]  # shape (1, vocab_size)
            top_words = np.argsort(coef)[-NN:]

            t = str(cls) + ": "

            for i in range(NN):
                t += inv_voc[top_words[i]]

                if i != NN - 1:
                    t += ", "

            print(t)
        # </Display>

    #########################################################################
    ## Sort the publications by categories.
    #########################################################################

    def _get_by_categories(self, classification_vector_name: str,\
                           publications: list[dict[str, str | list[str]]])\
                            -> dict[str, list[dict[str, str | list[str]]]]:
        result = {
            catego: [] for catego\
            in self._labels.get(classification_vector_name)
        }

        # <Manually add the extra class>
        result['Other'] = []
        # </Manually add the extra class>

        for publication in publications:
            categories_in_ascii: list[str] =\
                json.loads(publication.get('categories', ""))

            publication['categories'] = categories_in_ascii

        for publication in publications:
            for catego in result:
                categories_pub: list[str] = publication.get('categories', "")

                if catego in categories_pub:
                    result[catego].append(publication)

        return result

    #########################################################################

#############################################################################



#############################################################################

