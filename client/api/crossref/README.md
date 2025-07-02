# Client - Crossref API

[***Habanero***](https://github.com/sckott/habanero/) wrapper.

- backend: **Python** (*habanero*) using *flask_socketio*, *gevent* and *flask*.

- frontend (tests only): **Javascript** using *socket.io* and *vite*, *react*.

The goal of this repository is to code a wrapper on the *Crossref API* client
called *Habanero*.

## Environment variables

TODO

## Production mode

1. ``cd client_crossref/``

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

3. Tests only, use the frontend:

```bash
# Open another terminal and do this:
cd frontend/
npm install
npm run dev
# TODO
```

## Security

1. **HTTPS**:

TODO (certificates)

2. **Token authentication JWT**:

TODO

3. **CORS**:

TODO

## TODO

- Should use `jsonify()` from *Flask* to return *json* file.

- Should verify the request status such as ``if (response.ok == 1)``...

- Add *CORS*.

- (Open question): How to prevent from *denial of services*?

- Add some *try catch* in the client to find errors.

### EOF

