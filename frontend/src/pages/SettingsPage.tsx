import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  User, 
  Upload, 
  Check, 
  Loader2, 
  Trash2,
  Camera,
  RefreshCw,
  Image,
  Sparkles,
  Shield,
  Monitor,
  Smartphone,
  Globe,
  Clock,
  Crown,
  LogOut,
  AlertCircle,
} from 'lucide-react';
import { uploadFace, deleteFace, getSession } from '../api/client';
import { getActiveSessions, revokeSession, logoutAll } from '../api/auth';
import { getSessionId, API_BASE } from '../config';
import { useAuth } from '../hooks';
import type { SessionInfo } from '../types/auth';

interface SettingsPageProps {
  onFaceChange?: () => void; // Called when face is uploaded or removed
}

export default function SettingsPage({ onFaceChange }: SettingsPageProps) {
  const { user } = useAuth();
  const sessionId = user?.id || getSessionId();
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Face state
  const [facePreview, setFacePreview] = useState<string | null>(null);
  const [faceUploaded, setFaceUploaded] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  
  // Sessions state
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [isLoadingSessions, setIsLoadingSessions] = useState(false);
  const [revokingSessionId, setRevokingSessionId] = useState<string | null>(null);
  const [isLoggingOutAll, setIsLoggingOutAll] = useState(false);
  const [sessionError, setSessionError] = useState<string | null>(null);
  
  // Preferences state
  const [preferences, setPreferences] = useState({
    autoThumbnails: true,
    includeFaceByDefault: true,
    soundEffects: false,
  });

  // Load face status on mount
  useEffect(() => {
    const checkFaceStatus = async () => {
      try {
        const session = await getSession(sessionId);
        if (session.has_face && session.face_path) {
          setFaceUploaded(true);
          setFacePreview(`${API_BASE}/face/${sessionId}?t=${Date.now()}`);
        }
      } catch (e) {
        // Session doesn't exist or no face - that's fine
      }
    };
    checkFaceStatus();
  }, [sessionId]);

  // Load sessions
  useEffect(() => {
    const loadSessions = async () => {
      setIsLoadingSessions(true);
      try {
        const response = await getActiveSessions();
        if (response) {
          setSessions(response.sessions);
        }
      } catch (e) {
        console.error('Failed to load sessions:', e);
      } finally {
        setIsLoadingSessions(false);
      }
    };
    loadSessions();
  }, []);

  // Load preferences from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('virallab_preferences');
    if (saved) {
      try {
        setPreferences(JSON.parse(saved));
      } catch (e) {
        // Ignore parse errors
      }
    }
  }, []);

  // Save preferences
  const savePreferences = (newPrefs: typeof preferences) => {
    setPreferences(newPrefs);
    localStorage.setItem('virallab_preferences', JSON.stringify(newPrefs));
  };

  // Handle file selection
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
        setUploadError('Please upload a JPG, PNG, or WebP image');
        return;
      }
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setUploadError('Image must be smaller than 5MB');
        return;
      }
      setUploadError(null);
      // Create preview
      const reader = new FileReader();
      reader.onload = (event) => {
        setFacePreview(event.target?.result as string);
      };
      reader.readAsDataURL(file);
      // Upload
      handleUpload(file);
    }
  };

  // Handle upload
  const handleUpload = async (file: File) => {
    setIsUploading(true);
    setUploadError(null);
    try {
      const response = await uploadFace(file, sessionId);
      if (response.success) {
        setFaceUploaded(true);
        // Refresh preview from server
        setFacePreview(`${API_BASE}/face/${sessionId}?t=${Date.now()}`);
        // Notify parent that face changed
        onFaceChange?.();
      } else {
        setUploadError(response.error || 'Upload failed');
        setFacePreview(null);
      }
    } catch (e) {
      setUploadError('Failed to upload. Please try again.');
      setFacePreview(null);
    } finally {
      setIsUploading(false);
    }
  };

  // Handle remove
  const handleRemove = async () => {
    try {
      await deleteFace(sessionId);
    } catch (e) {
      // Ignore errors
    }
    setFacePreview(null);
    setFaceUploaded(false);
    // Notify parent that face changed
    onFaceChange?.();
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Revoke a specific session
  const handleRevokeSession = async (sessionId: string) => {
    setRevokingSessionId(sessionId);
    setSessionError(null);
    try {
      const result = await revokeSession(sessionId);
      if (result.success) {
        setSessions(prev => prev.filter(s => s.id !== sessionId));
      } else {
        setSessionError(result.message || 'Failed to revoke session');
      }
    } catch (e) {
      setSessionError('Failed to revoke session');
    } finally {
      setRevokingSessionId(null);
    }
  };

  // Logout from all other devices
  const handleLogoutAll = async () => {
    setIsLoggingOutAll(true);
    setSessionError(null);
    try {
      const result = await logoutAll();
      if (result.success) {
        // Reload sessions (should be empty or just current)
        const response = await getActiveSessions();
        if (response) {
          setSessions(response.sessions);
        }
      }
    } catch (e) {
      setSessionError('Failed to logout from all devices');
    } finally {
      setIsLoggingOutAll(false);
    }
  };

  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  };

  // Get device icon
  const getDeviceIcon = (deviceInfo: string | null) => {
    if (!deviceInfo) return Globe;
    const info = deviceInfo.toLowerCase();
    if (info.includes('mobile') || info.includes('android') || info.includes('iphone')) {
      return Smartphone;
    }
    return Monitor;
  };

  // Parse device info for display
  const parseDeviceInfo = (deviceInfo: string | null) => {
    if (!deviceInfo) return 'Unknown device';
    // Simplify user agent
    if (deviceInfo.includes('Chrome')) return 'Chrome Browser';
    if (deviceInfo.includes('Firefox')) return 'Firefox Browser';
    if (deviceInfo.includes('Safari') && !deviceInfo.includes('Chrome')) return 'Safari Browser';
    if (deviceInfo.includes('Edge')) return 'Edge Browser';
    return 'Web Browser';
  };

  return (
    <div className="flex flex-col items-center min-h-[calc(100vh-120px)] px-6 pt-8 pb-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-2xl"
      >
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-semibold text-white mb-1">Settings</h1>
          <p className="text-sm text-white/50">Manage your account and preferences</p>
        </div>

        {/* Account Info Section */}
        {user && (
          <div className="bg-white/[0.02] border border-white/[0.06] rounded-xl p-6 mb-6">
            <div className="flex items-start gap-2 mb-6">
              <User className="w-5 h-5 text-white/70 mt-0.5" />
              <div>
                <h2 className="text-base font-medium text-white">Account</h2>
                <p className="text-xs text-white/40 mt-0.5">
                  Your account information
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4 p-4 rounded-lg bg-white/[0.02] border border-white/[0.04]">
              {/* Avatar */}
              <div className={`w-14 h-14 rounded-full overflow-hidden flex items-center justify-center ${
                facePreview ? '' : 'bg-gradient-to-br from-violet-500 to-purple-600'
              }`}>
                {facePreview ? (
                  <img src={facePreview} alt="Profile" className="w-full h-full object-cover" />
                ) : (
                  <span className="text-xl font-semibold text-white">
                    {user.full_name?.charAt(0).toUpperCase() || user.email?.charAt(0).toUpperCase() || 'U'}
                  </span>
                )}
              </div>

              {/* Info */}
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <p className="text-base font-medium text-white">{user.full_name}</p>
                  {user.is_premium && (
                    <div className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-500/20 border border-amber-500/30">
                      <Crown className="w-3 h-3 text-amber-400" />
                      <span className="text-xs font-medium text-amber-400">Premium</span>
                    </div>
                  )}
                </div>
                <p className="text-sm text-white/50">{user.email}</p>
                <p className="text-xs text-white/30 mt-1">
                  Member since {new Date(user.created_at).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Your Face Section */}
        <div className="bg-white/[0.02] border border-white/[0.06] rounded-xl p-6 mb-6">
          <div className="flex items-start gap-2 mb-6">
            <Camera className="w-5 h-5 text-white/70 mt-0.5" />
            <div>
              <h2 className="text-base font-medium text-white">Your Face</h2>
              <p className="text-xs text-white/40 mt-0.5">
                Upload your photo to appear in AI-generated thumbnails
              </p>
            </div>
          </div>
          
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={handleFileSelect}
            className="hidden"
          />
          
          <div className="flex items-start gap-6">
            {/* Face Preview Circle */}
            <div className="relative flex-shrink-0">
              <div 
                className={`w-28 h-28 rounded-full overflow-hidden border-2 transition-all ${
                  isUploading 
                    ? 'border-white/30' 
                    : faceUploaded 
                      ? 'border-emerald-500/50' 
                      : 'border-white/[0.08] border-dashed'
                }`}
              >
                {facePreview ? (
                  <img 
                    src={facePreview} 
                    alt="Your face" 
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full bg-white/[0.02] flex items-center justify-center">
                    <User className="w-10 h-10 text-white/20" />
                  </div>
                )}
                
                {/* Upload overlay on hover */}
                {!isUploading && (
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="absolute inset-0 bg-black/60 opacity-0 hover:opacity-100 transition-opacity flex items-center justify-center rounded-full"
                  >
                    <Upload className="w-6 h-6 text-white" />
                  </button>
                )}
                
                {/* Loading overlay */}
                {isUploading && (
                  <div className="absolute inset-0 bg-black/60 flex items-center justify-center rounded-full">
                    <Loader2 className="w-6 h-6 text-white animate-spin" />
                  </div>
                )}
              </div>
              
              {/* Status indicator */}
              {faceUploaded && !isUploading && (
                <div className="absolute -bottom-1 -right-1 w-7 h-7 rounded-full bg-emerald-500 flex items-center justify-center border-2 border-[#0a0a0a]">
                  <Check className="w-4 h-4 text-white" />
                </div>
              )}
            </div>

            {/* Info & Actions */}
            <div className="flex-1 pt-2">
              {faceUploaded ? (
                <>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-sm text-emerald-400 font-medium">Face uploaded</span>
                  </div>
                  <p className="text-xs text-white/40 mb-4">
                    Your face will be included in thumbnail generations when enabled.
                  </p>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      disabled={isUploading}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-white/[0.05] hover:bg-white/[0.08] border border-white/[0.08] text-xs text-white/70 transition-colors"
                    >
                      <RefreshCw className="w-3 h-3" />
                      Change
                    </button>
                    <button
                      onClick={handleRemove}
                      disabled={isUploading}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-md hover:bg-red-500/10 border border-transparent text-xs text-white/40 hover:text-red-400 transition-colors"
                    >
                      <Trash2 className="w-3 h-3" />
                      Remove
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <p className="text-sm text-white/60 mb-3">
                    No face uploaded yet
                  </p>
                  <p className="text-xs text-white/30 mb-4">
                    For best results, use a clear, front-facing photo with good lighting.
                  </p>
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    disabled={isUploading}
                    className="flex items-center gap-2 px-4 py-2 rounded-md bg-white/10 hover:bg-white/15 text-sm text-white font-medium transition-colors"
                  >
                    <Upload className="w-4 h-4" />
                    Upload Photo
                  </button>
                </>
              )}
              
              {/* Error message */}
              {uploadError && (
                <p className="text-xs text-red-400 mt-3">{uploadError}</p>
              )}
            </div>
          </div>
          
          {/* Usage hint */}
          {faceUploaded && (
            <div className="mt-6 pt-4 border-t border-white/[0.06]">
              <div className="flex items-start gap-2 text-xs text-white/40">
                <Sparkles className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" />
                <span>
                  Your face will be intelligently integrated into thumbnails. 
                  You can toggle this per-generation in the Workflow page.
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Active Sessions Section */}
        <div className="bg-white/[0.02] border border-white/[0.06] rounded-xl p-6 mb-6">
          <div className="flex items-start gap-2 mb-6">
            <Shield className="w-5 h-5 text-white/70 mt-0.5" />
            <div className="flex-1">
              <h2 className="text-base font-medium text-white">Active Sessions</h2>
              <p className="text-xs text-white/40 mt-0.5">
                Devices where you're currently logged in
              </p>
            </div>
            {sessions.length > 1 && (
              <button
                onClick={handleLogoutAll}
                disabled={isLoggingOutAll}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs text-red-400 hover:bg-red-500/10 transition-colors"
              >
                {isLoggingOutAll ? (
                  <Loader2 className="w-3 h-3 animate-spin" />
                ) : (
                  <LogOut className="w-3 h-3" />
                )}
                Sign out all
              </button>
            )}
          </div>

          {sessionError && (
            <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-red-400" />
              <p className="text-xs text-red-400">{sessionError}</p>
            </div>
          )}

          {isLoadingSessions ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-5 h-5 text-white/30 animate-spin" />
            </div>
          ) : sessions.length === 0 ? (
            <p className="text-sm text-white/40 text-center py-4">No active sessions</p>
          ) : (
            <div className="space-y-2">
              {sessions.map((session, index) => {
                const DeviceIcon = getDeviceIcon(session.device_info);
                const isFirst = index === 0;
                
                return (
                  <div
                    key={session.id}
                    className={`flex items-center gap-3 p-3 rounded-lg transition-colors ${
                      isFirst ? 'bg-violet-500/10 border border-violet-500/20' : 'bg-white/[0.02] border border-white/[0.04]'
                    }`}
                  >
                    <div className={`w-9 h-9 rounded-full flex items-center justify-center ${
                      isFirst ? 'bg-violet-500/20' : 'bg-white/[0.05]'
                    }`}>
                      <DeviceIcon className={`w-4 h-4 ${isFirst ? 'text-violet-400' : 'text-white/50'}`} />
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="text-sm text-white/80 truncate">
                          {parseDeviceInfo(session.device_info)}
                        </p>
                        {isFirst && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-violet-500/30 text-violet-300 font-medium">
                            Current
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-2 text-xs text-white/40">
                        <Clock className="w-3 h-3" />
                        <span>Last active: {formatDate(session.last_used_at)}</span>
                      </div>
                    </div>
                    
                    {!isFirst && (
                      <button
                        onClick={() => handleRevokeSession(session.id)}
                        disabled={revokingSessionId === session.id}
                        className="p-2 rounded-md text-white/40 hover:text-red-400 hover:bg-red-500/10 transition-colors"
                      >
                        {revokingSessionId === session.id ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <LogOut className="w-4 h-4" />
                        )}
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Preferences Section */}
        <div className="bg-white/[0.02] border border-white/[0.06] rounded-xl p-6 mb-6">
          <div className="flex items-start gap-2 mb-6">
            <Image className="w-5 h-5 text-white/70 mt-0.5" />
            <div>
              <h2 className="text-base font-medium text-white">Thumbnail Preferences</h2>
              <p className="text-xs text-white/40 mt-0.5">
                Default settings for content generation
              </p>
            </div>
          </div>
          
          <div className="space-y-1">
            {/* Auto-generate thumbnails */}
            <div className="flex items-center justify-between py-3 border-b border-white/[0.04]">
              <div>
                <p className="text-sm text-white/80">Auto-generate thumbnails</p>
                <p className="text-xs text-white/30 mt-0.5">Create thumbnails automatically with scripts</p>
              </div>
              <button
                onClick={() => savePreferences({ ...preferences, autoThumbnails: !preferences.autoThumbnails })}
                className={`relative w-11 h-6 rounded-full transition-colors ${
                  preferences.autoThumbnails ? 'bg-white/20' : 'bg-white/[0.08]'
                }`}
              >
                <div 
                  className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-all ${
                    preferences.autoThumbnails ? 'left-6' : 'left-1'
                  }`}
                />
              </button>
            </div>
            
            {/* Include face by default */}
            <div className="flex items-center justify-between py-3 border-b border-white/[0.04]">
              <div>
                <p className="text-sm text-white/80">Include face by default</p>
                <p className="text-xs text-white/30 mt-0.5">Always include your face in thumbnails</p>
              </div>
              <button
                onClick={() => savePreferences({ ...preferences, includeFaceByDefault: !preferences.includeFaceByDefault })}
                className={`relative w-11 h-6 rounded-full transition-colors ${
                  preferences.includeFaceByDefault ? 'bg-white/20' : 'bg-white/[0.08]'
                }`}
                disabled={!faceUploaded}
              >
                <div 
                  className={`absolute top-1 w-4 h-4 rounded-full transition-all ${
                    preferences.includeFaceByDefault && faceUploaded ? 'bg-white left-6' : 'bg-white/50 left-1'
                  }`}
                />
              </button>
            </div>
            
            {/* Sound effects */}
            <div className="flex items-center justify-between py-3">
              <div>
                <p className="text-sm text-white/80">Sound effects</p>
                <p className="text-xs text-white/30 mt-0.5">Play sounds when generations complete</p>
              </div>
              <button
                onClick={() => savePreferences({ ...preferences, soundEffects: !preferences.soundEffects })}
                className={`relative w-11 h-6 rounded-full transition-colors ${
                  preferences.soundEffects ? 'bg-white/20' : 'bg-white/[0.08]'
                }`}
              >
                <div 
                  className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-all ${
                    preferences.soundEffects ? 'left-6' : 'left-1'
                  }`}
                />
              </button>
            </div>
          </div>
        </div>

        {/* API Keys Section */}
        <div className="bg-white/[0.02] border border-white/[0.06] rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-medium text-white">API Configuration</h2>
              <p className="text-xs text-white/40 mt-0.5">
                API keys are configured via environment variables
              </p>
            </div>
            <div className="flex items-center gap-1.5 px-2 py-1 rounded bg-emerald-500/10 border border-emerald-500/20">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              <span className="text-xs text-emerald-400">Connected</span>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
