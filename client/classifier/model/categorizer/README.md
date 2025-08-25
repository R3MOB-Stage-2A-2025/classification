# Client - Sentence Transformers from Hugging Face

A classification model mostly used to labellize a dataset.

## Development mode

Using *Python 3.13*:

```bash
cd client/classifier
python -m venv .venv
source .venv/bin/activate

pip install -r requirements/flask_requirements.txt
pip install -r requirements/categorizer_requirements.txt

# Edit .env variables.
vim .env

# In the .env file:
CLASSIFIER_CATEGORIZER_USE=TRUE
# If you also do `CLASSIFIER_TFIDF_USE==TRUE`, it will choose by default
# TFIDF, so you want to put it to FALSE.

python app.py
```

It is not necessary to use the *miscellaneous* packages.
Their goal is to preprocess text. This model is a **LLM**, it can
understand sentences. So it is better to give it directly sentences,
not formatted.

Be careful of your partition:

```bash
backend  >>  du -sch .venv/
6.2G    .venv/
6.2G    total
```

## The model used

Model based on [***sentence transformers***](https://github.com/UKPLab/sentence-transformers)
which is a *text embedding* framework based on [***SBERT***](www.sbert.net).

There are a lot a available models, however I chose the by default model
which is `all-MiniLM-L6-v2`.

This one is used to labellize data, it used in the `dataset/` folder.

### Edit the labels

In the `data/labels.json`, you will find some french words, followed by a list
of english words.

1. Each key of this file is a **vector of classification**, example:
*"challenges", "themes", "scientificThemes"*, etc..
For each vector of classification there will be a model trained on it.

2. They contain some labels/categories. for example, "challenges" can take the
value of "Economiques", "Environnementaux", "Sociétaux", "Stratégiques",
"Technologiques".

3. Each label/category will be emphasized with some english keywords related to
it. For instance, the label "Economique", related to the vector of
classification named **"challenges"**, has the keywords:

```
Economic impact, Cost-benefit analysis, Funding, Investment, Market,
Business model, Profitability, Budget, Financial sustainability,
Monetary policy, Price elasticity, Return on investment, Economic growth,
Infrastructure costs
```

These keywords are needed by the *categorizer* model (llm) to understand
what could exactly contain each category.

These labels should be chosen wisely. A word that is not related to the label
could lead to big problems. For instance, for the vector of classification
named *"mobilityTypes"*, for the label/category named *"Fluvial/Maritime"*,
the **chosen words** for the *categorizer* were:

```
Water transport, Maritime transport, Shipping, Port, Harbor, Freight ship,
Inland waterways, Sea route, Cargo vessel, Maritime logistics, Navigation,
Ferry, Container ship, Marine traffic, Shipyard, Oceanography
```

and for no reason, I don't even know how this is possible, but the
*categorizer* (TFIDF model) predicted on the training dataset these words
for this category (top words from the publications related to this label):

```
development, chemistry process, machine psychology, archaeology,
social computing, underwater, chain, aspect, humanitarian, port, flow,
supply, physic engineering, type, water, ocean, marine, container,
maritime, ship
```

I think we can all agree that there is a bias here.
The *TFIDF* model is not able to predict (Recall of 0.34) that a
publication is related to "Fluvial/Maritime", and when it predicts that a
publication is related to "Fluvial/Maritime", there is only 35%
of chance (Precision) that this prediction is true:

```
Vector of classification: mobilityTypes
Total number of publications: N=11828
Number of words in the vocabulary (max_features): C=10000
Range of ngram: ngram_range=(1, 2)
Type of labellisation: singlelabel
Algorithm used (only for multilabel):
    algo=LinearSVC(class_weight='balanced')
Algorithm used (only for singlelabel):
    algo=LogisticRegression(class_weight='balanced')
Classification Report :

======================================================
                      precision    recall  f1-score   support

              Aérien       0.56      0.54      0.55       134
         Ferroviaire       0.37      0.35      0.36       105
    Fluvial/Maritime       0.35      0.34      0.35       180
               Other       0.90      0.83      0.86      2367
             Routier       0.61      0.74      0.67       554
Transport par cables       0.39      0.52      0.44       209

            accuracy                           0.75      3549
           macro avg       0.53      0.55      0.54      3549
        weighted avg       0.77      0.75      0.75      3549
```

If we check the difference between the true numbers of publications
related to this label, and the its "support" from the classficiation
report, we can see a difference of 0.3 * 635 - 180 = 10.5
(0.3 is because the *test dataset* is composed of 30% of the true dataset):

```
Number of unique categories: C=6
Split by categories:
Aérien: 460
Ferroviaire: 373
Fluvial/Maritime: 635
Routier: 1892
Transport par cables: 726
Other: 7887
```

"Routier" has a difference of 14, and "Transport par cables" has a difference
of -11.

For "Routier":

```
Chosen words (data/labels.json):

Road transport, Highway, Truck, Bus, Car, Traffic, Road infrastructure,
Public transport, Motorway, Urban mobility, Logistics vehicle,
Freight transport, Personal vehicle, Road network, Toll road

Words found by TFIDF (top words):

innovation, path, truck, automation, decision, control, system, service, driver,
city, infrastructure, network, business, planning, automotive, transport,
road, transportation, traffic, vehicle
```

For "Transport par cables":

```
Chosen words (data/labels.json):

Cable transport, Cable car, Aerial lift, Funicular, Gondola lift, Ropeway,
Urban cable transport, Mountain transport, Suspended transport, Teleferic,
Passenger cableway, Inclined elevator

Words found by TFIDF (top words):

robotic, coil navigation, artificial wide, electrical clean,
electronic engineering, electronic, mechanic, cable, effect,
air energy, crosswind, slice, cut, multipath, robot, aerospace, design,
mechanical, type
```

We can see here that "Transport par cables" is more related to robots and
some generic stuffs like *"coil nagivation"* than actually *"Cable transport"*.

It does not seem to be only a problem of overfitting, because the TFIDF model
predicted only those words for "Other" (90% Precision for "Other"):

```
humanity, study, propose, difference, ecology, radiation, server, molecular,
thermal, property, thermodynamics, distribution, present, psychology, show,
result, material, cloud, rate, temperature
```

So I think the *categorizer* (llm) has at least 3 bias:

1. *"Transport par cables"* is also taking all publications related to robotics.

2. *"Routier"* has the word *transport* as a top word. This label seems to
take publications from other labels related to transport (difference of +14).

3. *"Fluvial/Maritime"* takes unecessary publications related to chemistry.

### Duck tape to make the model more efficent

The file `data/sentence_transformers_parameters.json` contains:

```json
{
  "challenges": {
    "precision": 0.05,
    "threshold": 0.1
  },
  "themes": {
    "precision": 0.05,
    "threshold": 0.2
  },
  "scientificThemes": {
    "precision": 0.4,
    "threshold": 0.1
  },
  "mobilityTypes": {
    "precision": 0.02,
    "threshold": 0.2
  },
  "axes": {
    "precision": 0.009,
    "threshold": 0.1,
    "parent": "mobilityTypes"
  },
  "usages": {
    "precision": 0.009,
    "threshold": 0.25,
    "parent": "mobilityTypes"
  }
}
```

For each vector of classification
(`challenges`, `axes`, `mobilityTypes`, ...), there are:

1. "threshold": at first (before classification),
all the keywords from all the labels are gathered into
one big label, which can represent the set of what the current
model can classify.
The threshold is the min value (abs value) of the result
of the classification model between the prompt
and this big label.
It prevents from bias, the classification is made only if
the prompt could be related to the set of labels from
the current vector of classification.

2. "precision": the max gap (abs value) between the top score
and the score of another possible label. There are at most
3 labels returned.
One label is returned when the precision is low.
2 or 3 labels are returned when the precision is high.

3. "parent" (Optional): The key of the vector of classification
that is related to the current one.

Example: if we want to classify by `usages`
(related to cars and traffic) but the classification by
`transport` returned nothing (the publication does not
talk about transport), then the `usages` will also
return nothing, because it is not relevant to classify
by `usages`.
It prevents from classifying something that is not talking
about transport, when the vector of classification is
about to be biased.

### EOF

