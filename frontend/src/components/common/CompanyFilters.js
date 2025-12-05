import React from "react";
import "./CompanyFilters.css";

const CompanyFilters = ({
  selectedLocation,
  onLocationFilter,
  companySearch,
  onCompanySearch,
  availableLocations,
  filteredCompanies,
  totalCompaniesCount,
  onRefreshCache,
}) => {
  const clearFilters = () => {
    onLocationFilter("all");
    onCompanySearch({ target: { value: "" } });
  };

  return (
    <div className="company-filters">
      <div className="filter-row">
        <div className="search-filter">
          <input
            type="text"
            placeholder="Search companies by name, category, or technology..."
            value={companySearch}
            onChange={onCompanySearch}
            className="company-search-input"
          />
        </div>
        <div className="location-filter">
          <select
            value={selectedLocation}
            onChange={(e) => onLocationFilter(e.target.value)}
            className="location-select"
          >
            <option value="all">All Locations</option>
            {availableLocations.map((location) => (
              <option key={location} value={location}>
                {location}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="filter-info">
        <div className="results-count">
          <span
            className={
              selectedLocation !== "all" ? "location-filter-active" : ""
            }
          >
            {selectedLocation !== "all" && `📍 ${selectedLocation} • `}
          </span>
          <span className={companySearch ? "search-filter-active" : ""}>
            {companySearch && `🔍 "${companySearch}" • `}
          </span>
          Showing {filteredCompanies.length} of {totalCompaniesCount} companies
        </div>

        <div className="filter-actions">
          {(selectedLocation !== "all" || companySearch) && (
            <button onClick={clearFilters} className="clear-filters-btn">
              Clear Filters
            </button>
          )}
          <button onClick={onRefreshCache} className="refresh-cache-btn">
            🔄 Refresh Data
          </button>
        </div>
      </div>
    </div>
  );
};

export default CompanyFilters;
