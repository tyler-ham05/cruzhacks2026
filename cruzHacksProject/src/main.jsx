import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'
import { Auth0Provider } from '@auth0/auth0-react'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Auth0Provider
      domain="dev-2hydh4svq703m2os.us.auth0.com"
      clientId="vQrdCOeyKaEEpEvhgNkORvGqs6qzmJzc"
      authorizationParams={{ redirect_uri: window.location.origin }}
    >
    <App />
    </Auth0Provider>
    
  </React.StrictMode>,
)
