import json
import re

from generic_app import Service
from functions import load_json, preprocess_text

# <Machine Learning>
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelBinarizer
# </Machine Learning>

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

        # <Split by categories>
        pub_sorted_by_catego: dict[str, list[dict[str, str | list[str]]]] =\
            self._get_by_categories(classification_vector_name, publications)

        nb_unique_categories: int =\
            len(pub_sorted_by_catego.items())

        split_by_categories: list[str] = [
            catego + ": " + str(len(publications))\
            for catego, publications in pub_sorted_by_catego.items()
        ]
        # </Split by categories>

        # <Display>
        head_dataset: list[str] = []
        for publication in publications[:5]:

            catego_suffix: str =\
                "" if len(publication['categories']) <= 20 else " ..."

            text_suffix: str =\
                "" if len(publication['text']) <= 20 else " ..."

            head_dataset.append(str(json.dumps({
                'categories': publication['categories'][:20] + catego_suffix,
                'text': publication['text'][:20] + text_suffix
            }))
            )

        print(f'\n\
#############################################################################\n\
Beginning the training for TF IDF...\n\
Vector of classification: {classification_vector_name}\n\
Total number of publications: N={len(publications)}\n\
#############################################################################\n\
Number of unique categories: C={nb_unique_categories}\n\
Split by categories:\n\
{'\n'.join(split_by_categories)}\n\
#############################################################################\n\
head(Dataset):\n\
{'\n'.join(head_dataset)}\n\
#############################################################################\n\
\
        ')
        # </Display>

        # <Format the texts>
        for publication in publications:
            text: str = publication.get('text', "")

            dataframe: dict[str, list[str | list[str]]] =\
                preprocess_text(text)
            text_clean: str = ' '.join(dataframe['STOP-WORDS'][0])

            publication['text_clean'] = text_clean
        # </Format the texts>

        # <To get only 1 category per publication>
        single_catego_pub: list[dict[str, str]] = []

        for publication in publications:
            categories: list[str] =\
                json.loads(publication.get('categories', ""))

            if 2 <= len(categories):
                for category in categories:
                    text: str = publication.get('text', "")
                    text_clean: str = publication.get('text_clean', "")

                    single_catego_pub.append({
                        'categories': category,
                        'text': text,
                        'text_clean': text_clean
                    })
            else:
                single_catego_pub.append(publication)
        # </To get only 1 category per publication>

        # <Split into Train and Test data>

        # the column `text_clean`:
        X: list[str] =\
            [ pub.get('text_clean', "") for pub in single_catego_pub ]
        # the column `categories`:
        y: list[str] =\
            [ pub.get('categories', "") for pub in single_catego_pub ]
        # copy of y:
        stratify: list[str] = [ elt for elt in y ]

        X_train, X_test, y_train, y_test =\
            train_test_split(X, y, test_size=0.3, random_state=42,
                             stratify=stratify)

        # <Display>
        display_percentage_train_test_data: list[dict[str, float]] = []
        for category in pub_sorted_by_catego.keys():
            y_count: int = y.count(category)
            y_train_count: int = y_train.count(category)

            display_percentage_train_test_data.append({
                category:\
                y_train_count / y_count if y_count != 0 else -1
            })

        display_percentage_train_test_data_to_display: list[str] = {
            str(json.dumps(dictionary))\
            for dictionary in display_percentage_train_test_data
        }

        print(f'\
Split into Train and Test data:\n\
{'\n'.join(display_percentage_train_test_data_to_display)}\n\
#############################################################################\n\
        ')
        # </Display>

        # </Split into Train and Test data>

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
            for catego in result:
                categories_in_ascii: list[str] =\
                    json.loads(publication.get('categories', ""))

                if catego in categories_in_ascii:
                    result[catego].append(publication)

        return result

    #########################################################################

#############################################################################



#############################################################################

