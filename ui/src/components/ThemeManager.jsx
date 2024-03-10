import React, { useEffect, useState } from 'react';
import '../styles/ThemeManager.css';
import themesJson from '../background-gradients/themes.json';
const themeData = {};
Object.keys(themesJson).forEach((themeId) => {
  const theme = themesJson[themeId];
  const cssPath = `../background-gradients/${theme.title}.css`;
  themeData[themeId] = {
    title: theme.title,
    description: theme.description,
    cssPath: cssPath,
    main: theme.main,
    accent: theme.accent,
    cssPath: cssPath,
    main: theme.main,
    accent: theme.accent
  };
});
const ThemeManager = ({ isOpen, onClose, setSelectedTheme, setThemeData, theme }) => {
  const [selectedTheme, setSelectedThemeState] = useState(null);
  useEffect(() => {
    const closeButton = document.querySelector('.close');
    const handleMouseMove = (event) => {
      const mouseX = event.clientX;
      const mouseY = event.clientY;
      const buttonRect = closeButton.getBoundingClientRect();
      const buttonCenterX = buttonRect.left + buttonRect.width / 2;
      const buttonCenterY = buttonRect.top + buttonRect.height / 2;
      const distance = Math.sqrt((mouseX - buttonCenterX) ** 2 + (mouseY - buttonCenterY) ** 2);
      if (distance <= 50) {
        closeButton.classList.add('hovered');
      } else {
        closeButton.classList.remove('hovered');
      }
    };
    document.addEventListener('mousemove', handleMouseMove);
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
    };
  }, [onClose]);
  const handleCheckboxChange = (themeId) => {
    setSelectedThemeState((prevSelectedTheme) => {
      const newSelectedTheme = prevSelectedTheme === themeId ? null : themeId;
      localStorage.setItem("theme",JSON.stringify(newSelectedTheme));
      localStorage.setItem("themeData", JSON.stringify(themeData[newSelectedTheme]));
      localStorage.setItem("theme",JSON.stringify(newSelectedTheme));
      localStorage.setItem("themeData", JSON.stringify(themeData[newSelectedTheme]));
      return newSelectedTheme;
    });
  };
  
  useEffect(() => {
    if (selectedTheme !== null) {
      setSelectedTheme(selectedTheme);
      setThemeData(themeData[selectedTheme]);
    }
  }, [selectedTheme, setSelectedTheme, setThemeData]);
  
  const renderThemes = () => {
    if (selectedTheme) theme = selectedTheme;
    if (selectedTheme) theme = selectedTheme;
    return Object.keys(themeData).map((themeId) => {
      const { title, description } = themeData[themeId];
      return (
        <div
        className="image-row"
        key={themeId}
        onClick={() => handleCheckboxChange(themeId)}
        style={{ cursor: 'pointer' }}
      >
          <div className="checkbox-container">
            <div className="round">
              <input
                type="checkbox"
                id={`checkbox${themeId}`}
                onChange={() => handleCheckboxChange(themeId)}
                checked={theme == themeId}
              />
              <div className = "box"></div>
              <div className = "box"></div>
            </div>
          </div>
          <div className="left-container">
            <h2>{title}</h2>
            <p>{description}</p>
          </div>
          <div className="right-container">
            <div className={`theme-image ${themeData[themeId].title}Light`} />
            <div className={`theme-image ${themeData[themeId].title}Dark`} />
          </div>
        </div>
      );
    });
  };
  if (!localStorage.getItem("themeData")) localStorage.setItem("themeData", JSON.stringify(themeData));
  return (
    <div className="theme-manager-container">
      <div className="theme-manager" style={{ '--theme-manager-left': isOpen ? '8.5%' : '0' }}>
        <div className="top-bar">
          <div className="close" onClick={onClose}></div>
        </div>
        <h1>Theme Manager</h1>
        <div className="image-container">{renderThemes()}</div>
        <p>Selected choice is automatically saved</p>
      </div>
    </div>
  );
};
export default ThemeManager;