import React from "react";
import "./CompanyCard.css";

const CompanyCard = ({
  company,
  selectedLocation,
  onCompanyCardClick,
  onJobSearchClick,
}) => {
  return (
    <div className="company-card">
      <div className="company-header">
        <div className="company-logo">
          <img
            src={company.logo_url}
            alt={`${company.display_name || company.name} logo`}
            className="company-logo-img"
            onError={(e) => {
              e.target.style.display = "none";
              e.target.nextSibling.style.display = "flex";
            }}
          />
          <div className="company-logo-fallback" style={{ display: "none" }}>
            {(company.display_name || company.name)
              .substring(0, 2)
              .toUpperCase()}
          </div>
        </div>
        <div className="company-basic-info">
          <h3
            className="company-name"
            title={company.display_name || company.name}
          >
            {company.display_name || company.name}
          </h3>
          <span className="company-category">{company.category}</span>
        </div>
        <div className="company-financial">
          {company.market_cap && company.market_cap !== "N/A" && (
            <span className="market-cap" title="Market Capitalization">
              {company.market_cap}
            </span>
          )}
          {company.stock_symbol && (
            <span className="stock-symbol" title="Stock Symbol">
              {company.stock_symbol}
            </span>
          )}
        </div>
      </div>

      <div className="company-description">
        <p title={company.long_description || company.description}>
          {company.description}
        </p>
      </div>

      {company.tags && company.tags.length > 0 && (
        <div className="company-tags">
          <div className="tags-header">
            <span className="tags-label">🏷️ Technologies:</span>
          </div>
          <div className="tags-list">
            {company.tags.slice(0, 4).map((tag, index) => (
              <span key={index} className="company-tag">
                {tag}
              </span>
            ))}
            {company.tags.length > 4 && (
              <span className="company-tag more-tags">
                +{company.tags.length - 4}
              </span>
            )}
          </div>
        </div>
      )}

      <div className="company-locations">
        <div className="locations-header">
          <span className="locations-label">🌍 Offices:</span>
          <span className="locations-count">({company.locations.length})</span>
        </div>
        <div className="locations-list">
          {company.locations.slice(0, 6).map((location) => (
            <button
              key={location}
              onClick={() => onCompanyCardClick(company, location)}
              className="location-chip"
              title={`Search for ${company.name} recruiters in ${location}`}
            >
              {location}
            </button>
          ))}
          {company.locations.length > 6 && (
            <span className="location-chip more-locations">
              +{company.locations.length - 6}
            </span>
          )}
        </div>
      </div>

      <div className="company-actions">
        <button
          onClick={() => onCompanyCardClick(company)}
          className="find-recruiters-btn"
        >
          🔍 Recruiters
        </button>
        {onJobSearchClick && (
          <button
            onClick={() => onJobSearchClick(company)}
            className="find-jobs-btn"
          >
            💼 Jobs
          </button>
        )}
        {company.website && (
          <a
            href={company.website}
            target="_blank"
            rel="noopener noreferrer"
            className="company-website-btn"
          >
            🌐 Site
          </a>
        )}
      </div>
    </div>
  );
};

export default CompanyCard;
