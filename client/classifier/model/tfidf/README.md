# Client - TF IDF

A classification model trained on the dataset `data/data.json`.

## Development mode

Using *Python 3.13*:

```bash
cd client/classifier
python -m venv .venv
source .venv/bin/activate

pip install -r requirements/flask_requirements.txt
pip install -r requirements/tfidf_requirements.txt
pip install -r requirements/miscellenaous_requirements.txt

# Edit .env variables.
vim .env

# In the .env file:
CLASSIFIER_TFIDF_USE=TRUE
CLASSIFIER_TFIDF_INPUT_FILE=data/data.json
CLASSIFIER_TFIDF_TEST_SIZE=0.3
CLASSIFIER_TFIDF_MAX_FEATURES=10000
CLASSIFIER_TFIDF_NGRAM_RANGE=(1, 2)
CLASSIFIER_TFIDF_MULTILABEL_ALGORITHM=SVC # SVC or SGDC or LOGISTIC.
CLASSIFIER_TFIDF_CLASS_WEIGHT=balanced
CLASSIFIER_TFIDF_IGNORE_WARNINGS=TRUE
CLASSIFIER_TFIDF_SAVE_TEXT_CLEAN=TRUE

# <Tokenizer + Embeddings>
CLASSIFIER_MISCELLANEOUS_USE=TRUE
NLTK_DIRECTORY=./.venv/nltk_data
SPACY_MODEL=en_core_web_lg
# </Tokenizer + Embeddings>
```

Moreover,
`CLASSIFIER_TFIDF_USE==TRUE` ==> `CLASSIFIER_MISCELLANEOUS_USE==TRUE`.

## Environment variables

1. `CLASSIFIER_TFIDF_INPUT_FILE` must be generated using the script called
`dataset/ready_to_classify`.

2. `CLASSIFIER_TFIDF_MAX_FEATURES` is the maximum number of words in the
vocabulary. It takes the 10000 words that appear the most in the given dataset.
`CLASSIFIER_TFIDF_MAX_FEATURES > 10000` is not necessary.

3. `CLASSIFIER_TFIDF_NGRAM_RANGE`, see the official doc of
***sklearn.TfidfVectorizer()***:

```
ngram_range : tuple (min_n, max_n), default=(1, 1)
    The lower and upper boundary of the range of n-values for different
    n-grams to be extracted. All values of n such that min_n <= n <= max_n
    will be used. For example an ``ngram_range`` of ``(1, 1)`` means only
    unigrams, ``(1, 2)`` means unigrams and bigrams, and ``(2, 2)`` means
    only bigrams.
```

4. `CLASSIFIER_TFIDF_MULTILABEL_ALGORITHM` is only used for multilabel.
The singlelabel classifier will always take the **LogisticRegression()** from
``sklearn.linear_model``.

- "SVC": ``sklearn.svm.LinearSVC()``, see the doc
[***right here***](https://scikit-learn.sourceforge.net/stable/modules/generated/sklearn.svm.LinearSVC.html).

- "SGDC": Stochastic Gradient Descent.

5. `CLASSIFIER_TFIDF_CLASS_WEIGHT`: you can either choose "auto" or "balanced".
See the official doc of ``sklearn.linear_model``:

```
class_weight : dict or 'balanced', default=None
    Set the parameter C of class i to ``class_weight[i]*C`` for
    SVC. If not given, all classes are supposed to have
    weight one.
    The "balanced" mode uses the values of y to automatically adjust
    weights inversely proportional to class frequencies in the input data
    as ``n_samples / (n_classes * np.bincount(y))``.
```

Unfortunately, for now, it does not support the use of a dictionary.

6. `CLASSIFIER_TFIDF_SAVE_TEXT_CLEAN`: a cache feature to save the preprocessed
texts (formatted texts) directly in the `CLASSIFIER_TFIDF_INPUT_FILE` file.
Format the texts of the dataset is the longest task of this classification.

### You can not save your model

It is theoretically possible to save the vocabulary of your trained model.
By default, *sklearn* recommends to use *Pickle*, which is a very exploitable
*python* package.

I will not use *Pickle* in this project as it is vulnerable to a lot of
exploits. I did not take the time to find an alternative of *Pickle* either.

Besides, the feature of saving formatted texts is very important insofar as
the models are trained each time the *Flask* server is launched.
For all the models, it took me about 2minutes to train them
(without text formatting).

### Choose between multilabel and singlelabel

Edit the `data/tfidf_parameters.json` file.

### EOF

