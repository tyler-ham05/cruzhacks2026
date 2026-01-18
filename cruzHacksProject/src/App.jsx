import { useAuth0 } from "@auth0/auth0-react";
import HomePage from "./homepage";
import './login.css'

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
    login({ authorizationParams: { screen_hint: "signup" } });

  const logout = () =>
    auth0Logout({ logoutParams: { returnTo: window.location.origin } });

  if (isLoading) return "Loading...";

  return isAuthenticated ? (
    <>
        <HomePage/>
    </>
  ) : (
    <>
      {error && <p>Error: {error.message}</p>}
      <div className="fullView">
        <div className="mainCol">
          <img src='src/assets/placeholder.png'/>
          <button className='loginButtons' onClick={signup}>Signup</button>
          <button className='loginButtons' onClick={login}>Login</button>
        </div>
      </div>
    </>
  );
}

export default App;