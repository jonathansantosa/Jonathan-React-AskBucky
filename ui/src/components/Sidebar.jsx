import React, { useState, useEffect} from 'react';
import '../styles/Sidebar.css';
import DarkModeSlider from './DarkModeButton';
import ThemesButton from './ThemeButton';
import PluginsButton from './PluginsButton';
import Searchbar from './Searchbar';
import ProfileButton from './ProfileButton';
import {changeChatWindow, deleteChatWindow, incrementMessageIndex, resetMessageIndex} from './ChatHistory.jsx';

const Sidebar = ({isOpen, onToggleSidebar, onToggleDarkMode, isDarkModeActive, setSelectedTheme, setThemeData }) => {
// State to manage the list of chat windows
const [chatWindows, setChatWindows] = useState(() => {
  const storedChatWindows = localStorage.getItem('chatWindows');
  return storedChatWindows ? JSON.parse(storedChatWindows) : [];
});
 const [shouldOpen, setShouldOpen] = useState(() => {
  const storedValue = localStorage.getItem('isOpen');
  return storedValue ? JSON.parse(storedValue) : true;
});
useEffect(() => {
  // Update localStorage when isOpen changes
  localStorage.setItem('isOpen', JSON.stringify(shouldOpen));
}, [shouldOpen]);
const onToggleSidebarNow = () => {
  onToggleSidebar();
  setShouldOpen((prevIsOpen) => !prevIsOpen);
};
const [selectedChatWindow, setSelectedChatWindow] = useState(null);
// Function to create a new chat window

useEffect(() => {
  // Check if there are no chat windows, and if so, create one
  if (chatWindows.length === 0) {
    const newChatWindow = {
      id: 0,
      name: 'Default Chat', // Set a default name for the chat window
    };
    localStorage.removeItem('chatHistoryMessages');
    setChatWindows([newChatWindow]);
    resetMessageIndex(); // Reset message index if needed
    incrementMessageIndex(); // Increment message index for the new message
    window.location.reload();
  }
}, []);

const handleResetClick = () => {
  console.log("Settings button clicked");
  setChatWindows([]);
  localStorage.removeItem('chatHistoryMessages');
  localStorage.removeItem('chatOtherHistoryMessages');
   // Also clear the chat windows from localStorage
  localStorage.removeItem('chatWindows');
  window.location.reload();
  resetMessageIndex();
  // Optionally, reset selectedChatWindow to null
  setSelectedChatWindow(null);
  // Here, you can add your logic to open a settings dialog or perform another action
};

 const handleNewChat = () => {
   localStorage.removeItem('chatHistoryMessages');
   incrementMessageIndex();
   const newChatWindow = {
     id: localStorage.getItem('messageIndex'), // Unique ID for the chat window
     name: 'New Chat', // Default name for the chat window
    
   }
   setChatWindows([...chatWindows, newChatWindow]);
   window.location.reload();
 };
 const handleDeleteChatWindow = (chatWindowId) => {
   const updatedChatWindows = chatWindows.filter((window) => window.id !== chatWindowId);
   setChatWindows(updatedChatWindows);
   localStorage.removeItem(`chatHistoryMessages_${chatWindowId}`);
   deleteChatWindow(chatWindowId);
   localStorage.setItem('chatWindows', JSON.stringify(updatedChatWindows));
   console.log("window.id: " + window.id);
   console.log("chatWindowID: " + chatWindowId);
   console.log("updatedChatWindowID: " + updatedChatWindows);
 };
 const handleRenameChatWindow = (chatWindowId) => {
   const newName = prompt("Enter a new name for the chat window:");


   if (newName) {
     const updatedChatWindows = chatWindows.map((window) =>
       window.id === chatWindowId ? { ...window, name: newName } : window
     );


     setChatWindows(updatedChatWindows);
     localStorage.setItem('chatWindows', JSON.stringify(updatedChatWindows));
   }
 };
 const handleSelectChatWindow = (chatWindowId) => {
   // Retrieve messages from localStorage or your state management solution
   // Assuming you have a way to update the messages displayed in ChatHistory
   changeChatWindow(chatWindowId)
 };
  useEffect(() => {
   localStorage.setItem('chatWindows', JSON.stringify(chatWindows));
 }, [chatWindows]);
  return (
    <div className={`sidebar ${shouldOpen ? 'open' : ''} ${isDarkModeActive ? 'dark-mode' : ''}`}>
      <div className="menu-top">
        <button
          className={`toggle-btn ${shouldOpen ? 'inside' : ''}`}
          onClick={onToggleSidebarNow}
        >
          {shouldOpen
            ? <i className='bx bx-menu-alt-right'></i>
            : <i className='bx bx-menu'></i>}
        </button>
        <Searchbar isCollapsed={!shouldOpen}/>
      </div>
      <button className={`new-chat-button ${shouldOpen ? 'inside' : ''}`} onClick={handleNewChat}>
      <i class='bx bx-edit'></i>
        {shouldOpen
          ? <span class="button-text">{"New Chat"}</span>
          : <span className="tooltip">New Chat</span>
        }        
      </button>
      <div className="content" style={{ overflowY: 'auto', overflowX: 'hidden', maxHeight: 'calc(100% - 120px)' }}>
        {/* Render list of chat windows */}
        {shouldOpen && chatWindows.map(chatWindow => (
          
          <div key={chatWindow.id} className="button-group">
 <button
         key={chatWindow.id}
         className={`chat-button ${shouldOpen ? 'inside' : ''}`}
         onClick={() => {
           // Handle button click, e.g., open the chat window
           console.log(`Clicked on chat window with ID: ${chatWindow.id}`);
          
           handleSelectChatWindow(chatWindow.id)
           window.location.reload();
         }}
       >
         <span>{chatWindow.name}</span>
         {/* Other chat window components */}


       </button>
          <button
            className="delete-chat-button"
            onClick={() => handleDeleteChatWindow(chatWindow.id)}
          >
            <span>Delete</span>
          </button>
          <button
            className="rename-chat-button"
            onClick={() => handleRenameChatWindow(chatWindow.id)}
          >
            <span>Rename</span>
            </button>
        </div>
        
        ))}
      </div>
      <div className="bottom-buttons">
        <DarkModeSlider onToggleDarkMode={onToggleDarkMode} isDarkModeActive={isDarkModeActive} />
        <PluginsButton shouldOpen={shouldOpen} onToggleDarkMode={onToggleDarkMode} isDarkModeActive={isDarkModeActive} />
        <ThemesButton shouldOpen={shouldOpen} onToggleDarkMode={onToggleDarkMode} isDarkModeActive={isDarkModeActive} setSelectedTheme={setSelectedTheme} setThemeData={setThemeData}/>
      </div>
      <ProfileButton />
    </div>
  );
};

export default Sidebar;