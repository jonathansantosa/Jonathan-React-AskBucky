// InfoBar.js
import React from 'react';
import '../styles/Infobar.css';

const InfoBar = ({ infoItems, isDarkModeActive }) => {
  return (
    <div className={`info-bar ${isDarkModeActive ? 'darkmode' : ''}`}>
      {infoItems.map((item, index) => (
        <div className="info-item" key={index}>
          <div className={`info-background ${isDarkModeActive ? 'darkmode' : ''}`}></div>
          <div className='info-equipped'><i className='bx bxs-circle'></i></div>
          <div className="info-text">{item.text}</div>
          <div className="info-icon"><i className={item.iconClass}></i></div>
          <div><p></p></div>
        </div>
      ))}
    </div>
  );
};

export default InfoBar;
