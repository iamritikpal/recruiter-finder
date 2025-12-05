import React from "react";
import RecruiterCard from "./RecruiterCard";
import "./ResumeResults.css";

const ResumeResults = ({ analysis, recommendedRecruiters }) => {
  if (!analysis) return null;

  return (
    <div className="resume-results">
      {/* Analysis Summary */}
      <div className="analysis-summary">
        <h2>📊 Resume Analysis Results</h2>

        {analysis.analysis && analysis.analysis.summary && (
          <div className="career-summary">
            <h3>💼 Career Summary</h3>
            <p>{analysis.analysis.summary}</p>
          </div>
        )}

        {analysis.analysis && analysis.analysis.experience_level && (
          <div className="experience-level">
            <h3>📈 Experience Level</h3>
            <span className="experience-badge">
              {analysis.analysis.experience_level}
            </span>
          </div>
        )}

        {analysis.analysis && analysis.analysis.industry && (
          <div className="industry">
            <h3>🏢 Industry</h3>
            <span className="industry-badge">{analysis.analysis.industry}</span>
          </div>
        )}

        {analysis.analysis &&
          analysis.analysis.skills &&
          analysis.analysis.skills.length > 0 && (
            <div className="extracted-skills">
              <h3>🛠️ Detected Skills</h3>
              <div className="skills-tags">
                {analysis.analysis.skills.map((skill, index) => (
                  <span key={index} className="skill-tag">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

        {analysis.analysis &&
          analysis.analysis.role_types &&
          analysis.analysis.role_types.length > 0 && (
            <div className="role-types">
              <h3>🎯 Suitable Roles</h3>
              <div className="roles-tags">
                {analysis.analysis.role_types.map((role, index) => (
                  <span key={index} className="role-tag">
                    {role}
                  </span>
                ))}
              </div>
            </div>
          )}

        {analysis.analysis &&
          analysis.analysis.companies &&
          analysis.analysis.companies.length > 0 && (
            <div className="companies">
              <h3>🏢 Past Companies</h3>
              <div className="companies-list">
                {analysis.analysis.companies.join(", ")}
              </div>
            </div>
          )}

        {analysis.analysis && analysis.analysis.confidence && (
          <div className="confidence">
            <h3>🎯 Analysis Confidence</h3>
            <span
              className={`confidence-badge ${analysis.analysis.confidence.toLowerCase()}`}
            >
              {analysis.analysis.confidence}
            </span>
          </div>
        )}
      </div>

      {/* Recommended Recruiters */}
      {recommendedRecruiters && recommendedRecruiters.length > 0 && (
        <div className="recommended-recruiters">
          <h2>🎯 Recommended Recruiters</h2>
          <p>
            Based on your skills and experience, here are recruiters who might
            be interested in your profile:
          </p>

          <div className="recruiters-grid">
            {recommendedRecruiters.map((recruiter, index) => (
              <div key={index} className="recommended-recruiter">
                <RecruiterCard
                  profile={recruiter}
                  searchedCompany={recruiter.target_company}
                />
                {recruiter.match_reason && (
                  <div className="match-reason">
                    <strong>Why this match:</strong> {recruiter.match_reason}
                  </div>
                )}
                {recruiter.match_score && (
                  <div className="match-score">
                    <span className="match-badge">
                      {Math.round(recruiter.match_score * 100)}% Match
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ResumeResults;
