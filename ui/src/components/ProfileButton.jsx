// ProfileButton.js
import React from 'react';
import '../styles/ProfileButton.css';
import userIcon from '../images/icon-user.png'

const ProfileButton = () => {
  return (
    <div className="profile-button">
        <img src={userIcon} alt="HUH" />
        <span>Cluster</span>
    </div>
  );
};

export default ProfileButton;
