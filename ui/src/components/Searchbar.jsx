// Searchbar.jsx
import React from 'react';
import '../styles/Searchbar.css';

const Searchbar = ({ isCollapsed }) => {
  return (
    <div className="searchbar">
      <div className={`search-icon ${isCollapsed ? 'collapsed' : ''}`}>
      </div>
      <input type="text" placeholder="Search for threads ..." className={`search-input ${isCollapsed ? 'collapsed' : ''}`} />
    </div>
  );
};

export default Searchbar;