import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Play, 
  Pause, 
  Volume2, 
  VolumeX,
  Download, 
  RefreshCw, 
  Check,
  AlertCircle,
  Loader2,
  SkipBack,
  SkipForward,
  ChevronDown,
  Mic,
  User,
  Wand2,
} from 'lucide-react';
import { generateAudio, getAudioOptions } from '../api/client';
import { API_BASE } from '../config';
import type { AudioResponse, AudioOptionsResponse, PersonaInfo } from '../types';

interface AudioStudioPageProps {
  incomingScript?: string;
  autoStart?: boolean;
  onAutoStartHandled?: () => void;
}

// Fallback personas in case API fails - professional labels without emojis
const FALLBACK_PERSONAS: PersonaInfo[] = [
  { id: 'storyteller', name: 'Storyteller', description: 'Engaging narrator for stories', icon: '' },
  { id: 'anime', name: 'Anime', description: 'Expressive for anime content', icon: '' },
  { id: 'tech', name: 'Tech Review', description: 'Clear for tech content', icon: '' },
  { id: 'tutorial', name: 'Tutorial', description: 'Patient for how-to content', icon: '' },
  { id: 'vlog', name: 'Vlog', description: 'Casual for vlogs', icon: '' },
  { id: 'podcast', name: 'Podcast', description: 'Conversational for podcasts', icon: '' },
  { id: 'news', name: 'News', description: 'Professional for news', icon: '' },
  { id: 'dramatic', name: 'Dramatic', description: 'Theatrical for drama', icon: '' },
];

