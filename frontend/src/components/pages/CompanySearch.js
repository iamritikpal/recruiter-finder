import React from "react";
import SearchForm from "../forms/SearchForm";
import SearchResults from "../common/SearchResults";
import { API_ENDPOINTS, buildURL } from "../../config/api";
import "./CompanySearch.css";

const CompanySearch = ({
  company,
  setCompany,
  results,
  setResults,
  loading,
  setLoading,
  error,
  setError,
  searchPerformed,
  setSearchPerformed,
  lastSearchedCompany,
  setLastSearchedCompany,
  lastSearchResponse,
  setLastSearchResponse,
  searchCount,
  setSearchCount,
}) => {
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!company.trim()) {
      setError("Please enter a company name");
      return;
    }

    setLoading(true);
    setError("");
    setLastSearchedCompany(company.trim());
    setSearchCount((count) => count + 1);

    try {
      const searchURL = buildURL(API_ENDPOINTS.searchRecruiters, {
        company: company.trim(),
      });
      const response = await fetch(searchURL);
      const data = await response.json();

      if (response.ok) {
        setResults(data.profiles || []);
        setLastSearchResponse(data);
        setSearchPerformed(true);
      } else {
        throw new Error(data.message || "Search request failed");
      }
    } catch (err) {
      console.error("Search error:", err);
      setError(
        err.message ||
          "Failed to search for recruiters. Please check your connection and try again."
      );
      setResults([]);
      setLastSearchResponse(null);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setCompany(e.target.value);
    if (error) setError("");
  };

  const handleClear = () => {
    setCompany("");
    setResults([]);
    setError("");
    setSearchPerformed(false);
    setLastSearchResponse(null);
  };

  const getSearchButtonText = () => {
    if (loading) return "Searching...";
    if (searchCount === 0) return "🔍 Search Recruiters";
    return `🔍 Search Again (${searchCount})`;
  };

  return (
    <div className="main-content">
      <div className="content-header">
        <h1>🏢 Find Recruiters by Company</h1>
        <p>
          Search for technical recruiters, talent acquisition specialists, and
          hiring managers at any company
        </p>
      </div>

      <SearchForm
        company={company}
        onInputChange={handleInputChange}
        onSubmit={handleSubmit}
        onClear={handleClear}
        loading={loading}
        error={error}
        searchPerformed={searchPerformed}
        getSearchButtonText={getSearchButtonText}
      />

      <SearchResults
        loading={loading}
        lastSearchedCompany={lastSearchedCompany}
        results={results}
        lastSearchResponse={lastSearchResponse}
        error={error}
        searchPerformed={searchPerformed}
      />
    </div>
  );
};

export default CompanySearch;
