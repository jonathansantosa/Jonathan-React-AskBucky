import React, { useState } from 'react';
import ThemeManager from './ThemeManager';
import '../styles/ThemeButton.css';

const ThemeButton = ({ isOpen, setSelectedTheme, setThemeData, selectedTheme }) => {
  const [isThemeManagerOpen, setThemeManagerOpen] = useState(false);
  const [isButtonActive, setButtonActive] = useState(false); // New state

  const handleThemeManagerOpen = () => {
    setThemeManagerOpen(true);
    setButtonActive(true);
  };

  const handleThemeManagerClose = () => {
    setThemeManagerOpen(false);
    setButtonActive(false);
  };

  return (
    <>
      <div
        className={`theme-button ${isButtonActive ? 'active' : ''}`} // Add 'active' class when active
        onClick={handleThemeManagerOpen}
      >
        <i className='bx bx-palette'></i>
        <span className="tooltip">Themes</span>
      </div>
      {isThemeManagerOpen && (
        <ThemeManager isOpen={isOpen} onClose={handleThemeManagerClose} setSelectedTheme={setSelectedTheme} setThemeData={setThemeData} theme = {selectedTheme} />
      )}
    </>
  );
};

export default ThemeButton;
