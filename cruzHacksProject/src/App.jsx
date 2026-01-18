import { useAuth0 } from '@auth0/auth0-react';
import { Routes, Route } from 'react-router-dom';
import HomePage from './homepage';
import './login.css';
import IncidentDetails from './IncidentDetails';
import placeholder from './assets/placeholder.png';

function App() {
  const {
    isLoading, // Loading state, the SDK needs to reach Auth0 on load
    isAuthenticated,
    error,
    loginWithRedirect: login, // Starts the login flow
    logout: auth0Logout, // Starts the logout flow
    user, // User profile
  } = useAuth0();

  const signup = () =>
    login({ authorizationParams: { screen_hint: 'signup' } });

  const logout = () =>
    auth0Logout({ logoutParams: { returnTo: window.location.origin } });

  if (isLoading) return 'Loading...';

  if (!isAuthenticated) {
    return (
      <>
        {error && <p>Error: {error.message}</p>}
        <div className="fullView">
          <div className="mainCol">
            <img src={placeholder} />
            <button
              className="loginButtons"
              onClick={() =>
                login({ authorizationParams: { screen_hint: 'signup' } })
              }
            >
              Signup
            </button>
            <button className="loginButtons" onClick={login}>
              Login
            </button>
          </div>
        </div>
      </>
    );
  }

  return (
    <Routes>
      <Route path="/" element={<HomePage userId = {user.sub} logout={logout} />} />
      <Route path="/incident" element={<IncidentDetails />} />
    </Routes>
  );
}

export default App;
