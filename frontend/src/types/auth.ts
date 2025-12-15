// ============================================
// AUTH TYPES
// ============================================

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_premium: boolean;
  credits: number;
  premium_expires_at: string | null;
  created_at: string;
  last_login: string | null;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number; // seconds until access token expires
}

export interface AuthResponse {
  success: boolean;
  user?: User;
  tokens?: TokenResponse;
  error?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface SessionInfo {
  id: string;
  device_info: string | null;
  ip_address: string | null;
  created_at: string;
  last_used_at: string;
}

export interface ActiveSessionsResponse {
  sessions: SessionInfo[];
  count: number;
}

export interface LogoutResponse {
  success: boolean;
  message: string;
}

export interface LogoutAllResponse {
  success: boolean;
  message: string;
  sessions_revoked: number;
}

// ============================================
// AUTH STATE
// ============================================

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<AuthResponse>;
  signup: (email: string, password: string, fullName: string) => Promise<AuthResponse>;
  logout: () => Promise<void>;
  refreshAuth: () => Promise<User | null>;
  updateUser: (user: User) => void;
}

// ============================================
// STORAGE KEYS
// ============================================

export const AUTH_STORAGE_KEYS = {
  ACCESS_TOKEN: 'virallab_access_token',
  REFRESH_TOKEN: 'virallab_refresh_token',
  USER: 'virallab_user',
} as const;

