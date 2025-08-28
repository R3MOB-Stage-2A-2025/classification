import "./Retriever.css";

import { useState, useEffect } from "react";
import { SearchBar } from "./components/SearchBar";
import { SearchResultsList } from "./components/SearchResultsList";
import { SearchCursorList } from "./components/SearchCursorList";

import { socket_retriever } from "./socket";

function Retriever() {
    const [results, setResults] = useState([]);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const [cursor, setCursor] = useState(0);

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
                socket_retriever.emit("convert_from_openalex",
                    JSON.stringify(jsonContent));
            } catch (err) {
                setError("JSON is invalid.");
            }
        };

        reader.readAsText(file);
    };

    // ----------------------------------------------------------------------

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

                <SearchCursorList
                    setCursor={setCursor}
                    cursor={cursor}
                    setLoading={setLoading}
                    loading={loading}
                />
            </div>

            <div className="Upload">
                <label htmlFor="jsonUpload">
                    <strong>Importer an Openalex JSON :</strong>
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

        </div>
    );
}

export default Retriever;

