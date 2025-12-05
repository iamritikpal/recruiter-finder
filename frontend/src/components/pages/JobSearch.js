import React, { useState, useEffect } from "react";
import { API_ENDPOINTS, buildURL, API_BASE_URL } from "../../config/api";
import JobTable from "../common/JobTable";
import "./JobSearch.css";

const JobSearch = ({ initialCompany = "", initialLocation = "" }) => {
  const [company, setCompany] = useState(initialCompany);
  const [location, setLocation] = useState(initialLocation);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [searchPerformed, setSearchPerformed] = useState(false);
  const [popularCompanies, setPopularCompanies] = useState([]);
  const [jobStats, setJobStats] = useState(null);
  const [popularJobs, setPopularJobs] = useState([]);
  const [loadingPopularJobs, setLoadingPopularJobs] = useState(false);



  // Fetch initial data
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        // Fetch job stats first
        const statsResponse = await fetch(API_ENDPOINTS.getJobStats);
        if (statsResponse.ok) {
          const statsData = await statsResponse.json();
          setJobStats(statsData);
        }

        // Fetch popular companies
        const companiesResponse = await fetch(API_ENDPOINTS.getPopularCompanies);
        if (companiesResponse.ok) {
          const companiesData = await companiesResponse.json();
          setPopularCompanies(companiesData.companies || []);
          
          // Fetch jobs from popular companies
          await fetchPopularJobs(companiesData.companies || []);
        }
              } catch (err) {
        console.error("Error fetching initial data:", err);
      }
    };

    fetchInitialData();
  }, []);

  // Fetch popular jobs from multiple companies
  const fetchPopularJobs = async (companies) => {
    setLoadingPopularJobs(true);
    const allJobs = [];
    
    try {
      // Get jobs from first 6 popular companies
      const topCompanies = companies.slice(0, 6);
      
      for (const company of topCompanies) {
        try {
          const params = { company: company.name, max_results: 3 };
          const url = buildURL(API_ENDPOINTS.searchJobs, params);
          const response = await fetch(url);
          
          if (response.ok) {
            const data = await response.json();
            const jobs = (data.results?.jobs || []).map(job => ({
              ...job,
              sourceCompany: company.name,
              sourceCategory: company.category
            }));
            allJobs.push(...jobs);
          }
        } catch (err) {
          console.error(`Error fetching jobs for ${company.name}:`, err);
        }
      }
      
      // Shuffle and limit to 12 jobs
      const shuffledJobs = allJobs.sort(() => 0.5 - Math.random()).slice(0, 12);
      setPopularJobs(shuffledJobs);
      
    } catch (err) {
      console.error("Error fetching popular jobs:", err);
    } finally {
      setLoadingPopularJobs(false);
    }
  };

  // Auto-trigger search if initial company is provided
  useEffect(() => {
    if (initialCompany && initialCompany.trim()) {
      handleAutoSearch(initialCompany, initialLocation);
    }
  }, [initialCompany, initialLocation]);

  const handleAutoSearch = async (companyName, locationName = "") => {
    if (!companyName || !companyName.trim()) return;

    setLoading(true);
    setError("");
    setResults([]);
    setSearchPerformed(false);

    try {
      const params = {
        company: companyName.trim(),
        max_results: 15,
      };

      if (locationName && locationName.trim()) {
        params.location = locationName.trim();
      }

      const url = buildURL(API_ENDPOINTS.searchJobs, params);
      const response = await fetch(url);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || "Job search request failed");
      }


      setResults(data.results?.jobs || []);
      setSearchPerformed(true);
      setError("");
    } catch (err) {
      console.error("Auto job search error:", err);
      setError(err.message || "Failed to search for jobs. Please try again.");
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!company.trim()) {
      setError("Please enter a company name");
      return;
    }

    setLoading(true);
    setError("");
    setResults([]);
    setSearchPerformed(false);

    try {


      const params = {
        company: company.trim(),
        max_results: 15,
      };

      if (location.trim()) {
        params.location = location.trim();
      }

      const url = buildURL(API_ENDPOINTS.searchJobs, params);
      const response = await fetch(url);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || "Job search request failed");
      }


      setResults(data.results?.jobs || []);
      setSearchPerformed(true);
      setError("");
    } catch (err) {
      console.error("Job search error:", err);
      setError(
        err.message ||
          "Failed to search for jobs. Please check your connection and try again."
      );
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCompanyClick = (companyName) => {
    setCompany(companyName);
    setLocation("");
    // Auto-trigger search
    setLoading(true);
    setError("");
    setResults([]);
    setSearchPerformed(false);

    setTimeout(async () => {
      try {
        const params = {
          company: companyName,
          max_results: 15,
        };

        const url = buildURL(API_ENDPOINTS.searchJobs, params);
        const response = await fetch(url);
        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.message || "Job search request failed");
        }

        setResults(data.results?.jobs || []);
        setSearchPerformed(true);
        setError("");
      } catch (err) {
        console.error("Job search error:", err);
        setError(err.message || "Failed to search for jobs. Please try again.");
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 100);
  };

  const clearSearch = () => {
    setCompany("");
    setLocation("");
    setResults([]);
    setError("");
    setSearchPerformed(false);
  };

  return (
    <div className="job-search-container">

      <div className="job-search-header">
        <h1>🔍 Find Jobs</h1>
        <p>Search for job openings by company name and location</p>
      </div>

      {/* Job Search Form */}
      <div className="job-search-form-container">
        <form onSubmit={handleSubmit} className="job-search-form">
          <div className="search-inputs">
            <div className="input-group">
              <label htmlFor="company">Company Name *</label>
              <input
                type="text"
                id="company"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                placeholder="e.g., Google, Microsoft, Amazon..."
                disabled={loading}
                required
              />
            </div>

            <div className="input-group">
              <label htmlFor="location">Location (Optional)</label>
              <input
                type="text"
                id="location"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="e.g., India, USA, Remote..."
                disabled={loading}
              />
            </div>
          </div>

          <div className="search-actions">
            <button
              type="submit"
              disabled={loading || !company.trim()}
              className="search-button"
            >
              {loading ? "🔄 Searching..." : "🔍 Search Jobs"}
            </button>

            {(company || location || searchPerformed) && (
              <button
                type="button"
                onClick={clearSearch}
                className="clear-button"
                disabled={loading}
              >
                🗑️ Clear
              </button>
            )}
          </div>
        </form>
      </div>

      {/* API Status */}
      {jobStats && (
        <div className="job-stats-info">
          <div className="stats-item">
            <span className="stats-label">Search Status:</span>
            <span
              className={`stats-value ${
                jobStats.job_search_available
                  ? "status-available"
                  : "status-unavailable"
              }`}
            >
              {jobStats.job_search_available ? "✅ Available" : "⚠️ Limited"}
            </span>
          </div>
          <div className="stats-item">
            <span className="stats-label">Job Sources:</span>
            <span className="stats-value">
              {jobStats.supported_sources?.slice(0, 3).join(", ")}
              {jobStats.supported_sources?.length > 3 &&
                ` +${jobStats.supported_sources.length - 3} more`}
            </span>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="error-message">
          <div className="error-content">
            <span className="error-icon">⚠️</span>
            <span className="error-text">{error}</span>
          </div>
        </div>
      )}

      {/* Trending Jobs */}
      {!searchPerformed && (
        <div className="trending-jobs-section">
          <div className="section-header">
            <h3>🔥 Trending Job Openings</h3>
            <p>Latest opportunities from top companies</p>
          </div>
          
          {loadingPopularJobs ? (
            <div className="trending-jobs-loading">
              <div className="loading-spinner"></div>
              <p>Finding the latest job opportunities...</p>
            </div>
          ) : (
            <div className="trending-jobs-grid">
              {popularJobs.length > 0 ? (
                popularJobs.map((job, index) => (
                  <div key={index} className="trending-job-card">
                    <div className="job-card-header">
                      <div className="job-title">{job.title}</div>
                      <div className="job-company">
                        <span className="company-name">{job.company}</span>
                        <span className="job-source">{job.source}</span>
                      </div>
                    </div>
                    
                    <div className="job-card-details">
                      <div className="job-location">
                        <span className="location-icon">📍</span>
                        {job.location}
                      </div>
                      <div className="job-type">
                        <span className="type-icon">💼</span>
                        {job.job_type}
                      </div>
                      {job.salary && job.salary !== 'Salary Not Specified' && (
                        <div className="job-salary">
                          <span className="salary-icon">💰</span>
                          {job.salary}
                        </div>
                      )}
                    </div>
                    
                    <div className="job-card-footer">
                      <div className="job-posted">{job.posted_date}</div>
                      <button 
                        className="apply-job-btn"
                        onClick={() => window.open(job.url, '_blank', 'noopener,noreferrer')}
                      >
                        Apply Now
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <div className="no-trending-jobs">
                  <div className="no-jobs-icon">💼</div>
                  <h4>No trending jobs available</h4>
                  <p>Use the search form above to find specific opportunities</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Search Results */}
      {searchPerformed && (
        <div className="job-results-section">
          <div className="results-header">
            <h3>
              🎯 Job Results for "{company}"{location && ` in ${location}`}
            </h3>
            <div className="results-count">
              {loading ? (
                <span className="loading-text">🔄 Searching...</span>
              ) : (
                <span className="count-text">
                  {results.length === 0
                    ? "No jobs found"
                    : `${results.length} job${
                        results.length !== 1 ? "s" : ""
                      } found`}
                </span>
              )}
            </div>
          </div>

          {loading && (
            <div className="loading-container">
              <div className="loading-spinner"></div>
              <p>Searching job boards and company career pages...</p>
            </div>
          )}

          {!loading && results.length === 0 && searchPerformed && (
            <div className="no-results">
              <div className="no-results-icon">💼</div>
              <h4>No job postings found</h4>
              <p>Try these suggestions:</p>
              <ul>
                <li>Check the company name spelling</li>
                <li>Try searching without location filter</li>
                <li>
                  Use a more general company name (e.g., "Google" instead of
                  "Google LLC")
                </li>
                <li>Try searching for a different company</li>
              </ul>
            </div>
          )}

          {!loading && results.length > 0 && <JobTable jobs={results} />}
        </div>
      )}

      {/* Search Tips */}
      {!searchPerformed && (
        <div className="search-tips">
          <h4>💡 Search Tips</h4>
          <div className="tips-grid">
            <div className="tip-item">
              <span className="tip-icon">🎯</span>
              <div>
                <strong>Be Specific:</strong>
                <p>Use exact company names for better results</p>
              </div>
            </div>
            <div className="tip-item">
              <span className="tip-icon">🌍</span>
              <div>
                <strong>Add Location:</strong>
                <p>Include location for region-specific jobs</p>
              </div>
            </div>
            <div className="tip-item">
              <span className="tip-icon">🔄</span>
              <div>
                <strong>Try Variations:</strong>
                <p>Search "Google India" or "Microsoft Remote"</p>
              </div>
            </div>
            <div className="tip-item">
              <span className="tip-icon">⏰</span>
              <div>
                <strong>Fresh Results:</strong>
                <p>We search live job boards for current openings</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default JobSearch;
