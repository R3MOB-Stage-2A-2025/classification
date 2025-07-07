# Client - ORCID

[***Pyorcid***](https://pypi.org/project/PyOrcid/) wrapper.

- backend: **Python** (*Pyorcid*) using *flask_socketio*, *gevent* and *flask*.

The goal of this repository is to code a wrapper on the *ORCID Api* client
called *pyorcid*.

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

1. ``cd crossref/``

2. Initialize the backend:

You should first choose you environment variables in the `backend/` folder.
do ``cp .env.example .env`` and edit the `.env` file.

```bash
# Open another terminal and do this:
cd client_crossref/backend/
python -m venv .venv
source .venv/bin/activate
cd backend/
pip install -r requirements.txt
python Server.py
```

### EOF

