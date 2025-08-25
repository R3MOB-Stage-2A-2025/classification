# Publication Classification Tool

The goal is to classify a text which is a concatenation of the *abstract*,
the *title* and some other *metadata* of a given scientific publication.

Example of a text to classify using the following format:

```json
"10.1016/s1570-6672(11)60225-0": {
  "title": "Traffic Flow Model for Staggered Intersection without Signal Lamp",
  "abstract": [],
  "topics": [
    "Traffic control and management",
    "Control and Systems Engineering",
    "Engineering",
    "Physical Sciences",
    "Transportation Planning and Optimization",
    "Transportation",
    "Social Sciences",
    "Social Sciences",
    "Traffic Prediction and Management Techniques",
    "Building and Construction",
    "Engineering",
    "Physical Sciences"
  ],
  "keywords": [
    "Traffic wave",
    "Signal timing",
    "Traffic conflict",
    "SIGNAL (programming language)",
    "Traffic bottleneck"
  ],
  "concepts": [
    "Intersection (aeronautics)",
    "Traffic flow (computer networking)",
    "Cellular automaton",
    "Traffic wave",
    "Signal timing",
    "Traffic congestion reconstruction with Kerner's three-phase theory",
    "Traffic conflict",
    "Queueing theory",
    "Computer science",
    "SIGNAL (programming language)",
    "Traffic optimization",
    "Process (computing)",
    "Traffic bottleneck",
    "Floating car data",
    "Simulation",
    "Real-time computing",
    "Transport engineering",
    "Traffic congestion",
    "Traffic signal",
    "Engineering",
    "Algorithm",
    "Computer network",
    "Operating system",
    "Programming language"
  ],
  "sustainable": [
    "Sustainable cities and communities"
  ]
}
```

```
Extracted DOI: 10.1016/s1570-6672(11)60225-0
```

Extracted keywords (text labellized by the categorizer/llm model):

```
Traffic Flow Model for Staggered Intersection without Signal Lamp, ,
Traffic control and management, Control and Systems Engineering, Engineering,
Physical Sciences, Transportation Planning and Optimization, Transportation,
Social Sciences, Social Sciences, Traffic Prediction and Management Techniques,
Building and Construction, Engineering, Physical Sciences, Traffic wave,
Signal timing, Traffic conflict, SIGNAL (programming language),
Traffic bottleneck, Intersection (aeronautics),
Traffic flow (computer networking), Cellular automaton, Traffic wave,
Signal timing, Traffic congestion reconstruction with Kerner's
three-phase theory, Traffic conflict, Queueing theory, Computer science,
SIGNAL (programming language), Traffic optimization, Process (computing),
Traffic bottleneck, Floating car data, Simulation, Real-time computing,
Transport engineering, Traffic congestion, Traffic signal, Engineering,
Algorithm, Computer network, Operating system, Programming language,
Sustainable cities and communities
```

Lemmatized text (text classified by the TFIDF model):

```
transportation intersection floating wave building signal science
reconstruction network bottleneck transport community computing realtime
physical timing threephase theory networking car algorithm lamp simulation
staggered engineering management congestion computer planning sustainable
prediction optimization aeronautics traffic construction conflict automaton
queueing control city model programming kerners system flow operating process
data without social cellular science technique language system
```

The categorizer model, which is a llm, is able to understand a sentence,
that's why I let him the whole text without preprocessing it.
In this example, there is not the abstract, but with the abstract it makes
more sense, because there are full sentences.

## Starting the Flask server in production mode

1. Edit the environment variables you wish:

```bash
cd backend/
cp .env.example .env
vim .env
```

Then you can use the specified *Dockerfile* with the *docker-compose.yml*
file in the root directory.

To understand each environment variable, you should go and read
the *README.md* file for each model section.

## Starting the Flask server in development mode

1. Use it for **python3.13**:

```bash
cd classification/backend/
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements_what_you_want.txt
```

2. Then do in another terminal:

```bash
cd classification/backend/
source .venv/bin/activate
python app.py
```

3. Tests only, use the frontend:

```bash
# Open another terminal and do this:
cd frontend/
npm install
npm run dev
```

## Understand the metrics

[***This article***](https://medium.com/analytics-vidhya/confusion-matrix-accuracy-precision-recall-f1-score-ade299cf63cd)
explains that *Accuracy*, *Precision*, *Recall* and *F1 Score* are
commonly used to evaluate the performance of a *Machine Learning Model*.

- *Accuracy*: number of correctly classified data instances over the
total number of data instances.

- *Precision*: From all the predictions, how many of them are correct?

- *Recall*: from all the publications related to it (that are True),
how many of them the model predicted it as True?

- *F1 Score*: takes into account both *precision* and *recall*. It's like an
average number between *precision* and *recall*.

These values are between 0 and 1, and tend to be 1.

[***This article***](https://www.kdnuggets.com/2023/01/micro-macro-weighted-averages-f1-score-clearly-explained.html)
explains well the difference between "micro", "macro", and "weighted".

- *micro*: there is no distinction of categories. It takes into account all
*True Positive* and *False Positive* from every categories/labels to calculate
the value of the parameter.

- *macro*: it is the classic average. If there are 3 categories/labels, the
*macro* value will be: ``( value_cat1 + value_cat2 + value_cat3 ) / 3``.

- *weighted*: it is the weighted average. It takes the propotion into account.
For 3 categories, proportion_cat1=0.3, proportion_cat2=0.5,
proportion_cat3=0.2: ``value_average = proportion_cat1 * value_cat1
+ proportion_cat2 * value_cat2 + proportion_cat3 * value_cat3``.

### What metrics should I look at?

The difference between *singlelabel* and *multilabel* is discussed in the
*TFIDF model* section.

1. For *singlelabel*, you should look at the **global accuracy**.

2. For *multilabel*, you should look at the **F1 score**.

If the categories/labels have very different proportions, you should
look at the **macro F1 score**. This one is a good example
[***right here***](https://stackoverflow.com/questions/66803701/micro-vs-macro-vs-weighted-f1-score).
Another example of mine:

```
Classification Report:
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

This is a *singlelabel* problem, so I look at the accuracy which is 75%,
although, the proportions (*support*) are very different, so I should also
look at the *macro F1 score* which is 54%. The labels with the most issues
are "Ferroviaire", "Fluvial/Maritime", "Transport par cables". The reason
is discussed in the *TFIDF model* section.

If the categories/labels have not very different proportions, you should look
at the **weighted F1 score**. It happens less frequently.

### EOF

