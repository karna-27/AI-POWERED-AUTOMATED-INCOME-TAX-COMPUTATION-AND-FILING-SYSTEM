import React from 'react';
// Correct import for react-router-dom v5
import { Route, Redirect } from 'react-router-dom';

const ProtectedRoute = ({ component: Component, ...rest }) => {
  // Your authentication logic (e.g., checking localStorage for a token)
  const isAuthenticated = localStorage.getItem('token') ? true : false;

  return (
    <Route
      {...rest}
      render={(props) =>
        isAuthenticated ? (
          <Component {...props} />
        ) : (
          // Use Redirect instead of Navigate
          <Redirect to="/login" />
        )
      }
    />
  );
};

export default ProtectedRoute;