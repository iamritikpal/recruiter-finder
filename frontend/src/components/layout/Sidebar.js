import React, { useState } from "react";
import { useAuth } from "../../contexts/AuthContext";
import "./Sidebar.css";

const Sidebar = ({ activeTab, setActiveTab }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { logout } = useAuth();

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    setIsMobileMenuOpen(false); // Close mobile menu when switching tabs
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const handleLogout = () => {
    logout();
    setIsMobileMenuOpen(false);
  };

  return (
    <>
      {/* Mobile Header */}
      <header className="mobile-header">
        <div className="header-content">
          <h1 className="app-title">🔍 RecruiterFinder</h1>
          <button
            className="mobile-menu-toggle"
            onClick={toggleMobileMenu}
            aria-label="Toggle mobile menu"
          >
            <span className="hamburger-icon">
              <span></span>
              <span></span>
              <span></span>
            </span>
          </button>
        </div>
      </header>

      {/* Mobile Overlay */}
      {isMobileMenuOpen && (
        <div
          className="mobile-overlay"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`sidebar ${isMobileMenuOpen ? "mobile-open" : ""}`}>
        {/* Sidebar Header */}
        <div className="sidebar-header">
          <div className="app-logo">
            <h1>🔍</h1>
          </div>
          <div className="app-title-sidebar">
            <h2>RecruiterFinder</h2>
            <p>AI-Powered Recruitment</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="sidebar-nav">
          <button
            className={`nav-item ${
              activeTab === "resume-analysis" ? "active" : ""
            }`}
            onClick={() => handleTabChange("resume-analysis")}
          >
            <span className="nav-icon">📄</span>
            <span className="nav-text">Resume Analysis</span>
          </button>

          <button
            className={`nav-item ${
              activeTab === "company-search" ? "active" : ""
            }`}
            onClick={() => handleTabChange("company-search")}
          >
            <span className="nav-icon">🔍</span>
            <span className="nav-text">Find Recruiters</span>
          </button>

          <button
            className={`nav-item ${
              activeTab === "company-gallery" ? "active" : ""
            }`}
            onClick={() => handleTabChange("company-gallery")}
          >
            <span className="nav-icon">🏢</span>
            <span className="nav-text">Company Gallery</span>
          </button>

          <button
            className={`nav-item ${activeTab === "job-search" ? "active" : ""}`}
            onClick={() => handleTabChange("job-search")}
          >
            <span className="nav-icon">💼</span>
            <span className="nav-text">Find Jobs</span>
          </button>
        </nav>

        {/* Logout Section */}
        <div className="sidebar-logout">
          <button
            className="logout-button"
            onClick={handleLogout}
            title="Sign out of your account"
          >
            <span className="nav-icon">🚪</span>
            <span className="nav-text">Logout</span>
          </button>
        </div>

        <div className="sidebar-footer">
          <div className="sidebar-info">
            <p>Powered by AI</p>
            <p>
              Made with ❤️ by
              <a
                className="my-linkedin-link"
                href="https://www.linkedin.com/in/ritik-pal-1a8255168/"
              >
                Ritik Pal
              </a>
            </p>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
