import React, { useState, useEffect, useRef } from 'react';
import { motion, useAnimationControls, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Zap, Image, Wand2, Mic, Settings, User, Check, Upload, ChevronRight, LogOut, Crown } from 'lucide-react';
import { useAuth } from '../hooks';

export type TabId = 'workflow' | 'thumbnail' | 'image' | 'audio' | 'settings';

interface Tab {
  id: TabId;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}

const tabs: Tab[] = [
  { id: 'workflow', label: 'Workflow', icon: Zap },
  { id: 'thumbnail', label: 'Thumbnails', icon: Image },
  { id: 'image', label: 'Image', icon: Wand2 },
  { id: 'audio', label: 'Audio', icon: Mic },
  { id: 'settings', label: 'Settings', icon: Settings },
];

interface CrystalDockProps {
  activeTab: TabId;
  setActiveTab: (tab: TabId) => void;
  // Face-related props
  facePreview?: string | null;
  faceUploaded?: boolean;
  includeFace?: boolean;
  onToggleFace?: () => void;
}

export default function CrystalDock({ 
  activeTab, 
  setActiveTab,
  facePreview,
  faceUploaded,
  includeFace,
  onToggleFace,
}: CrystalDockProps) {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [isVisible, setIsVisible] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0);
  const [showFacePopover, setShowFacePopover] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const controls = useAnimationControls();
  const popoverRef = useRef<HTMLDivElement>(null);

  // Handle logout
  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
      // Still navigate to login even if API call fails
      navigate('/login');
    } finally {
      setIsLoggingOut(false);
    }
  };

  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      const scrollThreshold = 10;
      
      if (Math.abs(currentScrollY - lastScrollY) < scrollThreshold) {
        return;
      }

      if (currentScrollY < 50) {
        setIsVisible(true);
      } else if (currentScrollY > lastScrollY) {
        setIsVisible(false);
      } else {
        setIsVisible(true);
      }

      setLastScrollY(currentScrollY);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [lastScrollY]);

  // Close popovers when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
        setShowFacePopover(false);
      }
    };
    
    if (showFacePopover) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showFacePopover]);

  useEffect(() => {
    if (isVisible) {
      controls.start({ 
        y: 0, 
        opacity: 1,
        transition: { type: "spring", stiffness: 300, damping: 30 }
      });
    } else {
      controls.start({ 
        y: -100, 
        opacity: 0,
        transition: { type: "spring", stiffness: 300, damping: 30 }
      });
    }
  }, [isVisible, controls]);

  // Get user initials
  const getUserInitial = () => {
    if (user?.full_name) {
      return user.full_name.charAt(0).toUpperCase();
    }
    if (user?.email) {
      return user.email.charAt(0).toUpperCase();
    }
    return 'U';
  };

  return (
    <>
      {/* Desktop / Tablet Dock */}
      <motion.nav 
        initial={{ y: 0, opacity: 1 }}
        animate={controls}
        className="hidden md:flex fixed top-6 left-1/2 -translate-x-1/2 z-50 items-center gap-3"
      >
        {/* Main Navigation */}
        <div className="p-2 rounded-full bg-black/40 backdrop-blur-2xl border border-white/10 shadow-[0_8px_32px_rgba(0,0,0,0.5)]">
          <ul className="flex items-center gap-1">
            {tabs.map((tab) => (
              <li key={tab.id} className="relative">
                <button
                  type="button"
                  onClick={() => setActiveTab(tab.id)}
                  className="relative px-6 py-2.5 rounded-full cursor-pointer"
                  aria-current={activeTab === tab.id ? 'page' : undefined}
                >
                  {activeTab === tab.id && (
                    <motion.div
                      layoutId="crystal-glow"
                      className="absolute inset-0 rounded-full bg-gradient-to-r from-violet-600 to-purple-600 shadow-[0_0_15px_rgba(139,92,246,0.5)]"
                      transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                    />
                  )}
                  <span
                    className={`relative z-10 flex items-center gap-2 text-sm font-medium transition-colors duration-200 
                              ${activeTab === tab.id ? 'text-white' : 'text-white/50 hover:text-white/80'}`}
                  >
                    <tab.icon className="w-4 h-4" />
                    {tab.label}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        </div>

        {/* Face Indicator - Separate pill */}
        <div className="relative" ref={popoverRef}>
          <button
            onClick={() => setShowFacePopover(!showFacePopover)}
            className={`relative flex items-center gap-2 px-3 py-2 rounded-full backdrop-blur-2xl border shadow-[0_8px_32px_rgba(0,0,0,0.5)] transition-all ${
              faceUploaded && includeFace
                ? 'bg-emerald-500/20 border-emerald-500/30 hover:border-emerald-500/50'
                : 'bg-black/40 border-white/10 hover:border-white/20'
            }`}
          >
            {/* Avatar */}
            <div className={`w-7 h-7 rounded-full overflow-hidden flex items-center justify-center ${
              facePreview ? '' : 'bg-gradient-to-br from-violet-500 to-purple-600'
            }`}>
              {facePreview ? (
                <img src={facePreview} alt="Your face" className="w-full h-full object-cover" />
              ) : (
                <span className="text-xs font-semibold text-white">{getUserInitial()}</span>
              )}
            </div>
            
            {/* Status indicator */}
            {faceUploaded && (
              <div className={`absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-[#0a0a0a] ${
                includeFace ? 'bg-emerald-400' : 'bg-white/30'
              }`} />
            )}
          </button>

          {/* Popover */}
          <AnimatePresence>
            {showFacePopover && (
              <motion.div
                initial={{ opacity: 0, y: 10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 10, scale: 0.95 }}
                transition={{ duration: 0.15 }}
                className="absolute top-full right-0 mt-3 w-72 rounded-xl bg-[#0f1014]/95 backdrop-blur-xl border border-white/10 shadow-2xl overflow-hidden"
              >
                {/* User Info Header */}
                {user && (
                  <div className="px-4 pt-4 pb-3 border-b border-white/[0.06]">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-full overflow-hidden flex items-center justify-center ${
                        facePreview ? 'border-2 border-white/10' : 'bg-gradient-to-br from-violet-500 to-purple-600'
                      }`}>
                        {facePreview ? (
                          <img src={facePreview} alt="Profile" className="w-full h-full object-cover" />
                        ) : (
                          <span className="text-sm font-semibold text-white">
                            {getUserInitial()}
                          </span>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <p className="text-sm font-medium text-white truncate">
                            {user.full_name || 'User'}
                          </p>
                          {user.is_premium && (
                            <Crown className="w-3.5 h-3.5 text-amber-400" />
                          )}
                        </div>
                        <p className="text-xs text-white/40 truncate">
                          {user.email}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Face Settings Section */}
                <div className="p-4">
                  <p className="text-[10px] font-medium text-white/40 uppercase tracking-wider mb-2">
                    Face Settings
                  </p>
                  
                  {/* Face Preview */}
                  <div className="flex items-center gap-3 mb-3 p-2 rounded-lg bg-white/[0.02]">
                    <div className={`w-8 h-8 rounded-full overflow-hidden flex items-center justify-center ${
                      facePreview ? '' : 'bg-white/[0.05] border border-dashed border-white/10'
                    }`}>
                      {facePreview ? (
                        <img src={facePreview} alt="Your face" className="w-full h-full object-cover" />
                      ) : (
                        <User className="w-4 h-4 text-white/30" />
                      )}
                    </div>
                    <div className="flex-1">
                      <p className="text-xs font-medium text-white/70">
                        {faceUploaded ? 'Face uploaded' : 'No face uploaded'}
                      </p>
                      <p className="text-[10px] text-white/40">
                        {faceUploaded 
                          ? includeFace ? 'Active in thumbnails' : 'Not active'
                          : 'Upload in Settings'}
                      </p>
                    </div>
                  </div>

                  {/* Toggle - Only show if face is uploaded */}
                  {faceUploaded && (
                    <button
                      onClick={() => {
                        onToggleFace?.();
                      }}
                      className={`w-full flex items-center justify-between p-2.5 rounded-lg mb-2 transition-all ${
                        includeFace 
                          ? 'bg-emerald-500/10 border border-emerald-500/20' 
                          : 'bg-white/[0.03] border border-white/[0.06]'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        {includeFace ? (
                          <Check className="w-3.5 h-3.5 text-emerald-400" />
                        ) : (
                          <div className="w-3.5 h-3.5 rounded border border-white/20" />
                        )}
                        <span className="text-xs text-white/80">Include in thumbnails</span>
                      </div>
                      <div className={`w-8 h-4 rounded-full transition-colors relative ${
                        includeFace ? 'bg-emerald-500/50' : 'bg-white/10'
                      }`}>
                        <div className={`absolute top-0.5 w-3 h-3 rounded-full bg-white transition-all ${
                          includeFace ? 'left-4' : 'left-0.5'
                        }`} />
                      </div>
                    </button>
                  )}

                  {/* Settings Link */}
                  <button
                    onClick={() => {
                      setActiveTab('settings');
                      setShowFacePopover(false);
                    }}
                    className="w-full flex items-center justify-between p-2.5 rounded-lg bg-white/[0.03] border border-white/[0.06] hover:bg-white/[0.05] transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      {faceUploaded ? (
                        <Settings className="w-3.5 h-3.5 text-white/50" />
                      ) : (
                        <Upload className="w-3.5 h-3.5 text-white/50" />
                      )}
                      <span className="text-xs text-white/70">
                        {faceUploaded ? 'Manage in Settings' : 'Upload Face'}
                      </span>
                    </div>
                    <ChevronRight className="w-3.5 h-3.5 text-white/30" />
                  </button>
                </div>

                {/* Logout Section */}
                <div className="px-4 pb-4 pt-2 border-t border-white/[0.06]">
                  <button
                    onClick={handleLogout}
                    disabled={isLoggingOut}
                    className="w-full flex items-center gap-2 p-2.5 rounded-lg text-red-400 hover:bg-red-500/10 transition-colors disabled:opacity-50"
                  >
                    {isLoggingOut ? (
                      <div className="w-4 h-4 border-2 border-red-400/30 border-t-red-400 rounded-full animate-spin" />
                    ) : (
                      <LogOut className="w-4 h-4" />
                    )}
                    <span className="text-sm font-medium">
                      {isLoggingOut ? 'Signing out...' : 'Sign out'}
                    </span>
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.nav>

      {/* Mobile Dock */}
      <nav
        className="md:hidden fixed left-1/2 -translate-x-1/2 z-50 w-[min(520px,calc(100vw-1.5rem))]"
        style={{ bottom: 'calc(1rem + env(safe-area-inset-bottom))' }}
        aria-label="Dashboard navigation"
      >
        <div className="p-1.5 rounded-2xl bg-black/40 backdrop-blur-2xl border border-white/10 shadow-[0_8px_32px_rgba(0,0,0,0.5)]">
          <ul className="flex items-center">
            {tabs.map((tab) => (
              <li key={tab.id} className="flex-1">
                <button
                  type="button"
                  onClick={() => setActiveTab(tab.id)}
                  className="relative w-full px-2 py-2 rounded-xl"
                  aria-current={activeTab === tab.id ? 'page' : undefined}
                >
                  {activeTab === tab.id && (
                    <motion.div
                      layoutId="crystal-glow-mobile"
                      className="absolute inset-0 rounded-xl bg-gradient-to-r from-violet-600 to-purple-600 shadow-[0_0_12px_rgba(139,92,246,0.45)]"
                      transition={{ type: "spring", bounce: 0.15, duration: 0.5 }}
                    />
                  )}
                  <div
                    className={`relative z-10 flex flex-col items-center justify-center gap-1 transition-colors duration-200 ${
                      activeTab === tab.id ? 'text-white' : 'text-white/55 hover:text-white/80'
                    }`}
                  >
                    <tab.icon className="w-5 h-5" />
                    <span className="text-[10px] font-medium leading-none">
                      {tab.label}
                    </span>
                  </div>

                  {/* Face status badge on Settings (mobile) */}
                  {tab.id === 'settings' && faceUploaded && (
                    <span
                      className={`absolute right-2.5 top-2.5 h-2 w-2 rounded-full ${
                        includeFace ? 'bg-emerald-400' : 'bg-white/30'
                      }`}
                      aria-hidden="true"
                    />
                  )}
                </button>
              </li>
            ))}
          </ul>
        </div>
      </nav>
    </>
  );
}
