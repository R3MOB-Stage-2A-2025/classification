# Publication Classification Tool

This tool is a *keyword* analysis based on *TF-IDF* and *Similarity Cosine*.

The goal is to classify a text which is a concatenation of the *abstract*,
the *title* and some other *metadata* of a given scientific publication.

### Current model

Model based on [***sentence transformers***](https://github.com/UKPLab/sentence-transformers)
which is a *text embedding* framework based on [**SBERT***](www.sbert.net).

There are a lot a available models, however I chose the by default model
which is `all-MiniLM-L6-v2`.

So the current solution is to use an *unsupervised algorithm*. Indeed,
there are not currently enough labelized data to use a classifier based
on *TF IDF*.

Here is the insights based on the ``classification/backend/test.py`` file:

```bash
(.venv)  backend  >>  python tests.py
Number of abstracts: 128
Exact Match Count: 57

Global Precision: 58.45%
Global Recall: 71.18%
Global F1-Score: 64.19%
Global Accuracy: 89.45%
```

### Understand the metrics

[***This article***](https://medium.com/analytics-vidhya/confusion-matrix-accuracy-precision-recall-f1-score-ade299cf63cd)
explains that *Accuracy*, *Precision*, *Recall* and *F1 Score* are
commonly used to evaluate the performance of a *Machine Learning Model*.

- *Accuracy*: number of correctly classified data instances over the
total number of data instances.

- *Precision*: positive predictive value in classifying the data instances.

- *Recall*: sensitivity of true positive rate.

- *F1 Score*: takes into account both *precision* and *recall*.

These values are between 0 and 1, and tend to be 1.

## Parsing module

You will need to clone the *parsing module* using this command:

```bash
cd classification/
git submodule update --init --recursive
```

## Starting the Flask server

1. Use it for **python3.13**:

```bash
cd classification/backend/
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Be careful of you partition:

```bash
backend  >>  du -sch .venv/
6.2G    .venv/
6.2G    total
```

2. Then do in another terminal:

```bash
cd classification/backend/
python Server.py
```

3. Tests only, use the frontend:

```bash
# Open another terminal and do this:
cd frontend/
npm install
npm run dev
```

## Launch the classification tests

You can do this:

```bash
cd classification/backend
# (.venv) $
python tests.py
```

### Result observations

In the repertory `classification/backend/results`, you will find:

- **classification_results.json**: the details for each tested publication.

- **comparaison_results.json**: the metrics like *precision*, *accuracy*,
*recall* and *F1 scores*.

- **theme_summary.json** the total numbers of publications for each themes.

### EOF

