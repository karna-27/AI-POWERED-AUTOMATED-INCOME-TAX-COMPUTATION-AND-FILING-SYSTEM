import React, { useState } from 'react';
import axios from 'axios';
import { useHistory, Link } from 'react-router-dom'; // Import Link for navigation to Login
import './index.css'; // Import Register specific CSS

const RegisterForm = () => { // Renamed to RegisterForm for consistency with App.js
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [pan, setPan] = useState('');
  const [aadhaar, setAadhaar] = useState('');
  const [address, setAddress] = useState('');
  const [phone, setPhone] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState(''); // 'success', 'error'
  const history = useHistory();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setMessage(''); // Clear previous messages
    setMessageType('');

    if (password !== confirmPassword) {
      setMessage('Passwords do not match.');
      setMessageType('error');
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post('http://127.0.0.1:5000/api/register', {
        username,
        email,
        password,
        fullName,
        pan,
        aadhaar,
        address,
        phone,
      });

      if (response.status === 201) {
        setMessage('Registration successful! Redirecting to login...');
        setMessageType('success');
        setTimeout(() => {
          history.push('/login'); // Redirect to login page
        }, 2000);
      } else {
        setMessage(response.data.message || 'Registration failed. Please try again.');
        setMessageType('error');
      }
    } catch (error) {
      console.error('Registration error:', error);
      if (error.response) {
        setMessage(error.response.data.message || 'An error occurred during registration.');
      } else {
        setMessage('Network error. Please check your connection.');
      }
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-container">
      <div className="register-box">
        <h2 className="register-title">Register for GarudaTax AI</h2>
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
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
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
          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <input
              type="password"
              id="confirmPassword"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              className="form-input"
              disabled={loading}
            />
          </div>
          <div className="form-group">
            <label htmlFor="fullName">Full Name</label>
            <input
              type="text"
              id="fullName"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="form-input"
              disabled={loading}
            />
          </div>
          <div className="form-group">
            <label htmlFor="pan">PAN</label>
            <input
              type="text"
              id="pan"
              value={pan}
              onChange={(e) => setPan(e.target.value.toUpperCase())} // Convert to uppercase
              className="form-input"
              pattern="[A-Z]{5}[0-9]{4}[A-Z]{1}" // Basic PAN validation pattern
              title="PAN should be 5 uppercase letters, 4 digits, and 1 uppercase letter (e.g., ABCDE1234F)"
              disabled={loading}
            />
          </div>
          <div className="form-group">
            <label htmlFor="aadhaar">Aadhaar (Optional)</label>
            <input
              type="text"
              id="aadhaar"
              value={aadhaar}
              onChange={(e) => setAadhaar(e.target.value)}
              className="form-input"
              pattern="[0-9]{12}" // Basic Aadhaar validation pattern
              title="Aadhaar should be 12 digits"
              disabled={loading}
            />
          </div>
          <div className="form-group">
            <label htmlFor="address">Address (Optional)</label>
            <textarea
              id="address"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              className="form-input"
              rows="3"
              disabled={loading}
            ></textarea>
          </div>
          <div className="form-group">
            <label htmlFor="phone">Phone Number (Optional)</label>
            <input
              type="tel"
              id="phone"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="form-input"
              pattern="[0-9]{10}" // Basic 10-digit phone number
              title="Phone number should be 10 digits"
              disabled={loading}
            />
          </div>

          <button type="submit" className="register-button" disabled={loading}>
            {loading ? 'Registering...' : 'Register'}
          </button>
        </form>
        {message && (
          <div className={`message ${messageType}`}>
            {message}
          </div>
        )}
        <p className="login-link-text">
          Already have an account? <Link to="/login" className="login-link">Login here</Link>
        </p>
      </div>
    </div>
  );
};

export default RegisterForm;
