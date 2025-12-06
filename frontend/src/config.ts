// ============================================
// CENTRALIZED CONFIGURATION
// ============================================

// API Base URL - Change this if backend port changes
export const API_BASE = import.meta.env.DEV 
  ? 'http://localhost:8001'  // Development
  : '';                       // Production (relative URL)

// API Port (for reference)
export const API_PORT = 8001;

// Frontend Port (for reference)
export const FRONTEND_PORT = 5173;

// Session ID (you can make this dynamic later)
export const getSessionId = (): string => {
  let sessionId = localStorage.getItem('virallab_session_id');
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
    localStorage.setItem('virallab_session_id', sessionId);
  }
  return sessionId;
};

