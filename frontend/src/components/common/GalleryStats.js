import React from "react";
import "./GalleryStats.css";

const GalleryStats = ({
  totalCompaniesCount,
  availableLocations,
  availableCategories,
  filteredCompanies,
}) => {
  return (
    <div className="gallery-stats">
      <div className="stat-card">
        <div className="stat-number">{totalCompaniesCount}</div>
        <div className="stat-label">Total Companies</div>
      </div>
      <div className="stat-card">
        <div className="stat-number">{availableLocations.length}</div>
        <div className="stat-label">Global Locations</div>
      </div>
      <div className="stat-card">
        <div className="stat-number">{availableCategories.length}</div>
        <div className="stat-label">Industries</div>
      </div>
      <div className="stat-card">
        <div className="stat-number">{filteredCompanies.length}</div>
        <div className="stat-label">Filtered Results</div>
      </div>
    </div>
  );
};

export default GalleryStats;
