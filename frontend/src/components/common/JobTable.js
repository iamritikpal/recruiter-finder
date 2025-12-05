import React from "react";
import JobRow from "./JobRow";
import "./JobTable.css";

const JobTable = ({ jobs }) => {
  if (!jobs || jobs.length === 0) {
    return null;
  }

  return (
    <div className="job-table-container">
      <div className="job-table-wrapper">
        <table className="job-table">
          <thead className="job-table-header">
            <tr>
              <th className="job-title-column">Job Title & Company</th>
              <th className="job-details-column">Location & Type</th>
              <th className="job-source-column">Source & Date</th>
              <th className="job-salary-column">Salary</th>
              <th className="job-actions-column">Actions</th>
            </tr>
          </thead>
          <tbody>
            {jobs.map((job, index) => (
              <JobRow key={`${job.url}-${index}`} job={job} />
            ))}
          </tbody>
        </table>
      </div>

      <div className="job-table-footer">
        <div className="table-info">
          <span className="job-count">
            {jobs.length} job{jobs.length !== 1 ? "s" : ""} found
          </span>
          <span className="table-note">
            🔄 Jobs are updated in real-time from multiple sources
          </span>
        </div>
      </div>
    </div>
  );
};

export default JobTable;
