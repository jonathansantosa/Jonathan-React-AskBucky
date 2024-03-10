// DarkModeSlider.js
import React, { useState } from 'react';
import '../styles/DarkModeButton.css'; // Create a new CSS file for this component

const ToggleDarkMode = ({ onToggle, isDarkModeActive }) => {
  return (
    <div 
      className={`dark-mode-button ${isDarkModeActive ? 'active' : ''}`} 
      onClick={() => {
        localStorage.setItem("darkMode", JSON.stringify(!isDarkModeActive));
        onToggle(!isDarkModeActive);
      }}
    >
      {isDarkModeActive 
        ? <i className='bx bxs-moon'></i>
        : <i className='bx bx-moon'></i>}
      {isDarkModeActive 
      ? <span className="tooltip">Lightmode</span>
      : <span className="tooltip">Darkmode</span>}
    </div>
  );
};

const DarkModeSlider = ({ onToggleDarkMode }) => {
  const [isDarkModeActive, setDarkModeActive] = useState(JSON.parse(localStorage.getItem("darkMode")));

  const handleToggleDarkMode = () => {
    setDarkModeActive(!isDarkModeActive);
    onToggleDarkMode(!isDarkModeActive);
  };

  return (
    <div className="dark-mode-slider">
      <ToggleDarkMode onToggle={handleToggleDarkMode} isDarkModeActive={isDarkModeActive} />
    </div>
  );
};

export default DarkModeSlider;
