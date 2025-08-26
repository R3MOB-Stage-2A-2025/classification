import "./SearchCursorList.css";

import { socket_retriever } from "../socket";

export const SearchCursorList = ({ setCursor, cursor, setLoading, loading }) => {
    const totalPages = 5;

    const setCurrentPage = (cursor) => {
        if (!loading) {
            setLoading(true);
            setCursor(cursor);

            socket_retriever.emit("search_query_cursor", JSON.stringify({
                id_cursor: cursor - 1
            }));
        }

    };

    return (
        <div className="SearchCursorList">
          {[...Array(totalPages)].map((_, index) => {
            const page = index + 1;
            return (
              <button
                key={page}
                onClick={() => setCurrentPage(page)}
                className={`page-btn ${page === cursor ? "active" : ""}`}
              >
                {page}
              </button>
            );
          })}
        </div>
      );
};

