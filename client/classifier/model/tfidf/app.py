import json
import re

from generic_app import Service
from functions import load_json

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

        Train data percentage: 70\%.
        Test data percentage: 30\%.

        Steps:
            1. Clean the texts: add 'text_clean' to each dictionary,
                it is text but tokenized, stemmed, lemmatisated.
            2. Train using logistics regression.
            The model is a pipeline consisting of vectorization and classifier.
            3. Display the top words for each category and the precision
                on train and test datasets, and the taken time to train.

        Repeat the process for each vector of classification.
        """

        dataset: dict[str, dict[str, str | list[str]]] = load_json(input_file)

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
                          dataset: dict[str, str | list[str]]) -> None:
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
        print(output_file)

#############################################################################


#############################################################################

