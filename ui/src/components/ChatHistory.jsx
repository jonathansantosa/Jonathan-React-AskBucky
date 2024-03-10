// ChatHistory.jsx
import React, { useEffect, useRef, useCallback, useState } from 'react';
import '../styles/ChatHistory.css';
import userImage from '../images/icon-user.png';
import botImage from '../images/askBuckyProfile.png';
import RenderCodeBlock from './ChatCodeBlock.jsx';

export const resetMessageIndex = () => {
 localStorage.setItem('messageIndex', -1);
 localStorage.setItem('messageCurrentIndex', -1);
}
export const incrementMessageIndex = () => {
 const storedMessageIndex = localStorage.getItem('messageIndex');
 const storedCurrentMessageIndex = localStorage.getItem('messageCurrentIndex');
 const newIndex = storedMessageIndex ? parseInt(storedMessageIndex, 10) + 1 : 1;
 const newCurrentIndex = storedMessageIndex ? parseInt(storedCurrentMessageIndex, 10) + 1 : 1;
 localStorage.setItem('messageIndex', newIndex.toString());
 localStorage.setItem('messageCurrentIndex', newIndex.toString());
};
export const changeChatWindow = (id) => {
 const storedOtherChatHistory = localStorage.getItem('chatOtherHistoryMessages');
 const otherMessages = storedOtherChatHistory ? JSON.parse(storedOtherChatHistory) : [];


 // Log each message.id
 // console.log("Messages to transfer with ID:",  typeof '' + id);
 // otherMessages.forEach(message => {
 //   console.log(typeof message.id);
 // });
 const messagesToTransfer = otherMessages.filter(message => message.id === ''+id);
 localStorage.setItem('chatHistoryMessages', JSON.stringify(messagesToTransfer));
 localStorage.setItem('messageCurrentIndex', id.toString());
 window.location.reload();
};
export const deleteChatWindow = (id) => {
 const storedOtherChatHistory = localStorage.getItem('chatOtherHistoryMessages');
 const otherMessages = storedOtherChatHistory ? JSON.parse(storedOtherChatHistory) : [];


 // Filter out messages not related to the current chat window (id)
 const messagesToKeep = otherMessages.filter(message => message.id !== '' + id);


 // Update localStorage for both other chat history and current chat history
 localStorage.setItem('chatOtherHistoryMessages', JSON.stringify(messagesToKeep));


 const storedChatHistory = localStorage.getItem('chatHistoryMessages');
 const chatMessages = storedOtherChatHistory ? JSON.parse(storedChatHistory) : [];


 // Filter out messages not related to the current chat window (id)
 const currentMessagesToKeep = chatMessages.filter(message => message.id !== '' + id);
 localStorage.setItem('chatHistoryMessages', JSON.stringify(currentMessagesToKeep));
 window.location.reload();
};
const renderMessage = (message, isDarkModeActive) => {
 message = message.replace(/\t/g, '\u00a0\u00a0\u00a0\u00a0');
 const segments = message.split(/(```([a-z]+?)\n[\s\S]*?\n```)/);
 var CodeLanguageSegment = "";


 return segments.map((segment, index) => {
   const isCode = segment.startsWith('```');


   if (isCode) {
     const codeMatch = segment.match(/```([a-z]+?)\n([\s\S]*?)\n```/);


     if (codeMatch) {
       const [, detectedLanguage, code] = codeMatch;
       CodeLanguageSegment = detectedLanguage;
       return <RenderCodeBlock key={index} code={code} detectedLanguage={detectedLanguage} isDarkModeActive={isDarkModeActive} />;
     } else {
       const code = segment.replace(/```[\s\S]*?\n([\s\S]*?)\n```/, '$1');
       const detectedLanguage = "bash";
       return <RenderCodeBlock key={index} code={code} detectedLanguage={detectedLanguage} isDarkModeActive={isDarkModeActive} />;
     }
   } else if (segment === CodeLanguageSegment) {
     return null;
   } else {
     var singleBacktickPattern = /(`[^`]+`[.:, ])/g;
     var matches = segment.match(singleBacktickPattern);


     if (matches) {
       return (
         <p key={index} className="message">
           {segment.split(singleBacktickPattern).map((phrase, i) => {
             if (i % 2 === 0) {
               return phrase;
             } else {
               return (
                 <span key={i} className="message-inline-bold">
                   {phrase
                   }
                 </span>
               );
             }
           })}
         </p>
       );
     } else {
       return (
         <p key={index} className="message">
           {segment.trim()}
         </p>
       );
     }
   }
 });
};


const ChatHistory = ({ messages, isDarkModeActive, isSidebarOpen }) => {
const chatHistoryRef = useRef();
const [copiedMessageIndex, setCopiedMessageIndex] = useState(null);
const [chatHistoryMessages, setChatHistoryMessages] = useState(() => {
   const storedChatHistory = localStorage.getItem('chatHistoryMessages');
   return storedChatHistory ? JSON.parse(storedChatHistory) : [];
});
const [chatOtherHistoryMessages, setChatOtherHistoryMessages] = useState(() => {
   const storedOtherChatHistory = localStorage.getItem('chatOtherHistoryMessages');
   return storedOtherChatHistory ? JSON.parse(storedOtherChatHistory) : [];
});


 // Automatically scroll to the latest message


 useEffect(() => {
   localStorage.setItem('chatHistoryMessages', JSON.stringify(chatHistoryMessages));
   localStorage.setItem('chatOtherHistoryMessages', JSON.stringify(chatOtherHistoryMessages));
 }, [chatHistoryMessages]);
 useEffect(() => {
   const storedMessageIndex = localStorage.getItem('messageIndex');
   if (!storedMessageIndex) {
     localStorage.setItem('messageIndex', '-1');
   }
 }, []);


 useEffect(() => {
   const storedMessageIndex = localStorage.getItem('messageCurrentIndex');
   if (!storedMessageIndex) {
     localStorage.setItem('messageCurrentIndex', '-1');
   }
 }, []);


 // Update cookies whenever messages change
useEffect(() => {
   const messagesWithId = messages.map((message, index) => ({ ...message, id: localStorage.getItem('messageCurrentIndex') }));
   let newMessage = messagesWithId[messagesWithId.length - 1];
   if(newMessage != null){
   setChatHistoryMessages(prevMessages => [...prevMessages, newMessage]);
   setChatOtherHistoryMessages(chatOtherHistoryMessages => [...chatOtherHistoryMessages, newMessage]);
   }
 }, [messages]);


 const getMessageIcon = (messageType) => {
   if (messageType === 'user') {
     return `url(${userImage})`;
   } else if (messageType === 'bot') {
     return `url(${botImage})`;
   }
   return '';
 };


 const copyToClipboard = useCallback((text, index) => {
   navigator.clipboard.writeText(text).then(() => {
     setCopiedMessageIndex(index);
     setTimeout(() => {
       setCopiedMessageIndex(null);
     }, 1500);
   }).catch((err) => {
     console.error('Failed to copy text: ', err);
   });
 }, []);


 return (
   <div className={`chat-history ${isDarkModeActive ? 'dark-mode' : ''}`} ref={chatHistoryRef}>
     {chatHistoryMessages.map((message) => (
       <div key={message.id} className={`message-container ${isDarkModeActive ? 'dark-mode' : ''} ${isSidebarOpen ? 'shifted' : ''}`}>
         <div
           className={`message-icon ${message.type === 'bot' ? 'bot-icon' : ''}`}
           style={{ backgroundImage: getMessageIcon(message.type) }}
         />
         <div className={`message ${message.type}`}>
           {renderMessage(message.text, isDarkModeActive)}
         </div>
         {message.type === 'bot' && (
           <div className={`message-actions ${isDarkModeActive ? 'dark-mode' : ''}`}>
             {copiedMessageIndex === message.id ? (
               <i className='bx bx-check'></i>
             ) : (
               <i className='bx bx-clipboard' onClick={() => copyToClipboard(message.text, message.id)}></i>
             )}
             <i className='bx bx-like'></i>
             <i className='bx bx-dislike'></i>
           </div>
         )}
       </div>
     ))}
   </div>
 ); 
}


export default ChatHistory;
