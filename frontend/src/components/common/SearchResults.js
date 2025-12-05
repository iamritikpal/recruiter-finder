import React from "react";
import LoadingSpinner from "./LoadingSpinner";
import RecruiterTable from "./RecruiterTable";
import "./SearchResults.css";

const SearchResults = ({
  loading,
  lastSearchedCompany,
  results,
  lastSearchResponse,
  error,
  searchPerformed,
}) => {
  if (loading) {
    return (
      <LoadingSpinner
        message={`Searching for recruiters at ${lastSearchedCompany}...`}
      />
    );
  }

  if (error && searchPerformed) {
    return (
      <div className="error-message">
        <h3>Search Error</h3>
        <p>{error}</p>
      </div>
    );
  }

  if (!searchPerformed || !lastSearchResponse) {
    return null;
  }

  return (
    <div className="results">
      <div className="results-header">
        <h2>
          {results.length === 0
            ? "No Results Found"
            : `Found ${results.length} Recruiter${
                results.length !== 1 ? "s" : ""
              }`}
          {lastSearchedCompany && ` at ${lastSearchedCompany}`}
        </h2>

        {lastSearchResponse.search_enhanced && (
          <div className="search-enhancement-info">
            <p>{lastSearchResponse.search_enhanced}</p>
          </div>
        )}
      </div>

      {results.length === 0 ? (
        <div className="no-results">
          <div className="no-results-content">
            <h3>🔍 No recruiters found</h3>
            <p>{lastSearchResponse.message}</p>
            <div className="search-tips">
              <h4>💡 Search Tips:</h4>
              <ul>
                <li>
                  Try searching with location: "Google India", "Microsoft UK"
                </li>
                <li>
                  Use variations of company names: "Meta" instead of "Facebook"
                </li>
                <li>Check spelling and try partial company names</li>
                <li>
                  Some companies may have limited public recruiter profiles
                </li>
              </ul>
            </div>
          </div>
        </div>
      ) : (
        <RecruiterTable
          profiles={results}
          searchedCompany={lastSearchedCompany}
        />
      )}
    </div>
  );
};

export default SearchResults;
