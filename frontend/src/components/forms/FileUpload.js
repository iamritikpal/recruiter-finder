import React from "react";
import "./FileUpload.css";

const FileUpload = ({ onFileUpload, loading, error, file }) => {
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      onFileUpload(selectedFile);
    }
  };

  return (
    <div className="upload-section">
      <div className="file-upload-container">
        <input
          type="file"
          id="resume-upload"
          className="file-input"
          accept=".pdf,.doc,.docx,.txt"
          onChange={handleFileChange}
          disabled={loading}
        />
        <label htmlFor="resume-upload" className="file-upload-label">
          <div className="upload-icon">📄</div>
          <div className="upload-text">
            <span className="upload-title">
              {file ? file.name : "Drop your resume here or click to browse"}
            </span>
            <span className="upload-subtitle">
              Supports PDF, DOC, DOCX, and TXT files (max 10MB)
            </span>
          </div>
        </label>
      </div>

      {loading && (
        <div className="upload-status loading">
          <div className="upload-spinner"></div>
          <p>Analyzing your resume with AI...</p>
          <div className="upload-progress">
            <div className="progress-bar"></div>
          </div>
        </div>
      )}

      {error && (
        <div className="upload-status error">
          <div className="error-icon">⚠️</div>
          <p>{error}</p>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
