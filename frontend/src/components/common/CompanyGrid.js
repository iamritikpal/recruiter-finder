import React from "react";
import CompanyCard from "./CompanyCard";
import GalleryStats from "./GalleryStats";
import "./CompanyGrid.css";

const CompanyGrid = ({
  companies,
  selectedLocation,
  companySearch,
  onCompanyCardClick,
  onJobSearchClick,
  totalCompaniesCount,
  availableLocations,
  availableCategories,
  onLocationFilter,
  onCompanySearch,
}) => {
  return (
    <>
      <div className="companies-grid">
        {companies.map((company) => (
          <CompanyCard
            key={company.id}
            company={company}
            selectedLocation={selectedLocation}
            onCompanyCardClick={onCompanyCardClick}
            onJobSearchClick={onJobSearchClick}
          />
        ))}
      </div>

      {/* No Results */}
      {companies.length === 0 && (
        <div className="no-companies-found">
          <h3>No companies found</h3>
          <p>
            {selectedLocation !== "all"
              ? `No companies found in ${selectedLocation}${
                  companySearch ? ` matching "${companySearch}"` : ""
                }.`
              : `No companies matching "${companySearch}".`}
          </p>
          <button
            onClick={() => {
              onLocationFilter("all");
              onCompanySearch({ target: { value: "" } });
            }}
            className="reset-filters-btn"
          >
            Reset Filters
          </button>
        </div>
      )}

      {/* Quick Stats */}
      <GalleryStats
        totalCompaniesCount={totalCompaniesCount}
        availableLocations={availableLocations}
        availableCategories={availableCategories}
        filteredCompanies={companies}
      />
    </>
  );
};

export default CompanyGrid;
