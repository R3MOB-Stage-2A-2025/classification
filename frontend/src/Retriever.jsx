import "./Retriever.css";

import { useState, useEffect } from "react";
import { SearchBar } from "./components/SearchBar";
import { SearchResultsList } from "./components/SearchResultsList";

import { socket_retriever } from "./socket";

function Retriever() {
    const [results, setResults] = useState([]);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        socket_retriever.on("search_error", (data) => {
            setError(data.error || "Unknown Error detected.");
            setLoading(false);
        });

        socket_retriever.on("search_results", (data) => {
            setLoading(false);
            setError(null);
            setResults(JSON.parse(data.results));
        });

        return () => {
            socket_retriever.off("search_error");
            socket_retriever.off("search_results");
        };
    }, []);

    return (
        <div className="Retriever">
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

export default Retriever;

