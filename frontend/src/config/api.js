/**
 * API Configuration
 * Centralized backend URL configuration for easy environment switching
 */

// Backend URL Configuration
const API_CONFIG = {
  // Development (localhost)
  development: process.env.REACT_APP_API_URL || "http://localhost:5000",

  // Production (Render or other deployment)
  production: process.env.REACT_APP_API_URL || "http://localhost:5000", // Replace with your actual Render URL
  // "https://find-recruiter-backend.onrender.com", // Replace with your actual Render URL

  // Staging (if needed)
  staging: process.env.REACT_APP_API_URL || "http://localhost:5000",
  // "https://find-recruiter-backend.onrender.com",
};

// Determine current environment
const getCurrentEnvironment = () => {
  // TEMPORARY FIX: Force production API for testing
  // TODO: Remove this when .env is working or for actual deployment
  if (window.location.hostname === "localhost") {
    console.log("🔧 TEMPORARY: Forcing production API for localhost testing");
    return "production";
  }

  // Check if we're in development mode
  if (process.env.NODE_ENV === "development") {
    return "development";
  }

  // Check if we're running on localhost
  if (
    window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1"
  ) {
    return "development";
  }

  // Check for staging environment
  if (window.location.hostname.includes("staging")) {
    return "staging";
  }

  // Default to production
  return "production";
};

// Get the appropriate base URL
const getBaseURL = () => {
  // Debug: Log all environment variables
  console.log("🔧 DEBUG: All environment variables:", {
    REACT_APP_API_URL: process.env.REACT_APP_API_URL,
    REACT_APP_USE_PRODUCTION_API: process.env.REACT_APP_USE_PRODUCTION_API,
    NODE_ENV: process.env.NODE_ENV,
  });

  // Check for explicit override via environment variable
  if (process.env.REACT_APP_API_URL) {
    console.log("🔧 Using explicit API URL:", process.env.REACT_APP_API_URL);
    return process.env.REACT_APP_API_URL;
  }

  // Check for development override to use production backend
  if (process.env.REACT_APP_USE_PRODUCTION_API === "true") {
    console.log("🔧 Development override: Using production API");
    return API_CONFIG.production;
  }

  const environment = getCurrentEnvironment();
  console.log("🔧 Auto-detected environment:", environment);
  console.log("🔧 Selected API URL:", API_CONFIG[environment]);
  return API_CONFIG[environment];
};

// Main API configuration
export const API_BASE_URL = getBaseURL();
console.log("🔧 Final API_BASE_URL:", API_BASE_URL);

// API endpoints - Matching the DEPLOYED backend routes (as of current deployment)
export const API_ENDPOINTS = {
  // Health check (no /api prefix) - DEPLOYED: /health ✅
  health: `${API_BASE_URL}/health`,

  // Resume analysis (has /api prefix) - DEPLOYED: /api/analyze-resume ✅
  analyzeResume: `${API_BASE_URL}/api/analyze-resume`,

  // Company and recruiter search (has /api prefix) - DEPLOYED: /api/search, /api/companies ✅
  searchRecruiters: `${API_BASE_URL}/api/search`,
  getCompanies: `${API_BASE_URL}/api/companies`,

  // Contact finding (has /api prefix) - DEPLOYED: /api/find_contact, /api/find_phone ✅
  findContact: `${API_BASE_URL}/api/find_contact`,
  findPhone: `${API_BASE_URL}/api/find_phone`,
  guessEmails: `${API_BASE_URL}/api/guess_emails`,

  // Job search (has /api prefix) - NEW: /api/search-jobs, /api/jobs-by-company
  searchJobs: `${API_BASE_URL}/api/search-jobs`,
  getJobsByCompany: `${API_BASE_URL}/api/jobs-by-company`,
  testJobSearch: `${API_BASE_URL}/api/test-job-search`,
  getJobStats: `${API_BASE_URL}/api/job-stats`,
  getPopularCompanies: `${API_BASE_URL}/api/popular-companies`,
};

// Helper function to build URL with query parameters
export const buildURL = (endpoint, params = {}) => {
  const url = new URL(endpoint);
  Object.keys(params).forEach((key) => {
    if (params[key] !== undefined && params[key] !== null) {
      url.searchParams.append(key, params[key]);
    }
  });
  return url.toString();
};

// Environment info for debugging
export const getEnvironmentInfo = () => {
  return {
    environment: getCurrentEnvironment(),
    baseURL: API_BASE_URL,
    hostname: window.location.hostname,
    nodeEnv: process.env.NODE_ENV,
  };
};

// Log current configuration (only in development)
if (getCurrentEnvironment() === "development") {
  console.log("🔧 API Configuration:", getEnvironmentInfo());
}

export default {
  API_BASE_URL,
  API_ENDPOINTS,
  buildURL,
  getEnvironmentInfo,
};
