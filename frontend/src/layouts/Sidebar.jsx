import React from 'react';
import { NavLink } from 'react-router-dom';
import './Sidebar.css';

const Sidebar = () => {
  const menuItems = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/dashboard/search', label: 'AI Search', icon: '🔍' },
    { path: '/dashboard/photos', label: 'Site Photos', icon: '📷' },
    { path: '/dashboard/analytics', label: 'Analytics', icon: '📈' }
  ];

  // Mock recent queries
  const recentQueries = [
    'Last 7 days concrete work',
    'Excavation progress',
    'Safety equipment violations',
    'Electrical installations',
    'Foundation photos'
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2 className="sidebar-title">AI Site Monitor</h2>
      </div>

      <nav className="sidebar-nav">
        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => 
              `sidebar-nav-item ${isActive ? 'active' : ''}`
            }
            end={item.path === '/dashboard'}
          >
            <span className="sidebar-nav-icon">{item.icon}</span>
            <span className="sidebar-nav-label">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-recent">
        <h3 className="sidebar-recent-title">Recent Queries</h3>
        <div className="sidebar-recent-list">
          {recentQueries.map((query, index) => (
            <button
              key={index}
              className="sidebar-recent-item"
              onClick={() => console.log('Query:', query)}
              title={query}
            >
              {query}
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
