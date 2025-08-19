import json
import re

from generic_app import Service

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

    def train(self, output_file: str = "./model.pt", input_file: str) -> None:
        """
        A Function to train the model.

        :param output_file: The path of the file that will store the model.
        :param input_file: The path of the file with the labelled metadata.
            This one is a json file like this:

            ```
            {
            'label_name (example: challenges, themes, etc..)': [
                    { 'category': "tech", 'text': "Once upon a time..." },
                    { 'category': "business", 'text': "In the Wilderness..." },
                    { 'category': "sport", 'text': "By Hugo Montenegro..." },
                    { 'category': "sport", 'text': "And Sergio Leone..." },
                    { 'category': "entertainment", 'text': "And Me..." }
                ]
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
        """



#############################################################################


#############################################################################

