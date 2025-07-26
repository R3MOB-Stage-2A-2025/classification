# Frontend - Development tool

A simple web interface to interact with the *Retriever* and the *Classifier*
servers, as a javascript client.

This is not designed for production.

## How to use

It is recommended to use `docker`.

### Docker

Just use the `docker-compose.yml` from the root directory.

If you need to change the port, it is hardcoded into the file located
at `frontend/vite.config.js`.

If you need to change the *Classifier* or *Retriever* ports, it is hardcoded
into the file located at `frontend/src/socket.js`.

### Manually

Just do this:

```bash
cd frontend/
npm install
npm run dev
```

## Overview

**vite + reactjs** app.

There are 2 sockets from `socket.io-client` located in the
`frontend/src/socket.js` file, respectively for the *Classifier*
and the *Retriever*.

NB: The labels are hardcoded into the source code, if you changed the labels
from the *Classifier* module, you will also have to edit the file
called `frontend/src/Classifier.jsx`.

### Javascript client for the Retriever module

If you want to get a simple client for the *Retriever* module, you can
use the one in `frontend/src/Retriever.jsx` which depends on some components
from the `frontend/src/components/` directory.

### Javascript client for the Classifier module

Here is a simple react client to get the `challenges`:

```javascript
// Simplified version of `frontend/src/Classifier.jsx`.

import { useState, useEffect } from 'react';

const socket_classifier = io.connect('http://localhost:5011');

function ClassifierClient() {
    const [input, setInput] = useState('');
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    // ----------------------------------------------------------------------
    // Retrieve the Challenges.
    // ----------------------------------------------------------------------

    // Challenges.
    const [challenges, setChallenges] = useState(null);

    const setVariablesToFalse = () => {
        setChallenges(false);
    };

    const setVariablesToData = (data) => {
        setChallenges(JSON.parse(data.challenges));
    };

    // ----------------------------------------------------------------------

    useEffect(() => {
        socket_classifier.on("classification_error", (data) => {
            setError(data.error || "Unknown Error detected.");
            setLoading(false);
        });

        socket_classifier.on("classification_results", (data) => {
            setLoading(false);
            setVariablesToData(data);
        });

        return () => {
            socket_classifier.off("classification_error");
            socket_classifier.off("classification_results");
        };
    }, []);

    const classify = () => {
        if (!loading) {
            setVariablesToFalse();
            setLoading(true);
            setError(null);
            socket_classifier.emit("text_classification", input);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter")
            classify();
    };

    // ----------------------------------------------------------------------
    // JSON Upload.
    // ----------------------------------------------------------------------

    const handleJsonUpload = (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();

        reader.onload = (e) => {
            try {
                const jsonContent = JSON.parse(e.target.result);
                setLoading(true);
                setError(null);
                setVariablesToFalse();
                socket_classifier.emit("json_classification",
                    JSON.stringify(jsonContent));
            } catch (err) {
                setError("JSON is invalid.");
            }
        };

        reader.readAsText(file);
    };

    // ----------------------------------------------------------------------

    return (
        <div className="Classifier">

            <h1>Classification des publications</h1>
            {loading && <span className="loading">Searching...</span>}

            { error &&
                <div className="error-wrapper-classifier">
                    { error.message }
                </div>
            }

            <div id="data">
                <form id="classificationForm" onSubmit={(e) => e.preventDefault()}>
                    <textarea
                        id="textInput"
                        rows="10"
                        cols="50"
                        placeholder="Entrez l'abstract ici (en anglais)..."
                        value={input}
                        onKeyDown={handleKeyDown}
                        onChange={(e) => setInput(e.target.value)}
                        disabled={loading}
                    />
                    <button type="button" onClick={classify}>Valider</button>
                </form>
            </div>

            <div className="Upload">
                <label htmlFor="jsonUpload">
                    <strong>Importer une publication JSON :</strong>
                </label>
                <input
                    type="file"
                    id="jsonUpload"
                    accept=".json"
                    onChange={handleJsonUpload}
                    disabled={loading}
                    style={{ marginTop: '0.5rem', fontSize: '1rem' }}
                />
            </div>

            <div id="result">
                {challenges && challenges.length > 0 && (
                    <>
                        <h2>Enjeux associés :</h2>
                        <ul>
                            {challenges.map((challenge, index) => (
                                <li key={index}>{challenge}</li>
                            ))}
                        </ul>
                    </>
                )}

            </div>
        </div>
    );
}
```

### EOF

