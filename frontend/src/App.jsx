import './App.css';

import { useState, useEffect } from 'react';

import { socket } from './socket';

function App() {
    const [input, setInput] = useState('');
    const [results, setResults] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        socket.on("classification_error", (data) => {
            setError(data.error || "Unknown Error detected.");
            setLoading(false);
            setResults(false);
        });

        socket.on("classification_results", (data) => {
            setLoading(false);
            setError(null);
            setResults(JSON.parse(data.themes));
        });

        socket.on("json_classification_results", (data) => {
            setLoading(false);
            setError(null);
            setResults(JSON.parse(data.themes));
        });

        socket.on("json_classification_error", (data) => {
            setLoading(false);
            setResults(false);
            setError(data.error || "JSON could not be imported.");
        });

        return () => {
            socket.off("classification_results");
            socket.off("classification_error");
            socket.off("json_classification_results");
            socket.off("json_classification_error");
        };
    }, []);

    const classifyText = () => {
        if (!loading) {
            setResults(false);
            setLoading(true);
            setError(false);
            socket.emit("classification", input);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter")
            classifyText();
    };

    const handleJsonUpload = (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();

        reader.onload = (e) => {
            try {
                const jsonContent = JSON.parse(e.target.result);
                setLoading(true);
                setError(null);
                setResults(false);
                socket.emit("json_classification", JSON.stringify(jsonContent));
            } catch (err) {
                setError("JSON is invalid.");
            }
        };

        reader.readAsText(file);
    };

    return (
        <div>
            <h1>Classification des publications</h1>
            {loading && <span className="loading">Searching...</span>}
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
                    <button type="button" onClick={classifyText}>Valider</button>
                </form>
            </div>
            <div>
                <label htmlFor="jsonUpload">
                    <strong>Importer une publication JSON :</strong>
                </label>
                <input
                    type="file"
                    id="jsonUpload"
                    accept=".json"
                    onChange={handleJsonUpload}
                    disabled={loading}
                    style={{ marginLeft: '1rem' }}
                />
            </div>
            <div id="result">
                {error && <p>{error}</p>}
                {results && results.length > 0 && (
                    <>
                        <h2>Thèmes scentifiques associés :</h2>
                        <ul>
                            {results.map((theme, index) => (
                                <li key={index}>{theme}</li>
                            ))}
                        </ul>
                    </>
                )}
            </div>
        </div>
    );
}

export default App;

