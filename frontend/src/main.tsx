import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import App from './App'
import Dashboard from './Dashboard'
import { 
  LoginPage, 
  SignupPage,
  TermsPage,
  PrivacyPage,
  RefundPage,
  ContactPage,
  PricingPage,
  AboutPage,
} from './pages'
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
          {/* Public routes */}
          <Route path="/" element={<App />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          
          {/* Legal & Info pages (required for payment provider) */}
          <Route path="/terms" element={<TermsPage />} />
          <Route path="/privacy" element={<PrivacyPage />} />
          <Route path="/refund" element={<RefundPage />} />
          <Route path="/contact" element={<ContactPage />} />
          <Route path="/pricing" element={<PricingPage />} />
          <Route path="/about" element={<AboutPage />} />
          
          {/* Protected routes */}
          <Route path="/dashboard" element={<ProtectedDashboard />} />
          
          {/* Catch all - redirect to home */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>,
)
