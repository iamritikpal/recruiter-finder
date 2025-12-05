import React from "react";
import RecruiterRow from "./RecruiterRow";
import "./RecruiterTable.css";

const RecruiterTable = ({ profiles, searchedCompany }) => {
  if (!profiles || profiles.length === 0) {
    return (
      <div className="no-results">
        <p>No recruiters found. Try searching for a different company.</p>
      </div>
    );
  }

  return (
    <div className="recruiter-table-container">
      <div className="table-header">
        <h3>Found {profiles.length} Recruiters</h3>
        <p className="table-subtitle">
          Click on email/phone buttons to find contact information
        </p>
      </div>

      <div className="recruiter-table">
        <div className="table-header-row">
          <div className="header-cell name-cell">Name & Title</div>
          <div className="header-cell company-cell">LinkedIn</div>
          <div className="header-cell actions-cell">Contact Actions</div>
          <div className="header-cell contact-cell">Contact Info</div>
        </div>

        <div className="table-body">
          {profiles.map((profile, index) => (
            <RecruiterRow
              key={index}
              profile={profile}
              searchedCompany={searchedCompany}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default RecruiterTable;
