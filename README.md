# Classification repository

The repository contains multiple services such as client *API*s,
and *parsing* modules.

## Manual installation/ Development mode

You can go to the specific subfolder and follow the given *README.md* file.

To explain what is going on, each *client* is a **Flask + gevent** server
that is launched using **socketio**.

A *client* can be the client from a search engine *API*,
or from the *classifier* module.

One day the client *API*s (not the *classifier*) will merge into one single
*Flask + gevent + socketio* server.

## Production mode

### Prerequisites

You will need:

- *docker*

- *docker compose*

### Launching

Each subfolder contains a *Dockerfile* file.

Anyway you will find at the root folder a `docker-compose.yml` file to rule them all.

Just do this:

```bash
cd classification/
# Edit the environment variables in the `.env` file before this.
docker compose -f docker-compose.yml up -d

# If you want to remove the containers.
docker compose -f docker-compose.yml down

# If you want to just stop the containers.
docker ps
docker stop <container-name>

### EOF

