import "./SearchBar.css";

import { useState } from "react";
import { FaSearch } from "react-icons/fa";

import { socket_retriever } from "../socket";

export const SearchBar = ({ setResults, setError, setLoading, loading }) => {
    const [input, setInput] = useState("");
    const [sort, setSort] = useState("");

    const sortingTypes = [
        "relevance", "score", "deposited", "indexed",
        "published", "published-print", "published-online",
        "issued", "is-referenced-by-count", "references-count"
    ];

    const handleKeyDown = (e) => {
        if (e.key === "Enter" && !loading) {
            setLoading(true);
            setError(false);
            socket_retriever.emit("search_query", JSON.stringify({
                query: input,
                sort: sort
            }));
        }
    };

    return (
        <div className="input-wrapper">
            <FaSearch id="search-icon" />
            <input
                placeholder="DOI, Title, Abstract, Author, etc..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={loading}
            />

            {loading && <span className="loading">Searching...</span>}

            <select
                value={sort}
                onChange={(e) => setSort(e.target.value)}
                style={{ padding: "8px", fontSize: "16px" }}
            >
                <option value="None">None</option>
                {sortingTypes.map((label) => (
                    <option key={label} value={label}>
                        {label}
                    </option>
                ))}
            </select>

        </div>
    );
};

