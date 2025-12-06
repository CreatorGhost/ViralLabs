import { API_BASE } from '../config';
import type {
  AuthResponse,
  LoginRequest,
  SignupRequest,
  RefreshTokenRequest,
  User,
  ActiveSessionsResponse,
  LogoutResponse,
  LogoutAllResponse,
  AUTH_STORAGE_KEYS,
} from '../types/auth';

// ============================================
// TOKEN MANAGEMENT
// ============================================

export const getStoredTokens = () => {
  const accessToken = localStorage.getItem('virallab_access_token');
  const refreshToken = localStorage.getItem('virallab_refresh_token');
  return { accessToken, refreshToken };
};

export const storeTokens = (accessToken: string, refreshToken: string) => {
  localStorage.setItem('virallab_access_token', accessToken);
  localStorage.setItem('virallab_refresh_token', refreshToken);
};

export const clearTokens = () => {
  localStorage.removeItem('virallab_access_token');
  localStorage.removeItem('virallab_refresh_token');
  localStorage.removeItem('virallab_user');
};

export const getStoredUser = (): User | null => {
  const userJson = localStorage.getItem('virallab_user');
  if (!userJson) return null;
  try {
    return JSON.parse(userJson);
  } catch {
    return null;
  }
};

export const storeUser = (user: User) => {
  localStorage.setItem('virallab_user', JSON.stringify(user));
};

// ============================================
// AUTH HEADERS
// ============================================

export const getAuthHeaders = (): Record<string, string> => {
  const { accessToken } = getStoredTokens();
  if (!accessToken) return {};
  return {
    Authorization: `Bearer ${accessToken}`,
  };
};

// ============================================
// AUTH API CALLS
// ============================================

export const signup = async (request: SignupRequest): Promise<AuthResponse> => {
  const response = await fetch(`${API_BASE}/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  
  const data = await response.json();
  
  // Store tokens and user on success
  if (data.success && data.tokens && data.user) {
    storeTokens(data.tokens.access_token, data.tokens.refresh_token);
    storeUser(data.user);
  }
  
  return data;
};

export const login = async (request: LoginRequest): Promise<AuthResponse> => {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  
  const data = await response.json();
  
  // Store tokens and user on success
  if (data.success && data.tokens && data.user) {
    storeTokens(data.tokens.access_token, data.tokens.refresh_token);
    storeUser(data.user);
  }
  
  return data;
};

export const refreshAccessToken = async (): Promise<AuthResponse> => {
  const { refreshToken } = getStoredTokens();
  
  if (!refreshToken) {
    return { success: false, error: 'No refresh token available' };
  }
  
  try {
    const response = await fetch(`${API_BASE}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    
    const data = await response.json();
    
    // Store new tokens on success
    if (data.success && data.tokens) {
      storeTokens(data.tokens.access_token, data.tokens.refresh_token);
    } else {
      // Refresh failed - clear all tokens
      clearTokens();
    }
    
    return data;
  } catch (error) {
    clearTokens();
    return { success: false, error: 'Token refresh failed' };
  }
};

export const logout = async (): Promise<LogoutResponse> => {
  const { refreshToken } = getStoredTokens();
  
  if (!refreshToken) {
    clearTokens();
    return { success: true, message: 'Already logged out' };
  }
  
  try {
    const response = await fetch(`${API_BASE}/auth/logout`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    
    const data = await response.json();
    clearTokens();
    return data;
  } catch {
    clearTokens();
    return { success: true, message: 'Logged out locally' };
  }
};

export const logoutAll = async (): Promise<LogoutAllResponse> => {
  const response = await fetch(`${API_BASE}/auth/logout-all`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
  });
  
  const data = await response.json();
  
  if (data.success) {
    clearTokens();
  }
  
  return data;
};

export const getCurrentUser = async (): Promise<User | null> => {
  const { accessToken } = getStoredTokens();
  
  if (!accessToken) {
    return null;
  }
  
  try {
    const response = await fetch(`${API_BASE}/auth/me`, {
      headers: {
        ...getAuthHeaders(),
      },
    });
    
    if (!response.ok) {
      // Token might be expired, try refresh
      if (response.status === 401) {
        const refreshResult = await refreshAccessToken();
        if (refreshResult.success) {
          // Retry with new token
          const retryResponse = await fetch(`${API_BASE}/auth/me`, {
            headers: {
              ...getAuthHeaders(),
            },
          });
          if (retryResponse.ok) {
            const user = await retryResponse.json();
            storeUser(user);
            return user;
          }
        }
      }
      return null;
    }
    
    const user = await response.json();
    storeUser(user);
    return user;
  } catch {
    return null;
  }
};

export const getActiveSessions = async (): Promise<ActiveSessionsResponse | null> => {
  try {
    const response = await fetch(`${API_BASE}/auth/sessions`, {
      headers: {
        ...getAuthHeaders(),
      },
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        const refreshResult = await refreshAccessToken();
        if (refreshResult.success) {
          const retryResponse = await fetch(`${API_BASE}/auth/sessions`, {
            headers: {
              ...getAuthHeaders(),
            },
          });
          if (retryResponse.ok) {
            return retryResponse.json();
          }
        }
      }
      return null;
    }
    
    return response.json();
  } catch {
    return null;
  }
};

export const revokeSession = async (sessionId: string): Promise<{ success: boolean; message?: string }> => {
  try {
    const response = await fetch(`${API_BASE}/auth/sessions/${sessionId}`, {
      method: 'DELETE',
      headers: {
        ...getAuthHeaders(),
      },
    });
    
    if (!response.ok) {
      const error = await response.json();
      return { success: false, message: error.detail || 'Failed to revoke session' };
    }
    
    return { success: true, message: 'Session revoked' };
  } catch {
    return { success: false, message: 'Network error' };
  }
};

// ============================================
// AUTHENTICATED FETCH WRAPPER
// ============================================

/**
 * Wrapper for fetch that automatically handles auth headers and token refresh
 */
export const authFetch = async (
  url: string,
  options: RequestInit = {}
): Promise<Response> => {
  const headers = {
    ...options.headers,
    ...getAuthHeaders(),
  };
  
  let response = await fetch(url, { ...options, headers });
  
  // If unauthorized, try to refresh token and retry
  if (response.status === 401) {
    const refreshResult = await refreshAccessToken();
    if (refreshResult.success) {
      // Retry with new token
      const newHeaders = {
        ...options.headers,
        ...getAuthHeaders(),
      };
      response = await fetch(url, { ...options, headers: newHeaders });
    }
  }
  
  return response;
};

