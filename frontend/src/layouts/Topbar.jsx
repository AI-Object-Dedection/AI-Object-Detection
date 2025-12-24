import React, { useState } from 'react';
import './Topbar.css';

const Topbar = ({ title = 'AI-Powered Reporting' }) => {
  const [showExportMenu, setShowExportMenu] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  const handleExport = (format) => {
    alert(`Export as ${format} - Feature coming soon!`);
    setShowExportMenu(false);
  };

  const handleScheduleReport = () => {
    alert('Schedule Report - Feature coming soon!');
  };

  return (
    <header className="topbar">
      <div className="topbar-left">
        <h1 className="topbar-title">{title}</h1>
      </div>

      <div className="topbar-right">
        {/* Export Dropdown */}
        <div className="topbar-dropdown">
          <button
            className="topbar-btn"
            onClick={() => setShowExportMenu(!showExportMenu)}
          >
            <span className="topbar-btn-icon">📥</span>
            Export
          </button>
          {showExportMenu && (
            <div className="topbar-dropdown-menu">
              <button onClick={() => handleExport('ZIP')}>
                Export as ZIP
              </button>
              <button onClick={() => handleExport('CSV')}>
                Export as CSV
              </button>
              <button onClick={() => handleExport('JSON')}>
                Export as JSON
              </button>
              <button onClick={() => handleExport('PDF')}>
                Export as PDF
              </button>
            </div>
          )}
        </div>

        {/* Schedule Report Button */}
        <button className="topbar-btn primary" onClick={handleScheduleReport}>
          <span className="topbar-btn-icon">📅</span>
          Schedule Report
        </button>

        {/* User Menu */}
        <div className="topbar-dropdown">
          <button
            className="topbar-user-btn"
            onClick={() => setShowUserMenu(!showUserMenu)}
          >
            <div className="topbar-avatar">
              <span>JD</span>
            </div>
            <div className="topbar-user-info">
              <span className="topbar-user-name">John Doe</span>
              <span className="topbar-user-role">Project Manager</span>
            </div>
          </button>
          {showUserMenu && (
            <div className="topbar-dropdown-menu right">
              <button onClick={() => alert('Profile')}>Profile</button>
              <button onClick={() => alert('Settings')}>Settings</button>
              <button onClick={() => alert('Logout')}>Logout</button>
            </div>
          )}
        </div>
      </div>

      {/* Click outside to close dropdowns */}
      {(showExportMenu || showUserMenu) && (
        <div
          className="topbar-overlay"
          onClick={() => {
            setShowExportMenu(false);
            setShowUserMenu(false);
          }}
        />
      )}
    </header>
  );
};

export default Topbar;
