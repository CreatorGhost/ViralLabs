import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import App from './App'
import Dashboard from './Dashboard'
import { LoginPage, SignupPage } from './pages'
import { AuthProvider, ProtectedRoute } from './context'
import './index.css'

// Protected route wrapper component
function ProtectedDashboard() {
  return (
    <ProtectedRoute fallback={<Navigate to="/login" replace />}>
      <Dashboard />
    </ProtectedRoute>
  );
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<App />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/dashboard" element={<ProtectedDashboard />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>,
)
