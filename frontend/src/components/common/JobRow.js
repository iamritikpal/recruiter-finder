import React, { useState } from "react";
import "./JobRow.css";

const JobRow = ({ job }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleApplyClick = () => {
    window.open(job.url, "_blank", "noopener,noreferrer");
  };

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  const getSourceIcon = (source) => {
    const sourceIcons = {
      LinkedIn: "💼",
      Indeed: "🔍",
      Glassdoor: "🏢",
      Naukri: "🇮🇳",
      Monster: "👹",
      "Company Career Page": "🏛️",
      Other: "🌐",
    };
    return sourceIcons[source] || "🌐";
  };

  const getJobTypeColor = (jobType) => {
    const typeColors = {
      "Full-time": "job-type-fulltime",
      "Part-time": "job-type-parttime",
      Contract: "job-type-contract",
      Internship: "job-type-internship",
      Freelance: "job-type-freelance",
      Temporary: "job-type-temporary",
      Permanent: "job-type-permanent",
    };
    return typeColors[jobType] || "job-type-default";
  };

  const getRelevanceColor = (score) => {
    if (score >= 80) return "relevance-high";
    if (score >= 60) return "relevance-medium";
    return "relevance-low";
  };

  const formatSalary = (salary) => {
    if (
      !salary ||
      salary === "Salary Not Specified" ||
      salary === "Not Specified"
    ) {
      return "Not specified";
    }
    return salary;
  };

  const formatDate = (dateStr) => {
    if (
      !dateStr ||
      dateStr === "Date Not Specified" ||
      dateStr === "Not Specified"
    ) {
      return "Recently";
    }
    return dateStr;
  };

  return (
    <>
      <tr
        className={`job-row ${isExpanded ? "expanded" : ""}`}
        onClick={toggleExpanded}
      >
        <td className="job-title-cell">
          <div className="job-title-content">
            <div className="job-title">{job.title}</div>
            <div className="job-company">
              <span className="company-name">{job.company}</span>
              {job.relevance_score && (
                <span
                  className={`relevance-score ${getRelevanceColor(
                    job.relevance_score
                  )}`}
                >
                  {job.relevance_score}% match
                </span>
              )}
            </div>
          </div>
        </td>

        <td className="job-details-cell">
          <div className="job-details-content">
            <div className="job-location">
              <span className="location-icon">📍</span>
              {job.location}
            </div>
            <div className="job-type-container">
              <span
                className={`job-type-badge ${getJobTypeColor(job.job_type)}`}
              >
                {job.job_type}
              </span>
            </div>
          </div>
        </td>

        <td className="job-source-cell">
          <div className="job-source-content">
            <div className="job-source">
              <span className="source-icon">{getSourceIcon(job.source)}</span>
              {job.source}
            </div>
            <div className="job-date">
              <span className="date-icon">⏰</span>
              {formatDate(job.posted_date)}
            </div>
          </div>
        </td>

        <td className="job-salary-cell">
          <div className="job-salary">💰 {formatSalary(job.salary)}</div>
        </td>

        <td className="job-actions-cell">
          <button
            className="apply-button"
            onClick={(e) => {
              e.stopPropagation();
              handleApplyClick();
            }}
            title="Apply for this job"
          >
            🚀 Apply
          </button>
        </td>
      </tr>

      {isExpanded && (
        <tr className="job-expanded-row">
          <td colSpan="5">
            <div className="job-expanded-content">
              <div className="job-description">
                <h4>📝 Job Description</h4>
                <p>{job.snippet}</p>
              </div>

              <div className="job-meta">
                <div className="meta-grid">
                  <div className="meta-item">
                    <span className="meta-label">🔗 Job URL:</span>
                    <a
                      href={job.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="meta-link"
                      onClick={(e) => e.stopPropagation()}
                    >
                      View Original Posting
                    </a>
                  </div>

                  {job.found_timestamp && (
                    <div className="meta-item">
                      <span className="meta-label">🕐 Found:</span>
                      <span className="meta-value">
                        {new Date(job.found_timestamp).toLocaleString()}
                      </span>
                    </div>
                  )}

                  <div className="meta-item">
                    <span className="meta-label">🎯 Source:</span>
                    <span className="meta-value">{job.source}</span>
                  </div>

                  {job.relevance_score && (
                    <div className="meta-item">
                      <span className="meta-label">📊 Relevance:</span>
                      <span
                        className={`meta-value ${getRelevanceColor(
                          job.relevance_score
                        )}`}
                      >
                        {job.relevance_score}% match
                      </span>
                    </div>
                  )}
                </div>
              </div>

              <div className="expanded-actions">
                <button
                  className="apply-button-large"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleApplyClick();
                  }}
                >
                  🚀 Apply for this Job
                </button>
                <button
                  className="collapse-button"
                  onClick={(e) => {
                    e.stopPropagation();
                    setIsExpanded(false);
                  }}
                >
                  ⬆️ Collapse
                </button>
              </div>
            </div>
          </td>
        </tr>
      )}
    </>
  );
};

export default JobRow;
