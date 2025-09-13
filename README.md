# Classification repository

From a given paper *DOI*, or the title of its book, or the name of one
of its authors, this service will find related papers, keywords attached 
to these papers, and all the non-copyrighted metadata that you will
ever need.

Example:

1. The *Retriever* module finds your paper, let's take
`DOI=j.marpol.2022.105310`:

```json
{
  "title": [
    "Decarbonisation of the shipping sector – Time to ban fossil fuels?"
  ],
  "abstract": null,
  "TL;DR": null,
  "DOI": "10.1016/j.marpol.2022.105310",
  "URL": "https://doi.org/10.1016/j.marpol.2022.105310",
  "OPENALEX": "https://openalex.org/W4306644972",
  "type": "journal-article",
  "ISSN": [
    "0308-597X",
    "1872-9460"
  ],
  "publisher": "Elsevier BV",
  "publication_date": "2022-10-17",
  "container-title": [
    "Marine Policy"
  ],
  "container-url": [
    "https://doi.org/10.1016/j.marpol.2022.105310"
  ],
  "author": [
    {
      "given": "Judith van",
      "family": "Leeuwen",
      "ORCID": "https://orcid.org/0000-0002-7750-1255",
      "OPENALEX": "https://openalex.org/A5059660065",
      "affiliation": [
        {
          "name": "Wageningen University & Research",
          "openalex": "https://openalex.org/I913481162",
          "ror": "https://ror.org/04qw24q55",
          "country": "NL"
        }
      ]
    },
    {
      "given": "Jason",
      "family": "Monios",
      "ORCID": "https://orcid.org/0000-0002-4916-9718",
      "OPENALEX": "https://openalex.org/A5004879798",
      "affiliation": [
        {
          "name": "Kedge Business School",
          "openalex": "https://openalex.org/I51205905",
          "ror": "https://ror.org/00wk3s644",
          "country": "FR"
        }
      ]
    }
  ],
  "reference": [],
  "related": [
    {
      "key": 1,
      "OPENALEX": "https://openalex.org/W955932470"
    },
    {
      "key": 2,
      "OPENALEX": "https://openalex.org/W4362733811"
    },
    {
      "key": 3,
      "OPENALEX": "https://openalex.org/W2976090524"
    },
    {
      "key": 4,
      "OPENALEX": "https://openalex.org/W2916704920"
    },
    {
      "key": 5,
      "OPENALEX": "https://openalex.org/W2808752493"
    },
    {
      "key": 6,
      "OPENALEX": "https://openalex.org/W2748270136"
    },
    {
      "key": 7,
      "OPENALEX": "https://openalex.org/W2114034199"
    },
    {
      "key": 8,
      "OPENALEX": "https://openalex.org/W2086169669"
    },
    {
      "key": 9,
      "OPENALEX": "https://openalex.org/W1858249912"
    },
    {
      "key": 10,
      "OPENALEX": "https://openalex.org/W1507007465"
    }
  ],
  "topics": [
    {
      "id": "https://openalex.org/T12126",
      "display_name": "Maritime Transport Emissions and Efficiency",
      "score": 1,
      "subfield": {
        "id": "https://openalex.org/subfields/2305",
        "display_name": "Environmental Engineering"
      },
      "field": {
        "id": "https://openalex.org/fields/23",
        "display_name": "Environmental Science"
      },
      "domain": {
        "id": "https://openalex.org/domains/3",
        "display_name": "Physical Sciences"
      }
    },
    {
      "id": "https://openalex.org/T11223",
      "display_name": "Maritime Ports and Logistics",
      "score": 0.9951,
      "subfield": {
        "id": "https://openalex.org/subfields/2209",
        "display_name": "Industrial and Manufacturing Engineering"
      },
      "field": {
        "id": "https://openalex.org/fields/22",
        "display_name": "Engineering"
      },
      "domain": {
        "id": "https://openalex.org/domains/3",
        "display_name": "Physical Sciences"
      }
    },
    {
      "id": "https://openalex.org/T11007",
      "display_name": "Hybrid Renewable Energy Systems",
      "score": 0.966,
      "subfield": {
        "id": "https://openalex.org/subfields/2102",
        "display_name": "Energy Engineering and Power Technology"
      },
      "field": {
        "id": "https://openalex.org/fields/21",
        "display_name": "Energy"
      },
      "domain": {
        "id": "https://openalex.org/domains/3",
        "display_name": "Physical Sciences"
      }
    }
  ],
  "keywords": [
    {
      "id": "https://openalex.org/keywords/timeline",
      "display_name": "Time line",
      "score": 0.59625614
    },
    {
      "id": "https://openalex.org/keywords/position",
      "display_name": "Position (finance)",
      "score": 0.5177559
    }
  ],
  "concepts": [
    {
      "id": "https://openalex.org/C47737302",
      "wikidata": "https://www.wikidata.org/wiki/Q167336",
      "display_name": "Greenhouse gas",
      "level": 2,
      "score": 0.7858928
    },
    {
      "id": "https://openalex.org/C68189081",
      "wikidata": "https://www.wikidata.org/wiki/Q12748",
      "display_name": "Fossil fuel",
      "level": 2,
      "score": 0.7147851
    },
    {
      "id": "https://openalex.org/C4438859",
      "wikidata": "https://www.wikidata.org/wiki/Q186117",
      "display_name": "Timeline",
      "level": 2,
      "score": 0.59625614
    },
    {
      "id": "https://openalex.org/C175605778",
      "wikidata": "https://www.wikidata.org/wiki/Q3299701",
      "display_name": "Natural resource economics",
      "level": 1,
      "score": 0.58531946
    },
    {
      "id": "https://openalex.org/C132651083",
      "wikidata": "https://www.wikidata.org/wiki/Q7942",
      "display_name": "Climate change",
      "level": 2,
      "score": 0.55959654
    },
    {
      "id": "https://openalex.org/C198082294",
      "wikidata": "https://www.wikidata.org/wiki/Q3399648",
      "display_name": "Position (finance)",
      "level": 2,
      "score": 0.5177559
    },
    {
      "id": "https://openalex.org/C144133560",
      "wikidata": "https://www.wikidata.org/wiki/Q4830453",
      "display_name": "Business",
      "level": 0,
      "score": 0.44546452
    },
    {
      "id": "https://openalex.org/C509746633",
      "wikidata": "https://www.wikidata.org/wiki/Q898653",
      "display_name": "Climate change mitigation",
      "level": 3,
      "score": 0.42341495
    },
    {
      "id": "https://openalex.org/C162324750",
      "wikidata": "https://www.wikidata.org/wiki/Q8134",
      "display_name": "Economics",
      "level": 0,
      "score": 0.36268923
    },
    {
      "id": "https://openalex.org/C10138342",
      "wikidata": "https://www.wikidata.org/wiki/Q43015",
      "display_name": "Finance",
      "level": 1,
      "score": 0.1709364
    },
    {
      "id": "https://openalex.org/C127413603",
      "wikidata": "https://www.wikidata.org/wiki/Q11023",
      "display_name": "Engineering",
      "level": 0,
      "score": 0.13188612
    },
    {
      "id": "https://openalex.org/C18903297",
      "wikidata": "https://www.wikidata.org/wiki/Q7150",
      "display_name": "Ecology",
      "level": 1,
      "score": 0.09517324
    },
    {
      "id": "https://openalex.org/C205649164",
      "wikidata": "https://www.wikidata.org/wiki/Q1071",
      "display_name": "Geography",
      "level": 0,
      "score": 0.09004903
    },
    {
      "id": "https://openalex.org/C166957645",
      "wikidata": "https://www.wikidata.org/wiki/Q23498",
      "display_name": "Archaeology",
      "level": 1,
      "score": 0
    },
    {
      "id": "https://openalex.org/C86803240",
      "wikidata": "https://www.wikidata.org/wiki/Q420",
      "display_name": "Biology",
      "level": 0,
      "score": 0
    },
    {
      "id": "https://openalex.org/C548081761",
      "wikidata": "https://www.wikidata.org/wiki/Q180388",
      "display_name": "Waste management",
      "level": 1,
      "score": 0
    }
  ],
  "sustainable_development_goals": [
    {
      "display_name": "Affordable and clean energy",
      "id": "https://metadata.un.org/sdg/7",
      "score": 0.62
    }
  ],
  "abstract_inverted_index": null
}
```

