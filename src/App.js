import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Switch, Route, Redirect } from 'react-router-dom';
import Cookies from 'js-cookie';

// Import your components
import LoginForm from './components/LoginForm';
import RegisterForm from './components/Register'; // Renamed from Register to RegisterForm for clarity
import Dashboard from './components/Dashboard';
import Header from './components/Header'; // Header component is now used conditionally or within specific layouts
import About from './components/About';
import ContactUs from './components/ContactUs';
import Profile from './components/Profile';
// No need to import TaxUploader, TaxCalculator, TaxHistory here, as they are managed by Dashboard

// Main App component
function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loadingAuth, setLoadingAuth] = useState(true);

  // Check authentication status on component mount
  useEffect(() => {
    const token = Cookies.get('jwt_token');
    if (token) {
      setIsAuthenticated(true);
    }
    setLoadingAuth(false); // Authentication check is complete
  }, []);

  // Function to handle successful login
  const handleLogin = (token) => {
    Cookies.set('jwt_token', token, { expires: 1 }); // Token expires in 1 day
    setIsAuthenticated(true);
  };

  // Function to handle logout
  const handleLogout = () => {
    Cookies.remove('jwt_token');
    setIsAuthenticated(false);
    // Optionally redirect to login page after logout
    // history.push('/login'); // If using useHistory hook
  };

  // Show a loading state while checking authentication
  if (loadingAuth) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <div className="text-xl font-semibold text-gray-700">Loading authentication...</div>
      </div>
    );
  }

  // Simple Home component for the root path
  const Home = () => (
    <>
      <Header onLogout={handleLogout} onNavigate={() => {}} /> {/* Pass dummy onNavigate for Home page header */}
      <div className="home-content"> {/* Use a class for styling */}
        <h1>Welcome to GarudaTax AI!</h1>
        <p>Your intelligent assistant for seamless tax filing.</p>
        <div className="home-cta">
          {isAuthenticated ? (
            <p>You are logged in! Go to your <a href="/dashboard" className="home-link">Dashboard</a>.</p>
          ) : (
            <p>Please <a href="/login" className="home-link">login</a> or <a href="/register" className="home-link">register</a> to get started.</p>
          )}
        </div>
      </div>
    </>
  );

  return (
    <Router>
      <div className="App">
        <Switch>
          {/* Public Routes */}
          <Route exact path="/" component={Home} />
          <Route
            path="/login"
            render={(props) => (
              isAuthenticated ? <Redirect to="/dashboard" /> : <LoginForm {...props} onLogin={handleLogin} />
            )}
          />
          <Route
            path="/register"
            render={(props) => (
              isAuthenticated ? <Redirect to="/dashboard" /> : <RegisterForm {...props} />
            )}
          />
          <Route path="/contact" component={ContactUs} />
          <Route path="/about" component={About} />

          {/* Protected Routes */}
          <Route
            path="/dashboard"
            render={(props) => (
              isAuthenticated ? <Dashboard {...props} onLogout={handleLogout} /> : <Redirect to="/login" />
            )}
          />
          <Route
            path="/profile"
            render={(props) => (
              isAuthenticated ? <Profile {...props} /> : <Redirect to="/login" />
            )}
          />

          {/* Catch-all route: Redirects to home if no other route matches */}
          <Redirect to="/" />
        </Switch>
      </div>
    </Router>
  );
}

export default App;
