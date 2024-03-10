// NewChatButton.jsx
import React from 'react';
import '../styles/NewChatButton.css';

const NewChatButton = ({ isOpen, handleNewChat, borderColor }) => {
    return (
        <div className = "new-chat-button" onClick = {handleNewChat} style = {{borderColor: borderColor}}>
            <span>{isOpen ? "New Chat" : "+"}</span>
        </div>
    )
};

export default NewChatButton;