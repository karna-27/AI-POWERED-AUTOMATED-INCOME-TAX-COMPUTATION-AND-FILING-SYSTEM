import React from 'react';
import { Link, useHistory } from 'react-router-dom'; // Import useHistory for programmatic navigation
import Cookies from 'js-cookie';
import './index.css'; // Import Header specific CSS

// Import icons (example: using Font Awesome via a CDN or local SVG)
// For demonstration, we'll use simple text or inline SVGs.
// In a real app, you might use a library like 'react-icons' or 'lucide-react'.

const Header = ({ onLogout, onNavigate }) => {
  const history = useHistory();
  const isAuthenticated = Cookies.get('jwt_token'); // Check for token to determine auth status

  const handleLogoutClick = () => {
    onLogout(); // Call the logout function passed from App.js
    history.push('/login'); // Redirect to login page after logout
  };

  const handleDashboardNavClick = (content) => {
    // If we are already on the dashboard route, use the onNavigate prop to change content
    // Otherwise, navigate to the dashboard route first, and the dashboard component will handle content
    if (history.location.pathname === '/dashboard') {
      onNavigate(content);
    } else {
      history.push('/dashboard');
      // A small delay or useEffect in Dashboard might be needed if onNavigate is called too quickly
      // before Dashboard fully renders and sets up its state. For now, rely on Dashboard's default.
    }
  };

  return (
    <header className="header-container">
      <div className="header-left">
        <Link to="/" className="header-logo-link">
          <img src="https://static.vecteezy.com/system/resources/thumbnails/002/205/856/small/calculator-icon-free-vector.jpg" className="logo-image"/>
          {/* <img src="/WebsiteLogo.png" alt="GarudaTax AI Logo" className="header-logo" /> */}
          <span className="header-app-name">GarudaTax AI</span>
        </Link>
      </div>
      <nav className="header-nav">
        {isAuthenticated ? (
          // Authenticated Navigation
          <>
            <button onClick={() => handleDashboardNavClick('upload')} className="nav-button">
              Upload Documents
            </button>
            <button onClick={() => handleDashboardNavClick('history')} className="nav-button">
              Tax History
            </button>
            <button onClick={() => handleDashboardNavClick('calculator')} className="nav-button">
              Tax Calculator
            </button>
            <button onClick={() => handleDashboardNavClick('profile')} className="nav-button">
              Profile
            </button>
            <button onClick={handleLogoutClick} className="nav-button logout-button">
              Logout
            </button>
          </>
        ) : (
          // Unauthenticated Navigation
          <>
            <Link to="/login" className="nav-link">Login</Link>
            <Link to="/register" className="nav-link">Register</Link>
            <Link to="/about" className="nav-link">About Us</Link>
            <Link to="/contact" className="nav-link">Contact Us</Link>
          </>
        )}
      </nav>
    </header>
  );
};

export default Header;
