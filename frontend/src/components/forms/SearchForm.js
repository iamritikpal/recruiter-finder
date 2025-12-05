import React from "react";
import "./SearchForm.css";

const SearchForm = ({
  company,
  onInputChange,
  onSubmit,
  onClear,
  loading,
  error,
  searchPerformed,
  getSearchButtonText,
}) => {
  return (
    <form onSubmit={onSubmit} className="search-form">
      <div className="input-group">
        <input
          type="text"
          value={company}
          onChange={onInputChange}
          placeholder="Enter company name or location (e.g., Google, Microsoft India, Apple UK)"
          className={`search-input ${error ? "error" : ""}`}
          disabled={loading}
          autoComplete="organization"
        />
        <button
          type="submit"
          className="search-button"
          disabled={loading || !company.trim()}
          title={loading ? "Searching..." : "Search for recruiters"}
        >
          {loading && <div className="button-spinner"></div>}
          {getSearchButtonText()}
        </button>
        {(company || searchPerformed) && (
          <button
            type="button"
            onClick={onClear}
            className="clear-button"
            disabled={loading}
            title="Clear search and results"
          >
            Clear
          </button>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}
    </form>
  );
};

export default SearchForm;
