import React from "react";
import FileUpload from "../forms/FileUpload";
import ResumeResults from "../common/ResumeResults";
import { API_ENDPOINTS } from "../../config/api";
import "./ResumeAnalysis.css";

const ResumeAnalysis = ({
  resumeFile,
  setResumeFile,
  resumeAnalysis,
  setResumeAnalysis,
  resumeLoading,
  setResumeLoading,
  resumeError,
  setResumeError,
  recommendedRecruiters,
  setRecommendedRecruiters,
}) => {
  const handleFileUpload = async (file) => {
    setResumeFile(file);
    setResumeError("");
    setResumeLoading(true);

    try {
      const formData = new FormData();
      formData.append("resume", file);

      const response = await fetch(API_ENDPOINTS.analyzeResume, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setResumeAnalysis(data);
        setRecommendedRecruiters(data.recommended_recruiters || []);
      } else {
        throw new Error(data.message || "Failed to analyze resume");
      }
    } catch (error) {
      console.error("Error analyzing resume:", error);
      setResumeError(error.message || "Failed to analyze resume");
      setResumeAnalysis(null);
      setRecommendedRecruiters([]);
    } finally {
      setResumeLoading(false);
    }
  };

  return (
    <div className="main-content">
      <div className="content-header">
        <h1>📄 Smart Resume Analysis</h1>
        <p>
          Upload your resume to get AI-powered analysis, skill extraction, and
          personalized recruiter recommendations
        </p>
      </div>

      <FileUpload
        onFileUpload={handleFileUpload}
        loading={resumeLoading}
        error={resumeError}
        file={resumeFile}
      />

      {resumeAnalysis && (
        <ResumeResults
          analysis={resumeAnalysis}
          recommendedRecruiters={recommendedRecruiters}
        />
      )}
    </div>
  );
};

export default ResumeAnalysis;
