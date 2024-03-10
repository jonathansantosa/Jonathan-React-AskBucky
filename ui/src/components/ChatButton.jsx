// ChatButton.jsx
import React from 'react';
import '../styles/ChatButton.css';

const ChatButton = ({ name, key, handleSelectChatWindow, borderColor }) => {
    return (
        <div className = "chat-button" key = { key } onClick = {() => handleSelectChatWindow(key)} style = {{borderColor: borderColor}}>
            <span>{name}</span>
        </div>
    );
};

export default ChatButton;