If you want to get a text that is parsed and that you can classify:

```json
"10.1016/j.marpol.2022.105310":
{
  "OPENALEX": "https://openalex.org/W4306644972",
  "title": "Decarbonisation of the shipping sector – Time to ban fossil fuels?",
  "abstract": [],
  "topics": [
    "Maritime Transport Emissions and Efficiency",
    "Environmental Engineering",
    "Environmental Science",
    "Physical Sciences",
    "Maritime Ports and Logistics",
    "Industrial and Manufacturing Engineering",
    "Engineering",
    "Physical Sciences",
    "Hybrid Renewable Energy Systems",
    "Energy Engineering and Power Technology",
    "Energy",
    "Physical Sciences"
  ],
  "keywords": [
    "Time line",
    "Position (finance)"
  ],
  "concepts": [
    "Greenhouse gas",
    "Fossil fuel",
    "Timeline",
    "Natural resource economics",
    "Climate change",
    "Position (finance)",
    "Business",
    "Climate change mitigation",
    "Economics",
    "Finance",
    "Engineering",
    "Ecology",
    "Geography",
    "Archaeology",
    "Biology",
    "Waste management"
  ],
  "sustainable": [
    "Affordable and clean energy"
  ]
}
```

2. The *Classifier* module categorizes it to fit with the themes
given by [***R3MOB***](https://www.r3mob.fr) (*json* format):

```json
"10.1016/j.marpol.2022.105310":
{
  "challenges": "[\"Environnementaux\"]",
  "themes": "[\"Energie\"]",
  "scientificThemes": "[\"Marketing, Durabilit\\u00e9, Chaine d\\u2019approvisionnement, Logistiques, Inter & Multimodalit\\u00e9\", \"Mat\\u00e9riaux, A\\u00e9rodynamique, Transition \\u00e9cologique, \\u00c9nerg\\u00e9tique et Mobilit\\u00e9s durables\", \"Sciences \\u00e9conomique, \\u00c9valuation des politiques publiques, Mod\\u00e8les \\u00e9conomiques\"]",
  "mobilityTypes": "[\"Fluvial/Maritime\"]",
  "axes": "[\"Accompagner le d\\u00e9veloppement des syst\\u00e8mes de transports d\\u00e9carbon\\u00e9s et s\\u00fbrs\", \"Favoriser le report modal des marchandises vers le fer et le maritime et am\\u00e9liorer la logistique urbaine et rurale\"]",
  "usages": "[ \"Other\" ]"
}
```

You can find all the classification categories into the `/client/classifier`
directory.


To explain what is going on:

1. *Crossref* searches for your given query,

2. *Openalex* enhances what *Crossref* can give with its own metadata,

3. The *llm* called **sentence-transformers** from *HuggingFace* labellizes
a generated dataset that is close to your searching query
(this part has to be done manually),

4. The current classification model, trained on that dataset, classifies the
searched paper amongst the given themes (here, the categories given by
**R3MOB**).

## Production mode

Recommended mode.

### Prerequisites

You will need:

- *docker*

- *docker compose*

```bash
 classification  >>  docker --version
Docker version 28.3.3, build 980b856816
 classification  >>  docker compose version
Docker Compose version 2.39.2
```

### Launching

Each client contains a *Dockerfile*,
that will permit you to use them individually.

Anyway you will find at the root folder a `docker-compose.yml` file to rule them all.

Just do this:

```bash
cd classification/

# Edit the client environment variables, do nothing to get the default
# environment variables.
cp client/retriever/.env.example client/retriever/.env
vim client/retriever/.env

cp client/classifier/.env.example client/classifier/.env
vim client/classifier/.env

# Launch.
docker compose -f docker-compose.yml up -d --build

# If you want to remove the containers.
docker compose -f docker-compose.yml down

# If you want to remove the docker images ( not done by `docker compose down` )
# `--build` recreates the image anyway.
docker images
docker rmi <image-name>

# If you want to just stop the containers.
docker ps
docker stop <container-name>
```

### How to install docker

- **Ubuntu** and **Debian**
`curl -fsSL https://get.docker.com | sh`

- **Arch Linux** and **Manjaro**
`sudo pacman -Sy --noconfirm docker && sudo systemctl enable --now docker`

- **Fedora**
`sudo dnf install -y docker docker-compose && sudo systemctl enable --now docker`

- **CentOS** and **RHEL**
`sudo yum install -y docker && sudo systemctl enable --now docker`

-  **OpenSUSE**
`sudo zypper install -y docker && sudo systemctl enable --now docker`

- **WSL2** on **Windows**
Use *Docker Desktop* with [this link](https://www.docker.com/products/docker-desktop/).
Then use
`sudo service docker start`

## Development mode

You can go into the specific client subfolder to launch it manually from there.

This could be useful when you want to labellize data using the *LLM* from
*Huggingface*, because this service is not supported by the *production mode*
due to space disk issues.

### Retriever

This is a **Flask + gevent** server that uses **socketio**.
To interact with it, there is an example of a *Python* client in
the `client/retriever/README.md` file. You can also use the *Javascript*
client from the `frontend/` directory.

The events are:

```
- connect() ( automatically called )

- disconnect() ( automatically called )

- data(text) ( don't use it )

- search_query(payload) -> search_results() | search_error()

- search_query_cursor(id_cursor) -> search_results() | search_error()

- convert_from_openalex(json_openalex) -> search_results() | search_error()

- convert_from_ris(json_crossref_style) -> search_results() | search_error()

- convert_from_crossref_style_to_ris(ris_file_str) -> conversion_ris_results()
```

where the `payload` is:

```python
payload = {
    'query': 'DOI, ORCID, text, title, author, etc..',
    'limit': 10, # the max number of results.
    'sort': "relevance", # It could be "relevance", "score",
                    # "deposited", "indexed", "published", "published-print",
                    # "published-online", "issued", "is-referenced-by-count",
                    # "references-count".
    'cursor_max': 100, # Max number of publication on all pages
                       # at the same time. if negative (-1), it is faster.
}
```

and `json_openalex` is a string, and `search_results()` sends:

```python
payload_results = {
    'results': results_str # a `json` object (see `client/retriever/README.md`).
}
```

and `search_error()` sends:

```python
payload_results = {
    'results': None
}

payload_error = {
    'error':  { 'message': error_str }
}
```

### Classifier

This is a **Flask + gevent** server that uses **socketio**.
To interact with it, there is an example of a *Python* client in
the `client/classifier/README.md` file. You can also use the *Javascript*
client from the `frontend/` directory.

The events are:

```
- connect() ( automatically called )

- disconnect() ( automatically called )

- data(text) ( don't use it )

- text_classification(text) -> classification_results() | classification_error()

- json_classification(json) -> classification_results() | classification_error()

- dataset_classification(partial_json) -> classification_results() | classification_error()
```

where the `text` is a text, **str**, and `search_results()` sends:

```python
payload_results = {
    'results': results_str # a `json` object. 
}
```

and `search_error()` sends:

```python
payload_results = {
    'results': None
}

payload_error = {
    'error':  { 'message': error_str }
}
```

Example of supported RIS file:

```ris
TY  - JOUR
TI  - Energy efficiency and consumption — the rebound effect — a survey
PY  - 2000
PB  - Elsevier BV
SN  - 0301-4215
T2  - Energy Policy
DO  - 10.1016/s0301-4215(00)00021-5
UR  - https://doi.org/10.1016/s0301-4215(00)00021-5
DA  - 2000-06-01
AU  - Greening, Lorna
C1  - International Resources Group, 1211 Connecticut Ave., NW Washington, DC 20036, USA
AU  - Greene, David
C1  - Oak Ridge National Laboratory Oak Ridge TN USA
AU  - Difiglio, Carmen
C1  - International Energy Agency, 9 rue de la Fédération 75739 Paris Cedex 15, France
LA  - en
KW  - Rebound Effect
KW  - Consumption
KW  - Energy accounting
VL  - 28
IS  - 6-7
SP  - 389
EP  - 401
ER  -
TY  - JOUR
TI  - Six Transformations to achieve the Sustainable Development Goals
PY  - 2019
PB  - Nature Portfolio
SN  - 2398-9629
T2  - Nature Sustainability
DO  - 10.1038/s41893-019-0352-9
UR  - https://doi.org/10.1038/s41893-019-0352-9
DA  - 2019-08-26
AU  - Sachs, Jeffrey
C1  - Columbia University, New York, NY, USA
AU  - Schmidt‐Traub, Guido
C1  - Sustainable Development Solutions Network, Paris, France
AU  - Mazzucato, Mariana
C1  - University College London, London, UK
AU  - Messner, Dirk
C1  - United Nations University, Bonn, Germany
AU  - Nakićenović, Nebojša
C1  - International Institute for Applied Systems Analysis, Laxenburg, Austria
AU  - Rockström, Johan
C1  - Potsdam Institute for Climate Impact Research, Potsdam, Germany
LA  - en
KW  - Civil Society
VL  - 2
IS  - 9
SP  - 805
EP  - 814
ER  -
```

### Dataset

This is just a client of both previous *Flask* servers.
It is a sandbox service used to generate a labelled dataset.
That is helpful to train some models for the *Classifier* module.

### Frontend - Development only

This is a *Javascript* client used to interact with the *Classifier* and
*Retriever* servers.

### EOF

