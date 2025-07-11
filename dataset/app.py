import socketio
import json

import config

sio = socketio.Client()

@sio.event
def connect():
    print("Connected.")

@sio.event
def disconnect():
    print("Disconnected.")

@sio.on("search_results")
def on_search_results(data):
    print("Search results received:")
    print(json.dumps(data))

@sio.on("search_error")
def on_search_error(data):
    print("Error from server:")
    print(json.dumps(data))

def main():
    sio.connect(config.SERVER_URL)

    query_data = {
        "query": "toto",
        "offset": 0,
        "limit": 1
    }

    sio.emit("search_query", json.dumps(query_data))
    sio.wait()
    sio.disconnect()

if __name__ == "__main__":
    main()

