// Home.js
import React, { useEffect, useState } from 'react';
import Background from './components/Background';
import ChatBox from './components/Chatbox';
import ChatHistory from './components/ChatHistory';
import Sidebar from './components/Sidebar';
import Infobar from './components/Infobar';
import './Home.css';
import axios from 'axios';
import { io } from 'socket.io-client';
import themesJson from "./background-gradients/themes.json";
 
const Home = () => {
  if (!localStorage.getItem("theme")) {
    localStorage.setItem("theme",JSON.stringify(themesJson[Object.keys(themesJson)[0]]));
  }
  if (!localStorage.getItem("themeData")) {
    let t = themesJson[Object.keys(themesJson)[0]];
    if (localStorage.getItem("theme")) t = JSON.parse(localStorage.getItem("theme"));
    let theme = {
      title: t.title,
      description: t.description,
      cssPath: `../background-gradients/${t.title}.css`,
      main: t.main,
      accent: t.accent    
    };
    localStorage.setItem("themeData", JSON.stringify(theme));
  }
  if (!localStorage.getItem("theme")) {
    localStorage.setItem("theme",JSON.stringify(themesJson[Object.keys(themesJson)[0]]));
  }
  if (!localStorage.getItem("themeData")) {
    let t = themesJson[Object.keys(themesJson)[0]];
    if (localStorage.getItem("theme")) t = JSON.parse(localStorage.getItem("theme"));
    let theme = {
      title: t.title,
      description: t.description,
      cssPath: `../background-gradients/${t.title}.css`,
      main: t.main,
      accent: t.accent    
    };
    localStorage.setItem("themeData", JSON.stringify(theme));
  }
  const [isSidebarOpen, setSidebarOpen] = useState(() => {
    const storedValue = localStorage.getItem('isOpen');
    return storedValue ? JSON.parse(storedValue) : false;
  });
  const [isDarkModeActive, setDarkModeActive] = useState(JSON.parse(localStorage.getItem("darkMode")));
  const [chatMessages, setChatMessages] = useState([]);
  const [selectedTheme, setSelectedTheme] = useState(JSON.parse(localStorage.getItem("theme")));
  const [themeData, setThemeData] = useState(JSON.parse(localStorage.getItem("themeData")));
  
  var schoolName = "Santa Clara University";
  var OpenAI_Model = "GPT-3.5-turbo";
  var occupation = "Student";
  const infoItems = [
    { iconClass: 'bx bxs-graduation', text: schoolName },
    { iconClass: 'bx bxs-bolt', text: OpenAI_Model },
    { iconClass: 'bx bxs-user', text: occupation },
  ];
  
  const handleToggleSidebar = () => {
    const newSidebarValue = !isSidebarOpen;
    setSidebarOpen(newSidebarValue);
    localStorage.setItem('isOpen', JSON.stringify(newSidebarValue));
  };
  const handleToggleDarkMode = () => {
    setDarkModeActive(!isDarkModeActive);
  };
  
  useEffect(() => {
    const savedMessages = localStorage.getItem('chatMessages');
    if (savedMessages) {
      setChatMessages(JSON.parse(savedMessages));
    }
  }, []);

  useEffect(() => {
    const socket = io('http://localhost:5000');
    let full_message = "";
  
    socket.on('message', (message) => {
      if (message.type === 'bot') {
        full_message += message.text;
        setChatMessages((prevMessages) => {
          const newMessages = [...prevMessages];
          const lastMessage = newMessages[newMessages.length - 1];
          if (lastMessage && lastMessage.type === 'bot') {
            lastMessage.text = full_message;
          } else {
            newMessages.push({ text: full_message, type: 'bot' });
          }
          return newMessages;
        });
      } else if (message.type === 'user') {
        full_message = "";
      }
    });
  
    return () => {
      socket.disconnect();
    };
  }, []);
  useEffect(() => {
    localStorage.setItem('chatMessages', JSON.stringify(chatMessages));
  }, [chatMessages]);
  const handleChatStreamSubmit = async (message) => {
    setChatMessages((prevMessages) => [...prevMessages, { text: message, type: 'user' }]);
    try {
      await axios.post('http://localhost:5000/main', { message: message });
    } catch (error) {
      console.error("Error sending message:", error);
    }
  };
  let main = "#990001";
  let accent = "#ffffff";
  if (themeData) {
    main = themeData.main;
    accent = themeData.accent;
  }
  
  return (
    <div className={`app ${isDarkModeActive ? 'dark-mode' : ''}`}>
      <Background isActive={isDarkModeActive} selectedTheme={selectedTheme} themeData={themeData}>
        <div className={`content-container ${isSidebarOpen ? 'content-shifted' : ''}`}>
          <Infobar infoItems={infoItems} isDarkModeActive={isDarkModeActive} />
          <Sidebar
            isOpen={isSidebarOpen}
            onToggleSidebar={handleToggleSidebar}
            onToggleDarkMode={handleToggleDarkMode}
            isDarkModeActive={isDarkModeActive}
            setSelectedTheme={setSelectedTheme}
            setThemeData={setThemeData}
            selectedTheme = {selectedTheme}
            mainColor = {main}
            accentColor = {accent}
          />
          <ChatHistory messages={chatMessages} isDarkModeActive={isDarkModeActive} isSidebarOpen={isSidebarOpen}/>
          <ChatBox isDarkMode={isDarkModeActive} onChatSubmit={handleChatStreamSubmit} isSidebarOpen={isSidebarOpen} />
        </div>
      </Background>
    </div>
  );
};
export default Home;
