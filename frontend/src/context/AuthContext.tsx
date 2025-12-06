import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import type { User, AuthContextType, AuthResponse } from '../types/auth';
import {
  login as apiLogin,
  signup as apiSignup,
  logout as apiLogout,
  getCurrentUser,
  getStoredTokens,
  getStoredUser,
  clearTokens,
  refreshAccessToken,
} from '../api/auth';

// ============================================
// CONTEXT
// ============================================

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// ============================================
// PROVIDER
// ============================================

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Derived state
  const isAuthenticated = !!user && !!accessToken;

  // Initialize auth state from storage
  useEffect(() => {
    const initAuth = async () => {
      setIsLoading(true);
      
      try {
        const tokens = getStoredTokens();
        const storedUser = getStoredUser();
        
        if (tokens.accessToken && tokens.refreshToken) {
          setAccessToken(tokens.accessToken);
          setRefreshToken(tokens.refreshToken);
          
          // Verify token is still valid by fetching current user
          const currentUser = await getCurrentUser();
          
          if (currentUser) {
            setUser(currentUser);
          } else {
            // Token invalid, clear everything
            clearTokens();
            setAccessToken(null);
            setRefreshToken(null);
            setUser(null);
          }
        } else if (storedUser) {
          // Legacy: user stored but no tokens - clear it
          clearTokens();
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        clearTokens();
        setUser(null);
        setAccessToken(null);
        setRefreshToken(null);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  // Login handler
  const login = useCallback(async (email: string, password: string): Promise<AuthResponse> => {
    setIsLoading(true);
    
    try {
      const response = await apiLogin({ email, password });
      
      if (response.success && response.user && response.tokens) {
        setUser(response.user);
        setAccessToken(response.tokens.access_token);
        setRefreshToken(response.tokens.refresh_token);
      }
      
      return response;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Signup handler
  const signup = useCallback(async (
    email: string,
    password: string,
    fullName: string
  ): Promise<AuthResponse> => {
    setIsLoading(true);
    
    try {
      const response = await apiSignup({ email, password, full_name: fullName });
      
      if (response.success && response.user && response.tokens) {
        setUser(response.user);
        setAccessToken(response.tokens.access_token);
        setRefreshToken(response.tokens.refresh_token);
      }
      
      return response;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Logout handler
  const logout = useCallback(async (): Promise<void> => {
    setIsLoading(true);
    
    try {
      await apiLogout();
    } finally {
      setUser(null);
      setAccessToken(null);
      setRefreshToken(null);
      setIsLoading(false);
    }
  }, []);

  // Refresh auth (for manual refresh or after token update)
  const refreshAuth = useCallback(async (): Promise<boolean> => {
    try {
      const result = await refreshAccessToken();
      
      if (result.success && result.tokens) {
        setAccessToken(result.tokens.access_token);
        setRefreshToken(result.tokens.refresh_token);
        
        // Also refresh user data
        const currentUser = await getCurrentUser();
        if (currentUser) {
          setUser(currentUser);
        }
        
        return true;
      }
      
      // Refresh failed - logout
      await logout();
      return false;
    } catch {
      await logout();
      return false;
    }
  }, [logout]);

  // Update user data (for external updates like profile changes)
  const updateUser = useCallback((updatedUser: User) => {
    setUser(updatedUser);
  }, []);

  // Context value
  const value: AuthContextType = {
    user,
    accessToken,
    refreshToken,
    isAuthenticated,
    isLoading,
    login,
    signup,
    logout,
    refreshAuth,
    updateUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// ============================================
// HOOK
// ============================================

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}

// ============================================
// PROTECTED ROUTE COMPONENT
// ============================================

interface ProtectedRouteProps {
  children: ReactNode;
  fallback?: ReactNode;
}

export function ProtectedRoute({ children, fallback }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    // Show loading spinner while checking auth
    return (
      <div className="min-h-screen bg-[#0B0C10] flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-2 border-violet-500/30 border-t-violet-500 rounded-full animate-spin" />
          <p className="text-white/50 text-sm">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    // Return fallback or null (parent should handle redirect)
    return fallback ? <>{fallback}</> : null;
  }

  return <>{children}</>;
}

export default AuthContext;

