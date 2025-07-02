import "./App.css";

import { useState, useEffect } from "react";
import { SearchBar } from "./components/SearchBar";
import { SearchResultsList } from "./components/SearchResultsList";

import { socket } from "./socket";

function App() {
    const [results, setResults] = useState([]);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        socket.on("search_error", (data) => {
            setError(data.error || "Unknown Error detected.");
            setLoading(false);
        });

        socket.on("search_results", (data) => {
            setLoading(false);
            setError(null);
            setResults(JSON.parse(data.results));
        });

        return () => {
            socket.off("search_error");
            socket.off("search_results");
        };
    }, []);

    return (
        <div className="App">
            { error &&
                <div className="error-wrapper">
                    { error.message }
                </div>
            }
            <div className="search-bar-container">
                <SearchBar
                    setResults={setResults}
                    setError={setError}
                    setLoading={setLoading}
                    loading={loading}
                />
                <SearchResultsList
                    setResults={setResults}
                    results={results}
                    setLoading={setLoading}
                    loading={loading}
                />
            </div>
        </div>
    );
}

export default App;