export default function AudioStudioPage({ 
  incomingScript = '', 
  autoStart = false,
  onAutoStartHandled 
}: AudioStudioPageProps) {
  // Persona & Voice state
  const [personas, setPersonas] = useState<PersonaInfo[]>(FALLBACK_PERSONAS);
  const [selectedPersona, setSelectedPersona] = useState<string>('storyteller');
  const [selectedVoice, setSelectedVoice] = useState<string>('female');
  const [isPersonaDropdownOpen, setIsPersonaDropdownOpen] = useState(false);
  
  // Script state
  const [script, setScript] = useState(incomingScript);
  
  // Generation state
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationError, setGenerationError] = useState<string | null>(null);
  const [audioResult, setAudioResult] = useState<AudioResponse | null>(null);
  
  // Player state
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [volume, setVolume] = useState(0.75);
  const [isMuted, setIsMuted] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const dropdownRef = useRef<HTMLDivElement | null>(null);
  
  // Waveform visualization
  const [waveformBars] = useState<number[]>(() => 
    Array.from({ length: 48 }, () => Math.random() * 60 + 20)
  );

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsPersonaDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Load audio options on mount
  useEffect(() => {
    loadAudioOptions();
  }, []);

  // Handle incoming script from workflow
  useEffect(() => {
    if (incomingScript) {
      setScript(incomingScript);
    }
  }, [incomingScript]);

  // Auto-start generation when coming from workflow
  useEffect(() => {
    if (autoStart && incomingScript && !isGenerating && !audioResult) {
      handleGenerate();
      onAutoStartHandled?.();
    }
  }, [autoStart, incomingScript]);

  // Update volume when changed
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = isMuted ? 0 : volume;
    }
  }, [volume, isMuted]);

  // Load available personas from API
  const loadAudioOptions = async () => {
    try {
      const options: AudioOptionsResponse = await getAudioOptions();
      if (options.personas && options.personas.length > 0) {
        setPersonas(options.personas);
      }
    } catch (error) {
      console.error('Failed to load audio options:', error);
    }
  };

  // Generate audio
  const handleGenerate = async () => {
    if (!script.trim()) {
      setGenerationError('Please enter a script to generate audio');
      return;
    }

    setIsGenerating(true);
    setGenerationError(null);
    setAudioResult(null);

    try {
      const result = await generateAudio({
        script: script,
        voice: selectedVoice,
        persona: selectedPersona,
      });

      if (result.success) {
        setAudioResult(result);
        setProgress(0);
        setCurrentTime(0);
        setIsPlaying(false);
      } else {
        setGenerationError(result.error || 'Audio generation failed');
      }
    } catch (error) {
      setGenerationError(error instanceof Error ? error.message : 'Audio generation failed');
    } finally {
      setIsGenerating(false);
    }
  };

  // Audio player controls
  const togglePlay = useCallback(() => {
    if (!audioRef.current) return;
    
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  }, [isPlaying]);

  const handleTimeUpdate = () => {
    if (!audioRef.current) return;
    const current = audioRef.current.currentTime;
    const total = audioRef.current.duration;
    setCurrentTime(current);
    setDuration(total);
    setProgress((current / total) * 100);
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!audioRef.current) return;
    const newProgress = Number(e.target.value);
    const newTime = (newProgress / 100) * audioRef.current.duration;
    audioRef.current.currentTime = newTime;
    setProgress(newProgress);
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = Number(e.target.value) / 100;
    setVolume(newVolume);
    setIsMuted(newVolume === 0);
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
  };

  const skipBackward = () => {
    if (!audioRef.current) return;
    audioRef.current.currentTime = Math.max(0, audioRef.current.currentTime - 10);
  };

  const skipForward = () => {
    if (!audioRef.current) return;
    audioRef.current.currentTime = Math.min(audioRef.current.duration, audioRef.current.currentTime + 10);
  };

  const handleAudioEnd = () => {
    setIsPlaying(false);
    setProgress(100);
  };

  const formatTime = (seconds: number) => {
    if (!seconds || isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Download audio
  const handleDownload = async () => {
    if (!audioResult?.audio_url) return;
    
    setIsDownloading(true);
    try {
      const response = await fetch(`${API_BASE}${audioResult.audio_url}`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = audioResult.filename || 'generated_audio.mp3';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
      setGenerationError('Failed to download audio file');
    } finally {
      setIsDownloading(false);
    }
  };

  // Get current persona info
  const currentPersona = personas.find(p => p.id === selectedPersona) || personas[0];
  const wordCount = script.split(/\s+/).filter(w => w).length;

  return (
    <div className="min-h-[calc(100vh-120px)] px-4 sm:px-6 lg:px-8 py-8">
      {/* Hidden Audio Element */}
      {audioResult?.audio_url && (
        <audio
          ref={audioRef}
          src={`${API_BASE}${audioResult.audio_url}`}
          onTimeUpdate={handleTimeUpdate}
          onEnded={handleAudioEnd}
          onLoadedMetadata={handleTimeUpdate}
          preload="metadata"
        />
      )}

      <div className="max-w-5xl mx-auto">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-semibold text-white tracking-tight">Audio Studio</h1>
          <p className="text-sm text-white/40 mt-1">Generate professional voiceovers from your scripts</p>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Settings */}
          <div className="lg:col-span-1 space-y-4">
            {/* Voice Selection Card */}
            <div className="bg-white/[0.02] border border-white/[0.06] rounded-lg p-4">
              <label className="text-xs font-medium text-white/50 uppercase tracking-wider mb-3 block">
                Voice
              </label>
              <div className="flex gap-2">
                <button
                  onClick={() => setSelectedVoice('male')}
                  className={`flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-md text-sm font-medium transition-all ${
                    selectedVoice === 'male'
                      ? 'bg-white/10 text-white border border-white/20'
                      : 'bg-transparent text-white/50 border border-white/[0.06] hover:border-white/10 hover:text-white/70'
                  }`}
                >
                  <User className="w-4 h-4" />
                  Male
                </button>
                <button
                  onClick={() => setSelectedVoice('female')}
                  className={`flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-md text-sm font-medium transition-all ${
                    selectedVoice === 'female'
                      ? 'bg-white/10 text-white border border-white/20'
                      : 'bg-transparent text-white/50 border border-white/[0.06] hover:border-white/10 hover:text-white/70'
                  }`}
                >
                  <User className="w-4 h-4" />
                  Female
                </button>
              </div>
            </div>

            {/* Persona Selection Card */}
            <div className="bg-white/[0.02] border border-white/[0.06] rounded-lg p-4">
              <label className="text-xs font-medium text-white/50 uppercase tracking-wider mb-3 block">
                Style
              </label>
              <div className="relative" ref={dropdownRef}>
                <button
                  onClick={() => setIsPersonaDropdownOpen(!isPersonaDropdownOpen)}
                  className="w-full flex items-center justify-between px-4 py-2.5 rounded-md bg-white/[0.03] border border-white/[0.08] hover:border-white/15 transition-colors"
                >
                  <span className="text-sm text-white">{currentPersona.name}</span>
                  <ChevronDown className={`w-4 h-4 text-white/40 transition-transform ${isPersonaDropdownOpen ? 'rotate-180' : ''}`} />
                </button>
                
                <AnimatePresence>
                  {isPersonaDropdownOpen && (
                    <motion.div
                      initial={{ opacity: 0, y: -8 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -8 }}
                      transition={{ duration: 0.15 }}
                      className="absolute top-full left-0 right-0 mt-1.5 bg-[#1a1a1f] border border-white/[0.08] rounded-md shadow-xl z-50 overflow-hidden"
                    >
                      <div className="max-h-64 overflow-y-auto">
                        {personas.map((persona) => (
                          <button
                            key={persona.id}
                            onClick={() => {
                              setSelectedPersona(persona.id);
                              setIsPersonaDropdownOpen(false);
                            }}
                            className={`w-full px-4 py-2.5 text-left text-sm transition-colors flex items-center justify-between ${
                              selectedPersona === persona.id
                                ? 'bg-white/[0.08] text-white'
                                : 'text-white/70 hover:bg-white/[0.04] hover:text-white'
                            }`}
                          >
                            <div>
                              <div className="font-medium">{persona.name}</div>
                              <div className="text-xs text-white/40 mt-0.5">{persona.description}</div>
                            </div>
                            {selectedPersona === persona.id && (
                              <Check className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                            )}
                          </button>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
              <p className="text-xs text-white/30 mt-2">{currentPersona.description}</p>
            </div>

            {/* Current Selection Summary */}
            <div className="bg-white/[0.02] border border-white/[0.06] rounded-lg p-4">
              <label className="text-xs font-medium text-white/50 uppercase tracking-wider mb-3 block">
                Configuration
              </label>
              <div className="space-y-2 text-sm">
                <div className="flex items-center justify-between py-1.5 border-b border-white/[0.04]">
                  <span className="text-white/40">Voice</span>
                  <span className="text-white/80 capitalize">{selectedVoice}</span>
                </div>
                <div className="flex items-center justify-between py-1.5 border-b border-white/[0.04]">
                  <span className="text-white/40">Style</span>
                  <span className="text-white/80">{currentPersona.name}</span>
                </div>
                <div className="flex items-center justify-between py-1.5">
                  <span className="text-white/40">Words</span>
                  <span className="text-white/80 font-mono">{wordCount}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Script & Player */}
          <div className="lg:col-span-2 space-y-4">
            {/* Script Input */}
            <div className="bg-white/[0.02] border border-white/[0.06] rounded-lg p-5">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2.5">
                  <Mic className="w-4 h-4 text-white/40" />
                  <span className="text-sm font-medium text-white/70">Script</span>
                </div>
                <span className="text-xs text-white/30 font-mono">{wordCount} words</span>
              </div>
              
              <textarea
                value={script}
                onChange={(e) => setScript(e.target.value)}
                placeholder="Enter your script here, or navigate from the Workflow page with a generated script..."
                rows={8}
                className="w-full px-4 py-3 rounded-md bg-black/20 border border-white/[0.06] 
                           text-white/90 placeholder-white/20 text-sm leading-relaxed
                           focus:outline-none focus:border-white/15
                           resize-none transition-colors font-[system-ui]"
              />
              
              <div className="flex items-center justify-end mt-4">
                <button
                  onClick={handleGenerate}
                  disabled={!script.trim() || isGenerating}
                  className={`
                    flex items-center gap-2 px-5 py-2.5 rounded-md text-sm font-medium
                    transition-all duration-200
                    ${script.trim() && !isGenerating
                      ? 'bg-white text-black hover:bg-white/90'
                      : 'bg-white/[0.06] text-white/30 cursor-not-allowed'
                    }
                  `}
                >
                  {isGenerating ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Wand2 className="w-4 h-4" />
                      Generate Audio
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Error Display */}
            <AnimatePresence>
              {generationError && (
                <motion.div
                  initial={{ opacity: 0, y: -8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                >
                  <div className="px-4 py-3 rounded-md bg-red-500/5 border border-red-500/20 flex items-center gap-3">
                    <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
                    <p className="text-sm text-red-400/90">{generationError}</p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Audio Player */}
            <AnimatePresence>
              {audioResult?.success && (
                <motion.div
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 12 }}
                  className="bg-white/[0.02] border border-white/[0.06] rounded-lg overflow-hidden"
                >
                  {/* Success Header */}
                  <div className="px-5 py-3 border-b border-white/[0.04] bg-emerald-500/[0.03]">
                    <div className="flex items-center gap-2 text-emerald-400 text-sm">
                      <Check className="w-4 h-4" />
                      <span>Audio generated successfully</span>
                    </div>
                  </div>

                  <div className="p-5">
                    {/* Waveform Visualization - Minimal Design */}
                    <div 
                      className="flex items-end justify-center gap-[2px] h-16 mb-4 cursor-pointer group"
                      onClick={(e) => {
                        if (!audioRef.current) return;
                        const rect = e.currentTarget.getBoundingClientRect();
                        const x = e.clientX - rect.left;
                        const percent = (x / rect.width) * 100;
                        const newTime = (percent / 100) * audioRef.current.duration;
                        audioRef.current.currentTime = newTime;
                        setProgress(percent);
                      }}
                    >
                      {waveformBars.map((height, i) => {
                        const barProgress = (i / waveformBars.length) * 100;
                        const isActive = barProgress <= progress;
                        
                        return (
                          <div
                            key={i}
                            className={`w-1 rounded-sm transition-all duration-100 ${
                              isActive
                                ? 'bg-white/80'
                                : 'bg-white/15 group-hover:bg-white/20'
                            }`}
                            style={{ height: `${height}%` }}
                          />
                        );
                      })}
                    </div>

                    {/* Progress Bar */}
                    <div className="relative h-1 bg-white/[0.08] rounded-full mb-4 group cursor-pointer">
                      <div
                        className="absolute inset-y-0 left-0 bg-white/60 rounded-full transition-all"
                        style={{ width: `${progress}%` }}
                      />
                      <div 
                        className="absolute top-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full shadow opacity-0 group-hover:opacity-100 transition-opacity"
                        style={{ left: `calc(${progress}% - 6px)` }}
                      />
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={progress}
                        onChange={handleSeek}
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                      />
                    </div>

                    {/* Time Display */}
                    <div className="flex justify-between text-xs text-white/40 mb-5 font-mono">
                      <span>{formatTime(currentTime)}</span>
                      <span>{formatTime(duration)}</span>
                    </div>

                    {/* Controls */}
                    <div className="flex items-center justify-between">
                      {/* Volume Control */}
                      <div className="flex items-center gap-2 w-28">
                        <button
                          onClick={toggleMute}
                          className="p-1.5 rounded hover:bg-white/[0.06] transition-colors"
                        >
                          {isMuted || volume === 0 ? (
                            <VolumeX className="w-4 h-4 text-white/50" />
                          ) : (
                            <Volume2 className="w-4 h-4 text-white/50" />
                          )}
                        </button>
                        <div className="flex-1 relative h-1 bg-white/[0.08] rounded-full">
                          <div 
                            className="absolute inset-y-0 left-0 bg-white/40 rounded-full"
                            style={{ width: `${isMuted ? 0 : volume * 100}%` }}
                          />
                          <input
                            type="range"
                            min="0"
                            max="100"
                            value={isMuted ? 0 : volume * 100}
                            onChange={handleVolumeChange}
                            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                          />
                        </div>
                      </div>

                      {/* Play Controls */}
                      <div className="flex items-center gap-3">
                        <button
                          onClick={skipBackward}
                          className="p-1.5 rounded hover:bg-white/[0.06] transition-colors"
                          title="Skip back 10s"
                        >
                          <SkipBack className="w-4 h-4 text-white/60" />
                        </button>
                        
                        <button
                          onClick={togglePlay}
                          className="w-10 h-10 rounded-full bg-white flex items-center justify-center hover:bg-white/90 transition-colors"
                        >
                          {isPlaying ? (
                            <Pause className="w-5 h-5 text-black" />
                          ) : (
                            <Play className="w-5 h-5 text-black ml-0.5" />
                          )}
                        </button>
                        
                        <button
                          onClick={skipForward}
                          className="p-1.5 rounded hover:bg-white/[0.06] transition-colors"
                          title="Skip forward 10s"
                        >
                          <SkipForward className="w-4 h-4 text-white/60" />
                        </button>
                      </div>

                      {/* Download Button */}
                      <div className="w-28 flex justify-end">
                        <button
                          onClick={handleDownload}
                          disabled={isDownloading}
                          className="flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium text-white/60 hover:text-white hover:bg-white/[0.06] transition-colors"
                        >
                          {isDownloading ? (
                            <Loader2 className="w-3.5 h-3.5 animate-spin" />
                          ) : (
                            <Download className="w-3.5 h-3.5" />
                          )}
                          <span>Download</span>
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Metadata Footer */}
                  <div className="px-5 py-3 border-t border-white/[0.04] bg-white/[0.01]">
                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-4 text-white/40">
                        <span>Style: <span className="text-white/60">{audioResult.persona_name || currentPersona.name}</span></span>
                        <span>Voice: <span className="text-white/60 capitalize">{audioResult.voice}</span></span>
                        {audioResult?.chunks_processed && audioResult.chunks_processed > 1 && (
                          <span>Parts: <span className="text-white/60">{audioResult.chunks_processed}</span></span>
                        )}
                      </div>
                      <span className="text-white/40 font-mono">{formatTime(duration)}</span>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Regenerate Button */}
            {audioResult?.success && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.15 }}
                className="flex justify-end"
              >
                <button 
                  onClick={handleGenerate}
                  className="flex items-center gap-2 px-3 py-1.5 rounded text-xs font-medium text-white/50 hover:text-white/80 hover:bg-white/[0.04] transition-colors"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  Regenerate
                </button>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
