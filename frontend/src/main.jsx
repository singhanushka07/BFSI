import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#0f2044',
            color: '#fff',
            border: '1px solid rgba(6,182,212,0.3)',
            borderRadius: '12px',
          },
          success: { iconTheme: { primary: '#22c55e', secondary: '#0f2044' } },
          error: { iconTheme: { primary: '#ef4444', secondary: '#0f2044' } },
        }}
      />
    </BrowserRouter>
  </React.StrictMode>
)
