# Dataset - or how to generate labelled data?

Train a model to categorize publications on given themes require
a large amount of labelled data, especially the models discussed
in the `/classification` section.

## Setup

There is not a "production mode" as it will not be used in production.
The only way to setup is to manually create a virtual environment:

```bash
# Created with Python3.13
cd dataset/

# <Environment variables>
cp .env.example .env
vim .env # edit the environment variables.
# </Environment variables>

# <Virtual environment>
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# </Virtual environment>
```

## How to use

1. Give some *DOI*s or *Openalex* IDs, they will be
the base of the dataset.

```bash
cp <file-containing-dois-or-openalex-ids> raw/base.txt
```

2. Then, enhance this base. For all ID in that file, find the related
papers of the given publication.

```bash
vim related.py # Change the name of the input file and output file.
               # Choose wether you want to extract DOIs or Openalex IDs,
               # by taking `related_dois()` or `related_openalex()`
               # in the main function.

source .venv/bin/activate
python related.py
```

NB: `outputFile` will be a *json* file.

In the `raw/` folder, you can already see how I used it.
I enhanced the dataset 3 times:

```
- depth=1: outputFile=./raw/r3mob_150725_depth_1.json,
inputFile=./raw/r3mob_150725.csv,
related_func=related_dois.

- depth=2: outputFile=./raw/r3mob_150725_depth_2.json,
inputFile=./raw/r3mob_150725_depth_1.csv,
related_func=related_openalex.

- depth=3: outputFile=./raw/r3mob_150725_depth_3.json,
inputFile=./raw/r3mob_150725_depth_2.csv,
related_func=related_openalex.
```

It respectively gave:

- depth=1: 1100 papers (not unique), around 600 unique papers.

- depth=2: 7280 papers (not unique), around 3500 unique papers.

- depth=3: 33280 papers (not unique), around 17000 unique papers.

And the retrieved papers from *Openalex* are still related to the
base given at the start, thanks to the *Openalex* classification algorithms.


However, it took a lot of time because sometimes DOIs are broken,
like this one `10.1175/1520-0450(1977)016<0237:pwviac>2.0.co;2`,
for my regex `r'10\.\d{4,9}/[\w.\-;()/:]+'`, this doi is
`10.1175/1520-0450(1977)016`. One way to improve this repository
is to find a better *regex*, which I tried but without success.
Among 12000 publications, I found around 80 publications with a broken *DOI*.

I checked into the source code of *Openalex* and they seem to make
only a comparison like that ``if DOI.startswith("10.") then ok else ko``,
which could fix the issue, but I'm not sure how to use it when trying to find
*DOI*s in a text.


Another idea is to use directly the web interface of *Openalex* to
download a set of papers related to specific topics, which I did
in the `request/` folder. However, you will have to parse it manually,
or merely to use the functions `related_dois()` or `related_openalex()`.

3. Processing: retrieve all the metadata related to the set of IDs.

```bash
vim processing.py # Change the name of the input file and output file.
source .venv/bin/activate
python processing.py
```

It merely calls the *Retriever* module to find the metadatas
related to all *Openalex* IDs in the input file, and stores it in a
*json* file. See the `processing/` directory to understand.


There are almost 30% of papers given by *Openalex* that have not a 
DOI. This is the case of books, and some web articles.
If there is no DOI, I don't take the paper.

4. Labelling: call the *llm* from the *Classifier* module
to categorize the papers.

Each paper in the `processing/file.json` file has its labels in the
`labelled/file.json` file, where the key is its *DOI*.

```bash
vim categorizing.py # Change the name of the input file and output file.
source .venv/bin/activate
python categorizing.py
```

### EOF

