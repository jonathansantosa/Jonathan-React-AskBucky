// Background.js

import React from 'react';
import '../styles/Background.css';

function importAll(r) {
  r.keys().forEach(r);
}

importAll(require.context('../background-gradients/', false, /\.css$/));

const Background = ({ isActive, children, selectedTheme, themeData }) => {
  let themeClass = themeData.title;
  themeClass += isActive ? 'Dark' : 'Light';
  
  return (
    <div className={`background ${themeClass} ${isActive ? 'Dark' : 'Light'}`}>
      <h1 className={`title ${isActive ? 'Dark' : ''}`}>{children}</h1>
    </div>
  );
};

export default Background;

