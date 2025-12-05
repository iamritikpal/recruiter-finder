import React from "react";
import CompanyFilters from "../common/CompanyFilters";
import CompanyGrid from "../common/CompanyGrid";
import LoadingSpinner from "../common/LoadingSpinner";
import ErrorMessage from "../common/ErrorMessage";
import "./CompanyGallery.css";

const CompanyGallery = ({
  selectedLocation,
  setSelectedLocation,
  companySearch,
  setCompanySearch,
  filteredCompanies,
  companyGalleryLoading,
  companyGalleryError,
  availableLocations,
  totalCompaniesCount,
  availableCategories,
  handleCompanyCardClick,
  handleJobSearchClick,
  fetchCompanies,
}) => {
  const handleLocationFilter = (location) => {
    setSelectedLocation(location);
  };

  const handleCompanySearch = (e) => {
    setCompanySearch(e.target.value);
  };

  const handleRefreshCache = async () => {
    await fetchCompanies(true);
  };

  return (
    <div className="main-content">
      <div className="content-header">
        <h1>🏢 Company Gallery</h1>
        <p>
          Explore 120+ companies across all industries. Click on any company to
          find recruiters and start your job search journey.
        </p>
      </div>

      <CompanyFilters
        selectedLocation={selectedLocation}
        onLocationFilter={handleLocationFilter}
        companySearch={companySearch}
        onCompanySearch={handleCompanySearch}
        availableLocations={availableLocations}
        filteredCompanies={filteredCompanies}
        totalCompaniesCount={totalCompaniesCount}
        onRefreshCache={handleRefreshCache}
      />

      {/* Loading State */}
      {companyGalleryLoading && (
        <LoadingSpinner message="Loading companies from APIs..." />
      )}

      {/* Error State */}
      {companyGalleryError && (
        <ErrorMessage
          title="⚠️ Unable to Load Companies"
          message={companyGalleryError}
          onRetry={() => fetchCompanies(true)}
        />
      )}

      {/* Companies Grid */}
      {!companyGalleryLoading && !companyGalleryError && (
        <CompanyGrid
          companies={filteredCompanies}
          selectedLocation={selectedLocation}
          companySearch={companySearch}
          onCompanyCardClick={handleCompanyCardClick}
          onJobSearchClick={handleJobSearchClick}
          totalCompaniesCount={totalCompaniesCount}
          availableLocations={availableLocations}
          availableCategories={availableCategories}
          onLocationFilter={handleLocationFilter}
          onCompanySearch={handleCompanySearch}
        />
      )}
    </div>
  );
};

export default CompanyGallery;
