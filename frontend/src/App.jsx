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

        return () => {
            socket.off("classification_results");
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

            <div id="result">
                {error && <p>{error}</p>}
                {results && results.length > 0 ? (
                    <>
                        <h2>Thèmes scentifiques associés :</h2>
                        <ul>
                            {results.map((theme, index) => (
                                <li key={index}>{theme}</li>
                            ))}
                        </ul>
                    </>
                ) : results && results.length === 0 ? (
                    <p>Aucun thème associé trouvé.</p>
                ) : null}
            </div>
        </div>
    );
}

export default App;

