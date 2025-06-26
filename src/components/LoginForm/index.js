import React, { useState } from 'react';
import axios from 'axios';
import { useHistory, Link } from 'react-router-dom'; // Import Link for navigation to Register
import './index.css'; // Import LoginForm specific CSS

const LoginForm = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(''); // For success/error messages
  const [messageType, setMessageType] = useState(''); // 'success', 'error'
  const history = useHistory();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setMessage(''); // Clear previous messages
    setMessageType('');
    setLoading(true);

    try {
      const response = await axios.post('http://127.0.0.1:5000/api/login', {
        username,
        password,
      });

      if (response.data.jwt_token) {
        onLogin(response.data.jwt_token); // Call the onLogin function passed from App.js
        setMessage('Login successful! Redirecting to dashboard...');
        setMessageType('success');
        setTimeout(() => {
          history.push('/dashboard'); // Redirect to dashboard
        }, 1500);
      } else {
        setMessage(response.data.message || 'Login failed. Please try again.');
        setMessageType('error');
      }
    } catch (error) {
      console.error('Login error:', error);
      if (error.response) {
        setMessage(error.response.data.error_msg || 'Invalid credentials or server error.');
      } else {
        setMessage('Network error. Please check your connection.');
      }
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h2 className="login-title">Login to GarudaTax AI</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="form-input"
              disabled={loading}
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="form-input"
              disabled={loading}
            />
          </div>
          <button type="submit" className="login-button" disabled={loading}>
            {loading ? 'Logging In...' : 'Login'}
          </button>
        </form>
        {message && (
          <div className={`message ${messageType}`}>
            {message}
          </div>
        )}
        <p className="register-link-text">
          Don't have an account? <Link to="/register" className="register-link">Register here</Link>
        </p>
      </div>
    </div>
  );
};

export default LoginForm;
