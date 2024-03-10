// Chatbox.jsx
import React, { useState, useRef, useEffect } from 'react';
import '../styles/Chatbox.css';

const ChatBox = ({ isDarkMode, onChatSubmit, isSidebarOpen }) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef();

  const handleChange = (e) => {
    setMessage(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() !== '') {
      onChatSubmit(message);
      setMessage('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault(); // Prevent new line
      handleSubmit(e);
    }
  };
  useEffect(() => {
    textareaRef.current.style.height = 'auto';
    textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';

    const chatbox = textareaRef.current.parentNode;
    chatbox.style.height = textareaRef.current.scrollHeight + 'px';
  }, [message]);

  return (
    <div className={`chat-box ${isDarkMode ? 'darkmode' : ''} ${isSidebarOpen ? 'shifted' : ''}`}>
      <form onSubmit={handleSubmit}>
        <textarea
          rows="1"
          ref={textareaRef}
          value={message}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder="Send a message..."
          maxlength="4096"
        />
        <div className="submit-button"><i className='bx bx-send' onClick={handleSubmit}></i><span className="tooltip">Send message</span></div>
      </form>
    </div>
  );
};

export default ChatBox;
