import { useState, useEffect } from "react";
import { API_ENDPOINTS, buildURL } from "../config/api";

const useCompanyData = (activeTab, selectedLocation, companySearch) => {
  const [companiesData, setCompaniesData] = useState([]);
  const [filteredCompanies, setFilteredCompanies] = useState([]);
  const [availableLocations, setAvailableLocations] = useState([]);
  const [availableCategories, setAvailableCategories] = useState([]);
  const [totalCompaniesCount, setTotalCompaniesCount] = useState(0);
  const [companyGalleryLoading, setCompanyGalleryLoading] = useState(false);
  const [companyGalleryError, setCompanyGalleryError] = useState("");
  const [cacheStatus, setCacheStatus] = useState(null);
  const [cacheStats, setCacheStats] = useState(null);
  const [showCacheInfo, setShowCacheInfo] = useState(false);

  // Fetch companies data when gallery tab is active
  useEffect(() => {
    if (activeTab === "company-gallery") {
      fetchCompanies();
    }
  }, [activeTab, selectedLocation, companySearch]);

  const fetchCompanies = async (forceRefresh = false) => {
    if (companyGalleryLoading) return; // Prevent duplicate calls

    setCompanyGalleryLoading(true);
    setCompanyGalleryError("");

    try {
      // Build query parameters
      const params = new URLSearchParams();
      if (selectedLocation !== "all") {
        params.append("location", selectedLocation);
      }
      if (companySearch.trim()) {
        params.append("search", companySearch.trim());
      }
      if (forceRefresh) {
        params.append("force_refresh", "true");
      }

      const companiesURL = buildURL(
        API_ENDPOINTS.getCompanies,
        Object.fromEntries(params)
      );
      console.log("Fetching companies from:", companiesURL);
      const response = await fetch(companiesURL);
      console.log("Response status:", response.status);
      const data = await response.json();

      if (response.ok && data.success) {
        setCompaniesData(data.companies || []);
        setFilteredCompanies(data.companies || []);
        setAvailableLocations(data.available_locations || []);
        setAvailableCategories(data.available_categories || []);
        setTotalCompaniesCount(data.total_count || 0);
        setCacheStatus(data.cache_status);
        setCacheStats(data.cache_stats);
      } else {
        throw new Error(data.message || "Failed to fetch companies");
      }
    } catch (error) {
      console.error("Error fetching companies:", error);
      console.error("Error details:", error.message);
      setCompanyGalleryError(
        `Failed to load companies: ${error.message}. Please check your connection and try again.`
      );
      setCompaniesData([]);
      setFilteredCompanies([]);
    } finally {
      setCompanyGalleryLoading(false);
    }
  };

  return {
    companiesData,
    filteredCompanies,
    availableLocations,
    availableCategories,
    totalCompaniesCount,
    companyGalleryLoading,
    companyGalleryError,
    cacheStatus,
    cacheStats,
    showCacheInfo,
    setShowCacheInfo,
    fetchCompanies,
  };
};

export default useCompanyData;
