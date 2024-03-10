import React, { useState } from 'react';
import Home from './Home';

const App = () => {
  const [selectedTheme, setSelectedTheme] = useState(null);
  const [themeData, setThemeData] = useState(null);

  return (
    <Home
      selectedTheme={selectedTheme}
      setSelectedTheme={setSelectedTheme}
      themeData={themeData}
      setThemeData={setThemeData}
    />
  );
};

export default App;
