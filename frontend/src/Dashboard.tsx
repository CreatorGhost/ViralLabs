import React, { useState, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import CrystalDock, { TabId } from './components/CrystalDock';
import { WorkflowPage, ThumbnailStudioPage, ImageStudioPage, AudioStudioPage, SettingsPage } from './pages';
import { getSession } from './api/client';
import { getSessionId, API_BASE } from './config';
import { useAuth } from './hooks';

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
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();
  const [activeTab, setActiveTab] = useState<TabId>('workflow');
  const [audioState, setAudioState] = useState<AudioGenerationState>({ script: '', autoStart: false });
  
  // Use user ID as session ID if authenticated, otherwise use default
  const sessionId = user?.id || getSessionId();
  
  // Global face state
  const [faceState, setFaceState] = useState<FaceState>({
    facePreview: null,
    faceUploaded: false,
    includeFace: false,
  });

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
            facePreview: `${API_BASE}/face/${sessionId}?t=${Date.now()}`,
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
          facePreview: `${API_BASE}/face/${sessionId}?t=${Date.now()}`,
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
      <div className="pt-24">
        <AnimatePresence mode="wait">
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
        </AnimatePresence>
      </div>
    </div>
  );
}
