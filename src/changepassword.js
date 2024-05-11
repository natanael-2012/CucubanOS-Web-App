import React, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import 'material-design-lite/material';
import 'material-design-lite/material.css';
import './styles.css';
import linkexpired from './images/linkexpired.png'; 

const ChangePassword = () => {
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordsMatch, setPasswordsMatch] = useState(true); // Flag to track if passwords match
  const [isNewPasswordVisible, setIsNewPasswordVisible] = useState(false);
  const [isConfirmPasswordVisible, setIsConfirmPasswordVisible] = useState(false);
  const [showNotification, setShowNotification] = useState(false);
  const [error, setError] = useState('');
  const [redirect, setRedirect] = useState(false);
  const [notificationTimeout, setNotificationTimeout] = useState(null);
  const [tokenValid, setTokenValid] = useState(false);


  useEffect(() => {
    validateToken();
  }, []);

  const validateToken = () => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');
    const email = localStorage.getItem('forgotPasswordEmail');

    console.log('Email:', email);

    // Send a request to check if the token is valid
    fetch(`https://boyaslacatalana.azurewebsites.net/check-forgotten-password-token?token=${token}&email=${email}`)
      .then(response => response.json())
      .then(data => {
        if (data.message === 'Token is valid') {
          setTokenValid(true);
          console.log('Email:', email);
        } else {
          // Redirect to an error page or display an error message
          console.error('Invalid token:', data.error);
        }
      })
      .catch(error => {
        console.error('Error checking token:', error);
      });
  };




  const handleSubmitConfirmPassword = async (event) => {
    event.preventDefault();

    const email = localStorage.getItem('forgotPasswordEmail');
  
    // Check if the new password meets the criteria
    const passwordRegex = /^(?=.*[0-9]).{8,12}$/;
    if (!passwordRegex.test(newPassword)) {
      // Display an error message to the user
      setError('New password must be at least 8 characters long and contain at least one number.');
      return;
    } else {
      setError(''); // Reset error message
    }
  
    // Check if new password and confirm password match
    if (newPassword !== confirmPassword) {
      // Display an error message to the user
      setError('Passwords do not match.');
      return;
    } else {
      setPasswordsMatch(true); // Reset passwords match flag
    }
  
    try {
      // Send a request to the backend to update the password
      const response = await fetch('https://boyaslacatalana-api.azurewebsites.net/update-password', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email,
          newPassword: newPassword,
        }),
      });
  
      if (response.ok) {
        // Password updated successfully
        console.log('Password updated successfully');
        setShowNotification(true);
        
        // Set a timeout to redirect to the login page after showing the notification
      const timeout = setTimeout(() => {
        setRedirect(true);
      }, 3000);

      // Clear the timeout when the component unmounts or when the notification is hidden
      return () => clearTimeout(timeout);
      } else {
        // Failed to update password
        console.log('Failed to update password');

        if (response.status === 400) {
          // Password cannot be the same as the current password
          setError('New password cannot be the same as the current password.');
        }
      }
    } catch (error) {
      console.error('Error updating password:', error);
    }
  };

  useEffect(() => {
    if (showNotification) {
      // Set a timeout to hide the notification after 3 seconds
      const timeout = setTimeout(() => {
        setShowNotification(false);
      }, 3000);

      // Store the timeout ID
      setNotificationTimeout(timeout);
    }
  }, [showNotification]);

  if (redirect) {
    // Clear the notification timeout before redirecting
    clearTimeout(notificationTimeout);
    return <Navigate to="/" />;
  }

  if (!tokenValid) {
    // Redirect the user to an error page or display an error message
    return <Navigate to="/" />;
  }

  return (
    <div className="center-container-login">
      {/* <div className="image-container">
      <img src={linkexpired} alt="Expired Link" />
        </div> */}
      <div className="demo-card-square mdl-card-change mdl-shadow--2dp">
        <div className="mdl-card__title mdl-card--expand">
          <h2 className="mdl-card__title-text">Change Password</h2>
        </div>
        <div className="mdl-card__supporting-text">
          <p>
            Please enter a new password for your account and confirm it below. This action cannot be undone.
          </p>
          <form onSubmit={handleSubmitConfirmPassword}>
            <div className={`mdl-textfield mdl-js-textfield mdl-textfield--floating-label ${error ? 'is-invalid' : ''}`}>
              <input
                className="mdl-textfield__input"
                type={isNewPasswordVisible ? "text" : "password"}
                id="newPassword"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
              />
              <label className="mdl-textfield__label" htmlFor="newPassword">New Password:</label>
              <button type="button" className="mdl-button mdl-js-button mdl-button--icon password-visibility-button" onClick={() => setIsNewPasswordVisible(!isNewPasswordVisible)}>
                <i className="material-icons">{isNewPasswordVisible ? 'visibility_off' : 'visibility'}</i>
              </button>
            </div>
            <div className={`mdl-textfield mdl-js-textfield mdl-textfield--floating-label ${error ? 'is-invalid' : ''}`}>
              <input
                className="mdl-textfield__input"
                type={isConfirmPasswordVisible ? "text" : "password"}
                id="confirmPassword"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
              <label className="mdl-textfield__label" htmlFor="confirmPassword">Confirm Password:</label>
              <button type="button" className="mdl-button mdl-js-button mdl-button--icon password-visibility-button" onClick={() => setIsConfirmPasswordVisible(!isConfirmPasswordVisible)}>
                <i className="material-icons">{isConfirmPasswordVisible ? 'visibility_off' : 'visibility'}</i>
              </button>
            </div>
            {error && <span className="error-message">{error}</span>}
            <div className="changepassword-button">
              <button className="mdl-button-login mdl-button mdl-js-button mdl-js-ripple-effect" type="submit">
                Submit
              </button>
            </div>
          </form>
        </div>
      </div>
      {/* Notification */}
      {showNotification && (
        <div className="notification-container">
          <div className="notification-card">
            <div className="notification-text">Password updated successfully!</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChangePassword;
