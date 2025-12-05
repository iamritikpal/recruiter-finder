import React, { useState } from "react";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import LoginPage from "./components/auth/LoginPage";
import Layout from "./components/layout/Layout";
import ResumeAnalysis from "./components/pages/ResumeAnalysis";
import CompanySearch from "./components/pages/CompanySearch";
import CompanyGallery from "./components/pages/CompanyGallery";
import JobSearch from "./components/pages/JobSearch";
import useCompanyData from "./hooks/useCompanyData";
import "./styles/App.css";

// Main App Component (with authentication)
const MainApp = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        }}
      >
        <div
          style={{
            color: "white",
            fontSize: "1.2rem",
            fontWeight: "600",
            display: "flex",
            alignItems: "center",
            gap: "1rem",
          }}
        >
          <div
            style={{
              width: "24px",
              height: "24px",
              border: "3px solid rgba(255,255,255,0.3)",
              borderTop: "3px solid white",
              borderRadius: "50%",
              animation: "spin 1s linear infinite",
            }}
          ></div>
          Loading RecruiterFinder...
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  return <AuthenticatedApp />;
};

// Authenticated App Component (existing functionality)
const AuthenticatedApp = () => {
  // Navigation state
  const [activeTab, setActiveTab] = useState("resume-analysis");

  // Company search states
  const [company, setCompany] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [searchPerformed, setSearchPerformed] = useState(false);
  const [lastSearchedCompany, setLastSearchedCompany] = useState("");
  const [lastSearchResponse, setLastSearchResponse] = useState(null);
  const [searchCount, setSearchCount] = useState(0);

  // Resume analysis states
  const [resumeFile, setResumeFile] = useState(null);
  const [resumeAnalysis, setResumeAnalysis] = useState(null);
  const [resumeLoading, setResumeLoading] = useState(false);
  const [resumeError, setResumeError] = useState("");
  const [recommendedRecruiters, setRecommendedRecruiters] = useState([]);

  // Company Gallery states
  const [selectedLocation, setSelectedLocation] = useState("all");
  const [companySearch, setCompanySearch] = useState("");

  // Job search states
  const [jobSearchCompany, setJobSearchCompany] = useState("");
  const [jobSearchLocation, setJobSearchLocation] = useState("");

  // Use custom hook for company data
  const {
    filteredCompanies,
    availableLocations,
    availableCategories,
    totalCompaniesCount,
    companyGalleryLoading,
    companyGalleryError,
    fetchCompanies,
  } = useCompanyData(activeTab, selectedLocation, companySearch);

  const handleCompanyCardClick = async (company, location = null) => {
    // Switch to recruiter search tab and pre-fill company
    const searchTerm = location ? `${company.name} ${location}` : company.name;
    setCompany(searchTerm);
    setActiveTab("company-search");
    setError("");
    setResults([]);
    setSearchPerformed(false);
  };

  const handleJobSearchClick = async (company, location = null) => {
    // Switch to job search tab and pre-fill company information
    const companyName = company.name || company;
    setJobSearchCompany(companyName);
    setJobSearchLocation(location || "");
    setActiveTab("job-search");
  };

  const renderCurrentPage = () => {
    switch (activeTab) {
      case "resume-analysis":
        return (
          <ResumeAnalysis
            resumeFile={resumeFile}
            setResumeFile={setResumeFile}
            resumeAnalysis={resumeAnalysis}
            setResumeAnalysis={setResumeAnalysis}
            resumeLoading={resumeLoading}
            setResumeLoading={setResumeLoading}
            resumeError={resumeError}
            setResumeError={setResumeError}
            recommendedRecruiters={recommendedRecruiters}
            setRecommendedRecruiters={setRecommendedRecruiters}
          />
        );
      case "company-search":
        return (
          <CompanySearch
            company={company}
            setCompany={setCompany}
            results={results}
            setResults={setResults}
            loading={loading}
            setLoading={setLoading}
            error={error}
            setError={setError}
            searchPerformed={searchPerformed}
            setSearchPerformed={setSearchPerformed}
            lastSearchedCompany={lastSearchedCompany}
            setLastSearchedCompany={setLastSearchedCompany}
            lastSearchResponse={lastSearchResponse}
            setLastSearchResponse={setLastSearchResponse}
            searchCount={searchCount}
            setSearchCount={setSearchCount}
          />
        );
      case "company-gallery":
        return (
          <CompanyGallery
            selectedLocation={selectedLocation}
            setSelectedLocation={setSelectedLocation}
            companySearch={companySearch}
            setCompanySearch={setCompanySearch}
            filteredCompanies={filteredCompanies}
            companyGalleryLoading={companyGalleryLoading}
            companyGalleryError={companyGalleryError}
            availableLocations={availableLocations}
            totalCompaniesCount={totalCompaniesCount}
            availableCategories={availableCategories}
            handleCompanyCardClick={handleCompanyCardClick}
            handleJobSearchClick={handleJobSearchClick}
            fetchCompanies={fetchCompanies}
          />
        );
      case "job-search":
        return (
          <JobSearch
            initialCompany={jobSearchCompany}
            initialLocation={jobSearchLocation}
          />
        );
      default:
        return null;
    }
  };

  return (
    <Layout activeTab={activeTab} setActiveTab={setActiveTab}>
      {renderCurrentPage()}
    </Layout>
  );
};

// Root App Component with Auth Provider
const App = () => {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
};

export default App;
