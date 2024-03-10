// PluginsButton.js
import React from 'react';
import '../styles/PluginsButton.css';

const PluginsButton = () => { 
  return (
    <div className="plugin-button">
        <i className='bx bx-extension'></i>
        <span className="tooltip">Plugins</span>
    </div>
  );
};

export default PluginsButton;