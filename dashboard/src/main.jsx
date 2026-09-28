import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { loadRuntimeConfig } from './api/client.js'

// ADDED: reads /server-config.json (the server's IP/address) before
// the app boots, so every API and WebSocket call already has the
// right host from the very first render. See src/api/client.js for
// what that file controls.
loadRuntimeConfig().finally(() => {
  createRoot(document.getElementById('root')).render(
    <StrictMode>
      <App />
    </StrictMode>,
  )
})