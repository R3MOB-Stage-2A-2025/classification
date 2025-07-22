# Retriever

An *API* cluster that you can use as a *python* client.

List of supported *API*s:

- [***Pyalex***](https://pypi.org/project/pyalex/):
OpenAlex client.

- [***Habanero***](https://github.com/sckott/habanero/):
non-official Crossref client.

- [***Semanticscholarapi***](https://github.com/danielnsilva/semanticscholar):
non-official Semantic Scholar client.

- [***Pybliometrics***](https://github.com/pybliometrics-dev/pybliometrics):
Scopus and ScienceDirect client.

- [***Pyorcid***](https://pypi.org/project/PyOrcid/):
non-official ORCID client.


You can get more information on each client in their own *README.md file,
located in their `/api/<client>/` directory.

### Want to change the API key of a specific client?

the file `.env.example` contains an example of what you can modify.

Certain *API*s as *SemanticScholar*, or *Pybliometrics* are not widely
used in this project. To reactivate them, you can directly modify the
source code in the `./Retriever.py` file.


Besides, this project does not require any *API* key at all.

### How many requests can I send before reaching the *API* limits?

This cluster is free to use, its limit is what the *API* can do, without
any *API* key (except if you provide one).

Here are some figures:

- [***Openalex***](https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication):
max 100,000 calls every day, max 10requests per second.

- [***Crossref***](https://crossref.readthedocs.io/en/latest/):
50 requests per second.

- [***Semanticscholar***](https://semanticscholar.readthedocs.io/en/stable/usage.html):
100 requests every 5 minutes without an *API* key.

- [***Pybliometrics***](https://github.com/pybliometrics-dev/pybliometrics/issues/300):
the response can not exceed 5000 lines for non-subscriber people.
The doc says that each *API* key allows only 5000 retrieval requests.
[***right here***](https://pybliometrics.readthedocs.io/en/stable/access.html)

- [***PyOrcid***](https://info.orcid.org/documentation/integration-and-api-faq/):
probably none.

*Openalex* and *Crossref* has a **polite pool*,
[***right here***](https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication).
Be sure to always precise your *mail* in the `.env` file.

## How to use

- backend: **Python** (*Pyalex*) using *flask_socketio*, *gevent* and *flask*.

The goal of this repository is to code a wrapper on the *OpenAlex Api* client
called *pyalex*.

## Starting the Flask server in production mode

1. Edit the environment variables you wish:

```bash
cd backend/
cp .env.example .env
vim .env
```

Then you can use the specified *Dockerfile* with the *docker-compose.yml*
file in the root directory.

## Starting the Flask server in development mode

1. ``cd openalex/``

2. Initialize the backend:

You should first choose you environment variables in the `backend/` folder.
do ``cp .env.example .env`` and edit the `.env` file.

```bash
# Open another terminal and do this:
cd openalex/backend/
python -m venv .venv
source .venv/bin/activate
cd backend/
pip install -r requirements.txt
python Server.py
```

### EOF

