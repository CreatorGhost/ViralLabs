import React, { useState, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Lock, Sparkles, ArrowRight, Clock, CheckCircle2, Coins } from 'lucide-react';
import CrystalDock, { TabId } from './components/CrystalDock';
import { WorkflowPage, ThumbnailStudioPage, ImageStudioPage, AudioStudioPage, SettingsPage } from './pages';
import { getSession } from './api/client';
import { getSessionId } from './config';
import { useAuth } from './hooks';
import { usePremiumStatus } from './context';
import { getPaymentStatus, type PaymentRequest } from './api/payment';

// Shared state for passing script to audio page
export interface AudioGenerationState {
  script: string;
  autoStart: boolean;
}

// Face state interface
export interface FaceState {
  facePreview: string | null;
  faceUploaded: boolean;
  includeFace: boolean;
}

export default function Dashboard() {
  const navigate = useNavigate();
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();
  const { isPremium } = usePremiumStatus();
  const [activeTab, setActiveTab] = useState<TabId>('workflow');
  const [audioState, setAudioState] = useState<AudioGenerationState>({ script: '', autoStart: false });

  // Payment status state
  const [hasPendingPayment, setHasPendingPayment] = useState(false);
  const [pendingPayment, setPendingPayment] = useState<PaymentRequest | null>(null);

  // Use user ID as session ID if authenticated, otherwise use default
  const sessionId = user?.id || getSessionId();

  // Global face state
  const [faceState, setFaceState] = useState<FaceState>({
    facePreview: null,
    faceUploaded: false,
    includeFace: false,
  });

  // Check for pending payment request on mount
  useEffect(() => {
    const checkPaymentStatus = async () => {
      if (!isAuthenticated || isPremium) return;

      try {
        const status = await getPaymentStatus();
        setHasPendingPayment(status.has_pending);
        setPendingPayment(status.pending_request || null);
      } catch {
        // Ignore errors - user might not have any payment requests
      }
    };

    if (!authLoading) {
      checkPaymentStatus();
    }
  }, [isAuthenticated, isPremium, authLoading]);

  // Load face status on mount
  useEffect(() => {
    const loadFaceStatus = async () => {
      if (!isAuthenticated) return;
      
      try {
        const session = await getSession(sessionId);
        if (session.has_face && session.face_path) {
          // Check user preference for including face by default
          const prefs = localStorage.getItem('virallab_preferences');
          const includeByDefault = prefs ? JSON.parse(prefs).includeFaceByDefault ?? true : true;
          
          setFaceState({
            facePreview: session.face_path ?? null,
            faceUploaded: true,
            includeFace: includeByDefault,
          });
        }
      } catch (e) {
        // Session doesn't exist or no face - that's fine
      }
    };
    
    if (!authLoading) {
      loadFaceStatus();
    }
  }, [sessionId, isAuthenticated, authLoading]);

  // Refresh face status (called after upload/delete in Settings)
  const refreshFaceStatus = useCallback(async () => {
    try {
      const session = await getSession(sessionId);
      if (session.has_face && session.face_path) {
        setFaceState(prev => ({
          ...prev,
          facePreview: session.face_path ?? null,
          faceUploaded: true,
        }));
      } else {
        setFaceState({
          facePreview: null,
          faceUploaded: false,
          includeFace: false,
        });
      }
    } catch (e) {
      // Ignore errors
    }
  }, [sessionId]);

  // Toggle face inclusion
  const toggleFace = useCallback(() => {
    setFaceState(prev => ({
      ...prev,
      includeFace: !prev.includeFace,
    }));
  }, []);

  // Callback to navigate to audio page with script
  // autoStart is FALSE so user can review/edit script and select voice/persona before generating
  const navigateToAudio = useCallback((script: string) => {
    setAudioState({ script, autoStart: false });
    setActiveTab('audio');
  }, []);

  // Clear auto-start state after audio page handles it
  const clearAudioAutoStart = useCallback(() => {
    setAudioState(prev => ({ ...prev, autoStart: false }));
  }, []);

  // Show loading while checking auth
  if (authLoading) {
    return (
      <div className="min-h-screen bg-[#0B0C10] flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-2 border-violet-500/30 border-t-violet-500 rounded-full animate-spin" />
          <p className="text-white/50 text-sm">Loading...</p>
        </div>
      </div>
    );
  }

  // Paywall component for non-premium users
  const PaywallOverlay = () => {
    // Show pending payment message if there's a pending request
    if (hasPendingPayment && pendingPayment) {
      return (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col items-center justify-center min-h-[60vh] px-6"
        >
          <div className="relative max-w-md w-full">
            {/* Glow effect */}
            <div className="absolute inset-0 bg-gradient-to-r from-amber-600/20 to-orange-600/20 blur-3xl" />

            <div className="relative p-8 rounded-2xl bg-white/[0.03] border border-amber-500/30 backdrop-blur-sm text-center">
              <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-amber-500/20 to-orange-500/20 border border-amber-500/30 flex items-center justify-center">
                <Clock className="w-8 h-8 text-amber-400" />
              </div>

              <h2 className="text-2xl font-bold mb-3">Payment Under Review</h2>
              <p className="text-white/60 mb-6">
                Thank you for your payment! Your 10 credits will be added within 24 hours after we verify your payment.
              </p>

              <div className="p-4 rounded-xl bg-white/5 border border-white/10 mb-6">
                <div className="flex items-center justify-between text-sm mb-2">
                  <span className="text-white/50">Status</span>
                  <span className="flex items-center gap-2 text-amber-400">
                    <Clock className="w-4 h-4" />
                    Pending Verification
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-white/50">Submitted</span>
                  <span className="text-white/70">
                    {new Date(pendingPayment.created_at).toLocaleDateString('en-IN', {
                      day: 'numeric',
                      month: 'short',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </span>
                </div>
              </div>

              <p className="text-xs text-white/40 mb-4">
                We'll notify you via email once your account is activated.
              </p>

              <button
                onClick={() => setActiveTab('settings')}
                className="w-full px-6 py-3 rounded-xl bg-white/10 hover:bg-white/15 font-medium transition-all"
              >
                Go to Settings
              </button>
            </div>
          </div>
        </motion.div>
      );
    }

    // Default paywall - no credits
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col items-center justify-center min-h-[60vh] px-6"
      >
        <div className="relative max-w-md w-full">
          {/* Glow effect */}
          <div className="absolute inset-0 bg-gradient-to-r from-violet-600/20 to-purple-600/20 blur-3xl" />

          <div className="relative p-8 rounded-2xl bg-white/[0.03] border border-white/10 backdrop-blur-sm text-center">
            <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-violet-500/20 to-purple-500/20 border border-violet-500/30 flex items-center justify-center">
              <Coins className="w-8 h-8 text-amber-400" />
            </div>

            <h2 className="text-2xl font-bold mb-3">Buy Credits to Continue</h2>
            <p className="text-white/60 mb-6">
              Purchase credits to unlock thumbnail generation, audio voiceovers, and all premium features.
            </p>

            <div className="space-y-3 mb-8 text-left">
              {[
                '10 script generations per pack (free)',
                '10 thumbnail generations per pack',
                'Professional audio voiceovers',
                'Priority processing',
              ].map((feature, i) => (
                <div key={i} className="flex items-center gap-3 text-sm text-white/70">
                  <Sparkles className="w-4 h-4 text-violet-400 flex-shrink-0" />
                  <span>{feature}</span>
                </div>
              ))}
            </div>

            <button
              onClick={() => navigate('/pricing')}
              className="w-full px-6 py-3 rounded-xl bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-500 hover:to-purple-500 font-medium transition-all flex items-center justify-center gap-2"
            >
              Buy Credits <ArrowRight className="w-4 h-4" />
            </button>

            <p className="mt-4 text-xs text-white/40">
              ₹50 for 10 credits. Credits never expire.
            </p>
          </div>
        </div>
      </motion.div>
    );
  };

  // Check if current tab requires premium (settings is always accessible)
  const requiresPremium = activeTab !== 'settings' && !isPremium;

  return (
    <div className="min-h-screen bg-[#0B0C10] text-white overflow-x-hidden">
      {/* Ambient Background */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-violet-500/10 rounded-full blur-[100px]" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-[100px]" />
      </div>

      {/* Crystal Dock Navigation with Face Indicator */}
      <CrystalDock 
        activeTab={activeTab} 
        setActiveTab={setActiveTab}
        facePreview={faceState.facePreview}
        faceUploaded={faceState.faceUploaded}
        includeFace={faceState.includeFace}
        onToggleFace={toggleFace}
      />

      {/* Page Content with Fluid Transitions */}
      <div className="pt-14 md:pt-24 pb-28 md:pb-0">
        <AnimatePresence mode="wait">
          {/* Show paywall if user is not premium and trying to access premium features */}
          {requiresPremium ? (
            <motion.div
              key="paywall"
              initial={{ opacity: 0, scale: 0.95, filter: "blur(10px)" }}
              animate={{ opacity: 1, scale: 1, filter: "blur(0px)" }}
              exit={{ opacity: 0, scale: 1.05, filter: "blur(10px)" }}
              transition={{ duration: 0.4 }}
            >
              <PaywallOverlay />
            </motion.div>
          ) : (
            <>
              {activeTab === 'workflow' && (
                <motion.div
                  key="workflow"
                  initial={{ opacity: 0, scale: 0.95, filter: "blur(10px)" }}
                  animate={{ opacity: 1, scale: 1, filter: "blur(0px)" }}
                  exit={{ opacity: 0, scale: 1.05, filter: "blur(10px)" }}
                  transition={{ duration: 0.4 }}
                >
                  <WorkflowPage
                    onGenerateAudio={navigateToAudio}
                    includeFace={faceState.faceUploaded && faceState.includeFace}
                  />
                </motion.div>
              )}
              {activeTab === 'thumbnail' && (
                <motion.div
                  key="thumbnail"
                  initial={{ opacity: 0, scale: 0.95, filter: "blur(10px)" }}
                  animate={{ opacity: 1, scale: 1, filter: "blur(0px)" }}
                  exit={{ opacity: 0, scale: 1.05, filter: "blur(10px)" }}
                  transition={{ duration: 0.4 }}
                >
                  <ThumbnailStudioPage
                    includeFace={faceState.faceUploaded && faceState.includeFace}
                  />
                </motion.div>
              )}
              {activeTab === 'image' && (
                <motion.div
                  key="image"
                  initial={{ opacity: 0, scale: 0.95, filter: "blur(10px)" }}
                  animate={{ opacity: 1, scale: 1, filter: "blur(0px)" }}
                  exit={{ opacity: 0, scale: 1.05, filter: "blur(10px)" }}
                  transition={{ duration: 0.4 }}
                >
                  <ImageStudioPage
                    includeFace={faceState.faceUploaded && faceState.includeFace}
                  />
                </motion.div>
              )}
              {activeTab === 'audio' && (
                <motion.div
                  key="audio"
                  initial={{ opacity: 0, scale: 0.95, filter: "blur(10px)" }}
                  animate={{ opacity: 1, scale: 1, filter: "blur(0px)" }}
                  exit={{ opacity: 0, scale: 1.05, filter: "blur(10px)" }}
                  transition={{ duration: 0.4 }}
                >
                  <AudioStudioPage
                    incomingScript={audioState.script}
                    autoStart={audioState.autoStart}
                    onAutoStartHandled={clearAudioAutoStart}
                  />
                </motion.div>
              )}
              {activeTab === 'settings' && (
                <motion.div
                  key="settings"
                  initial={{ opacity: 0, scale: 0.95, filter: "blur(10px)" }}
                  animate={{ opacity: 1, scale: 1, filter: "blur(0px)" }}
                  exit={{ opacity: 0, scale: 1.05, filter: "blur(10px)" }}
                  transition={{ duration: 0.4 }}
                >
                  <SettingsPage onFaceChange={refreshFaceStatus} />
                </motion.div>
              )}
            </>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
