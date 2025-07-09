import "./SearchBar.css";

import { useState } from "react";
import { FaSearch } from "react-icons/fa";

import { socket } from "../socket";

export const SearchBar = ({ setResults, setError, setLoading, loading }) => {
    const [input, setInput] = useState("");

    const handleKeyDown = (e) => {
        if (e.key === "Enter" && !loading) {
            setLoading(true);
            setError(false);
            socket.emit("search_query", JSON.stringify({
                query: input
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
        </div>
    );
};

