// ChatCodeBlock.jsx
import React, { useState } from 'react';
import '../styles/ChatCodeBlock.css';
import Editor from '@monaco-editor/react';

const RenderCodeBlock = ({ code, detectedLanguage = 'plaintext', isDarkModeActive }) => {
  
  const [isCodeCopied, setIsCodeCopied] = useState(false);
  const numberOfLines = code.split('\n').length;
  const fontSize = 12;
  const editorHeight = `${1.5 * numberOfLines * fontSize}px`;

  const copyCodeToClipboard = () => {
    navigator.clipboard.writeText(code)
      .then(() => {
        setIsCodeCopied(true);
        
        setTimeout(() => {
          setIsCodeCopied(false);
        }, 1500);
      })
      .catch(err => {
        console.error('Failed to copy code to clipboard', err);
      });
  };
  
  const options = {
    selectOnLineNumbers: false,
    readOnly: true,
    automaticLayout: true,
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    fontFamily: "'Monospace'",
    fontSize: fontSize,
    roundedSelection: true,
  };

  return (
    <div className="code-block-container">
      <div className="code-block-bar">
        <span className="code-block-title">{detectedLanguage}</span>
        <i className={isCodeCopied? 'bx bx-check' : 'bx bx-clipboard copy-button'} onClick={() => copyCodeToClipboard()} ></i>
      </div>
      <Editor
        defaultLanguage={detectedLanguage}
        theme={isDarkModeActive? "vs-dark" : "vs-light"}
        value={code}
        options={options}
        height={editorHeight}
      />
    </div>
  );
};

export default RenderCodeBlock;