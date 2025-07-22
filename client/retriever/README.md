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

You can launch the application manually using *python* (recommended for dev),
or automatically using *docker* for non-dev users.

### Starting the Flask server in production mode (docker)

1. Edit the environment variables you wish:

```bash
cp .env.example .env
vim .env # edit the variables
```

2. Install *docker and *docker compose* (last section of main *README.md*).

3. Use the `docker compose` of the main *README.md* file.

### Starting the Flask server in development mode (python)

1. Initialize the backend:

```bash
cp .env.example .env
vim .env # edit the variables
```

2. Launch the Flask app

```bash
# Open another terminal and do this:
cd /client/retriever
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Overview

- backend: *flask_socketio*, *gevent* and *flask*.

- frontend: for development only, see the `/frontend` directory.

### Example of a client API

You can use this *Flask* server like this with **Python3.13**:

```python
import socketio
import json

RETRIEVER_URL: str = "http://localhost:5001"

sio = socketio.Client()

def connect():
    print("Connected.")

@sio.event
def disconnect():
    print("Disconnected.")

@sio.on("search_results")
def on_search_results(data):
    results: dict = json.loads(data.get('results', {}))

    try:
        # results contains various publications, it just displays one here.
        message: dict = results.get('message', {})
        items: dict = message.get('items', [{}])

        publication: dict = items[0]
        print(publication.get('title', ""))

        publication_str: str = json.dumps(publication)
        # Do something with it.
        print(f'\n\n{publication}\n\n')

    except Exception as e:
        print(f'{e}')
        exit(0)

@sio.on("search_error")
def on_search_error(data):
    print("Error from server:")
    print(data)

def main():
    sio.connect(RETRIEVER_URL)

    try:
        query_data = {
            'query' : 'Mohamed Mosbah',
            "offset": 0,
            "limit": 1
        }
        # 'query' can also be a DOI, an Openalex ID, an ORCID.

        sio.emit("search_query", json.dumps(query_data))

    except Exception as e:
        print(f'{e}')
        exit(0)

    sio.sleep(20) # Wait 20sec for the response
    disconnect()

if __name__ == "__main__":
    main()
```

Here is the *requirements.txt* file:

```python
python-engineio==4.12.2
python-socketio==5.13.0
websocket-client==1.8.0
requests==2.32.4
```

For a *javascript* client, you can check the `/frontend` directory.

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

### EOF

