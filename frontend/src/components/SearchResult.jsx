import "./SearchResult.css";

import { socket } from "../socket";

export const SearchResult = ({ item, loading, setLoading }) => {
    const title = item?.['title'] || "Untitled";
    const doi = item?.['DOI'] || "No DOI";
    const url = item?.['URL'] || `https://doi.org/${doi}`;

    const authors = item?.['author']
        ? item?.['author'].map((a) =>
        [a.given, a.family].filter(Boolean).join(" ")
    ).join(", ")
        : "No authors";

    const abstract = item['abstract']
        ? item['abstract'].replace(/<\/?jats:[^>]+>/g, '')
        : "No abstract available";

    const handleMetadataClick = () => {
        const dataStr = JSON.stringify(item, null, 2);
        const blob = new Blob([dataStr], { type: "application/json" });
        const url = URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = `${item.title[0]?.replaceAll(" ", "_") || "metadata"}.json`;
        a.click();

        URL.revokeObjectURL(url);
    };

    const handleFilterClick = () => {
        const title = item?.['title'][0] || item?.['container-title'][0];

        if (!loading && title !== "") {
            setLoading(true);
            socket.emit("search_query", JSON.stringify({
                query: title,
                offset: 0
            }));
        }
    };

    return (
        <div className="search-result">
            <h3>{title}</h3>
            <p><strong>DOI:</strong> <a href={url} target="_blank" rel="noopener noreferrer">{doi}</a></p>
            <p><strong>Authors:</strong> {authors}</p>
            <p><strong>Abstract:</strong> {abstract}</p>

            <button className="result-button" onClick={handleFilterClick}>Filter by Title</button>
            <button className="result-button" onClick={handleMetadataClick}>Metadata as JSON</button>
        </div>
    );
};

