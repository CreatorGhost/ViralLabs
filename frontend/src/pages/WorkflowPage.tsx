import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Search, 
  X, 
  FileText, 
  Check, 
  ChevronDown,
  RefreshCw, 
  RotateCcw, 
  Wand2, 
  Image, 
  Zap,
  Settings2,
  Square,
  Volume2,
  Download,
  Copy,
  AlertCircle,
  Trash2,
  Maximize2,
  Clock,
  Eye,
  Loader2,
  Play,
} from 'lucide-react';
import { useStreamingWorkflow } from '../hooks/useStreamingWorkflow';
import { searchVideos } from '../api/client';
import { getSessionId, API_BASE } from '../config';
import type { 
  WorkflowMode, 
  QualityPreset, 
  QuickModeSettings,
  StudioModeSettings,
  VideoItem,
  StreamingThumbnail,
} from '../types';

// Storage key for persisting results
const STORAGE_KEY = 'virallab_workflow_results';

// Saved results interface
interface SavedResults {
  query: string;
  script: string;
  thumbnails: StreamingThumbnail[];
  videosAnalyzed: number;
  refinedQuery: string;
  savedAt: number;
}

// Re-export constants that we need
const QUALITY_PRESETS_DATA: Record<QualityPreset, { videos: number; description: string; time: string }> = {
  fast: { videos: 3, description: 'Quick results', time: '~2 min' },
  balanced: { videos: 5, description: 'Best balance', time: '~3 min' },
  thorough: { videos: 10, description: 'Deep analysis', time: '~5 min' },
};

const WORKFLOW_STEPS_DATA = [
  { name: 'refining' as const, label: 'Refining', description: 'Optimizing query' },
  { name: 'searching' as const, label: 'Searching', description: 'Finding videos' },
  { name: 'ranking' as const, label: 'Ranking', description: 'Selecting best' },
  { name: 'transcripts' as const, label: 'Transcripts', description: 'Extracting content' },
  { name: 'generating' as const, label: 'Writing', description: 'Creating script' },
  { name: 'thumbnails' as const, label: 'Thumbnails', description: 'Generating visuals' },
];

// Example topics that rotate in placeholder
const EXAMPLE_TOPICS = [
  'Best AI coding tools in 2025',
  'How to learn programming fast',
  'Top productivity tips for creators',
  'Side hustle ideas that actually work',
];

// Load saved results from localStorage
const loadSavedResults = (): SavedResults | null => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      const parsed = JSON.parse(saved) as SavedResults;
      // Check if results are less than 24 hours old
      if (Date.now() - parsed.savedAt < 24 * 60 * 60 * 1000) {
        return parsed;
      }
    }
  } catch (e) {
    console.error('Failed to load saved results:', e);
  }
  return null;
};

// Save results to localStorage
const saveResults = (results: SavedResults) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(results));
  } catch (e) {
    console.error('Failed to save results:', e);
  }
};

// Clear saved results
const clearSavedResults = () => {
  localStorage.removeItem(STORAGE_KEY);
};

interface WorkflowPageProps {
  onGenerateAudio?: (script: string) => void;
  includeFace?: boolean; // Passed from Dashboard - global face state
}

export default function WorkflowPage({ onGenerateAudio, includeFace = false }: WorkflowPageProps) {
  // Core state
  const [query, setQuery] = useState('');
  const [mode, setMode] = useState<WorkflowMode>('quick');
  const [placeholderIndex, setPlaceholderIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const scriptContainerRef = useRef<HTMLDivElement>(null);
  const sessionId = getSessionId();

  // Persisted results state (survives refresh)
  const [savedResults, setSavedResults] = useState<SavedResults | null>(null);

  // Quick mode settings
  const [quickSettings, setQuickSettings] = useState<QuickModeSettings>({
    includeThumbnails: true,
    quality: 'balanced',
  });

  // Studio mode state
  const [studioStep, setStudioStep] = useState<'search' | 'select' | 'configure'>('search');
  const [searchedVideos, setSearchedVideos] = useState<VideoItem[]>([]);
  const [selectedVideoIds, setSelectedVideoIds] = useState<string[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [refinedQuery, setRefinedQuery] = useState<string | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [studioSettings, setStudioSettings] = useState<StudioModeSettings>({
    model: 'gpt-4o',
    refine_model: 'gpt-4o-mini',
    temperature: 0.7,
    max_videos: 15,
    top_n_videos: 5,
    subscriber_threshold: 50000,
    max_workers: 5,
    enable_thumbnails: true,
    num_thumbnails: 3,
    resolution: '1K',
    use_reference_images: false,
    include_face: false,
    face_mode: 'auto',
    face_style: 'realistic',
  });

  // Copy feedback
  const [copied, setCopied] = useState(false);

  // Thumbnail gallery state
  const [selectedThumbnail, setSelectedThumbnail] = useState<number | null>(null);
  const [zoomedThumbnail, setZoomedThumbnail] = useState<{ url: string; index: number } | null>(null);

  // Streaming workflow hook
  const {
    startGeneration,
    stopGeneration,
    progress,
    script,
    thumbnails,
    error,
    isGenerating,
    isComplete,
    refinedQuery: streamRefinedQuery,
    videosAnalyzed,
    resetState,
  } = useStreamingWorkflow();

  // Load saved results on mount
  useEffect(() => {
    const saved = loadSavedResults();
    if (saved) {
      setSavedResults(saved);
      setQuery(saved.query);
    }
  }, []);

  // Save results when generation completes
  useEffect(() => {
    if (isComplete && script) {
      const results: SavedResults = {
        query,
        script,
        thumbnails,
        videosAnalyzed,
        refinedQuery: streamRefinedQuery,
        savedAt: Date.now(),
      };
      saveResults(results);
      setSavedResults(results);
    }
  }, [isComplete, script, thumbnails, videosAnalyzed, streamRefinedQuery, query]);

  // Auto-scroll script container during streaming
  useEffect(() => {
    if (scriptContainerRef.current && isGenerating) {
      scriptContainerRef.current.scrollTop = scriptContainerRef.current.scrollHeight;
    }
  }, [script, isGenerating]);

  // Rotate placeholder text
  useEffect(() => {
    const interval = setInterval(() => {
      setPlaceholderIndex((prev) => (prev + 1) % EXAMPLE_TOPICS.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  // Calculate estimated time based on settings
  const getEstimatedTime = useCallback(() => {
    if (mode === 'quick') {
      return quickSettings.includeThumbnails 
        ? QUALITY_PRESETS_DATA[quickSettings.quality].time.replace('~', '~') + ' + 1min'
        : QUALITY_PRESETS_DATA[quickSettings.quality].time;
    }
    return studioSettings.enable_thumbnails ? '~4-6 min' : '~3-4 min';
  }, [mode, quickSettings, studioSettings]);

  // Handle search in studio mode
  const handleStudioSearch = async () => {
    if (!query.trim()) return;
    setIsSearching(true);
    try {
      const response = await searchVideos({
        topic: query.trim(),
        max_videos: studioSettings.max_videos,
        subscriber_threshold: studioSettings.subscriber_threshold,
        refine_model: studioSettings.refine_model,
      }, sessionId);
      
      if (response.success && response.videos) {
        setSearchedVideos(response.videos);
        setRefinedQuery(response.refined_query || null);
        // Auto-select top 5 videos
        const topVideos = response.videos.slice(0, 5).map(v => v.video_id);
        setSelectedVideoIds(topVideos);
        setStudioStep('select');
      }
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setIsSearching(false);
    }
  };

  // Handle generation (both modes)
  const handleGenerate = () => {
    if (!query.trim()) return;
    
    // Clear saved results when starting new generation
    setSavedResults(null);
    clearSavedResults();
    
    if (mode === 'quick') {
      // Quick mode - AI picks videos automatically
      const videosToAnalyze = QUALITY_PRESETS_DATA[quickSettings.quality].videos;
      startGeneration({
        topic: query.trim(),
        top_n_videos: videosToAnalyze,
        max_videos: videosToAnalyze * 2,
        enable_thumbnails: quickSettings.includeThumbnails,
        num_thumbnails: 3,
        // Face inclusion is controlled globally from Dashboard
        include_face: includeFace,
      }, sessionId);
    } else {
      // Studio mode - use selected videos
      if (selectedVideoIds.length === 0) return;
      startGeneration({
        topic: query.trim(),
        selected_video_ids: selectedVideoIds,
        model: studioSettings.model,
        temperature: studioSettings.temperature,
        enable_thumbnails: studioSettings.enable_thumbnails,
        num_thumbnails: studioSettings.num_thumbnails,
        resolution: studioSettings.resolution,
        // Face inclusion is controlled globally from Dashboard
        include_face: includeFace,
        face_mode: studioSettings.face_mode,
        face_style: studioSettings.face_style,
      }, sessionId);
    }
  };

  // Reset everything
  const handleReset = () => {
    setQuery('');
    setSearchedVideos([]);
    setSelectedVideoIds([]);
    setStudioStep('search');
    setRefinedQuery(null);
    setSavedResults(null);
    clearSavedResults();
    resetState();
    inputRef.current?.focus();
  };

  // Toggle video selection
  const toggleVideoSelection = (videoId: string) => {
    setSelectedVideoIds(prev => 
      prev.includes(videoId) 
        ? prev.filter(id => id !== videoId)
        : [...prev, videoId]
    );
  };

  // Copy script to clipboard
  const copyScript = () => {
    const textToCopy = savedResults?.script || script;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Get current step index for progress
  const getCurrentStepIndex = (): number => {
    const stepIndex = WORKFLOW_STEPS_DATA.findIndex(s => s.name === progress.currentStep);
    return stepIndex >= 0 ? stepIndex : 0;
  };

  // Get display data (from streaming or saved results)
  const displayScript = isGenerating ? script : (savedResults?.script || script);
  const displayThumbnails = isGenerating ? thumbnails : (savedResults?.thumbnails || thumbnails);
  const displayVideosAnalyzed = savedResults?.videosAnalyzed || videosAnalyzed;
  const displayQuery = savedResults?.query || query;

  // Check if we have any valid results to show
  const hasValidResults = Boolean(
    savedResults?.script || 
    (isComplete && script) || 
    (script && script.length > 100) // If we have substantial script content
  );

  // Determine what to show - more robust logic to prevent blank page
  const showGenerating = isGenerating;
  const showResults = !isGenerating && hasValidResults;
  const showInput = !isGenerating && !hasValidResults;

  return (
    <div className="min-h-[calc(100vh-120px)] px-4 sm:px-6 lg:px-8 py-8">
      <AnimatePresence mode="wait">
        {/* ============================================ */}
        {/* INPUT STATE - Show when not generating */}
        {/* ============================================ */}
        {showInput && !showResults && (
          <motion.div
            key="input"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
            className="max-w-4xl mx-auto"
          >
            {/* Page Header */}
            <div className="text-center mb-8">
              <h1 className="text-2xl font-semibold text-white tracking-tight mb-2">
                Content Generator
              </h1>
              <p className="text-sm text-white/40">
                Create viral scripts and thumbnails from trending content
              </p>
            </div>

            {/* Mode Selector - Clean Toggle */}
            <div className="flex items-center justify-center mb-8">
              <div className="inline-flex items-center p-1 rounded-lg bg-white/[0.03] border border-white/[0.06]">
                <button
                  onClick={() => setMode('quick')}
                  className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                    mode === 'quick' 
                      ? 'bg-white/10 text-white' 
                      : 'text-white/50 hover:text-white/70'
                  }`}
                >
                  <Zap className="w-4 h-4" />
                  Quick Mode
                </button>
                <button
                  onClick={() => setMode('studio')}
                  className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                    mode === 'studio' 
                      ? 'bg-white/10 text-white' 
                      : 'text-white/50 hover:text-white/70'
                  }`}
                >
                  <Settings2 className="w-4 h-4" />
                  Studio Mode
                </button>
              </div>
            </div>

            {/* Search Input Card */}
            <div className="bg-white/[0.02] border border-white/[0.06] rounded-lg p-6 mb-6">
              <label className="text-xs font-medium text-white/50 uppercase tracking-wider mb-3 block">
                Topic or Idea
              </label>
              <div className="relative">
                <div className="flex items-center gap-3">
                  <Search className="w-5 h-5 text-white/30 flex-shrink-0" />
                  <input
                    ref={inputRef}
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        if (mode === 'quick') {
                          handleGenerate();
                        } else if (studioStep === 'search') {
                          handleStudioSearch();
                        } else {
                          handleGenerate();
                        }
                      }
                    }}
                    placeholder={EXAMPLE_TOPICS[placeholderIndex]}
                    className="flex-1 py-3 bg-transparent text-white text-base placeholder-white/25 focus:outline-none"
                  />
                  {query && (
                    <button 
                      onClick={() => setQuery('')}
                      className="p-1.5 text-white/30 hover:text-white/60 transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>
                <div className="absolute bottom-0 left-0 right-0 h-px bg-white/[0.08]" />
              </div>
              
              {/* Quick suggestions */}
              <div className="flex flex-wrap items-center gap-2 mt-4">
                <span className="text-xs text-white/30">Suggestions:</span>
                {['Tech Review', 'Tutorial', 'Product Launch', 'Vlog', 'Educational'].map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => setQuery(suggestion)}
                    className="px-3 py-1 rounded text-xs text-white/40 hover:text-white/70 bg-white/[0.02] hover:bg-white/[0.05] border border-white/[0.04] transition-colors"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>

            {/* Mode-specific Options */}
            <AnimatePresence mode="wait">
              {mode === 'quick' ? (
                <motion.div
                  key="quick-options"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="w-full"
                >
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                    {/* Output Type */}
                    <div className="bg-white/[0.02] border border-white/[0.06] rounded-lg p-4">
                      <label className="text-xs font-medium text-white/50 uppercase tracking-wider mb-3 block">
                        Output
                      </label>
                      <div className="flex gap-2">
                        <button
                          onClick={() => setQuickSettings(s => ({ ...s, includeThumbnails: false }))}
                          className={`flex-1 p-3 rounded-md border transition-all text-center ${
                            !quickSettings.includeThumbnails 
                              ? 'bg-white/10 border-white/20 text-white' 
                              : 'bg-transparent border-white/[0.06] text-white/50 hover:border-white/10'
                          }`}
                        >
                          <FileText className="w-5 h-5 mx-auto mb-1.5" />
                          <div className="text-xs font-medium">Script Only</div>
                        </button>
                        <button
                          onClick={() => setQuickSettings(s => ({ ...s, includeThumbnails: true }))}
                          className={`flex-1 p-3 rounded-md border transition-all text-center ${
                            quickSettings.includeThumbnails 
                              ? 'bg-white/10 border-white/20 text-white' 
                              : 'bg-transparent border-white/[0.06] text-white/50 hover:border-white/10'
                          }`}
                        >
                          <div className="flex items-center justify-center gap-1 mb-1.5">
                            <FileText className="w-4 h-4" />
                            <span className="text-white/30">+</span>
                            <Image className="w-4 h-4" />
                          </div>
                          <div className="text-xs font-medium">+ Thumbnails</div>
                        </button>
                      </div>
                    </div>

                    {/* Analysis Depth */}
                    <div className="bg-white/[0.02] border border-white/[0.06] rounded-lg p-4">
                      <label className="text-xs font-medium text-white/50 uppercase tracking-wider mb-3 block">
                        Analysis Depth
                      </label>
                      <div className="flex gap-2">
                        {(['fast', 'balanced', 'thorough'] as QualityPreset[]).map((preset) => (
                          <button
                            key={preset}
                            onClick={() => setQuickSettings(s => ({ ...s, quality: preset }))}
                            className={`flex-1 py-2 px-2 rounded-md border transition-all text-center ${
                              quickSettings.quality === preset
                                ? 'bg-white/10 border-white/20 text-white'
                                : 'bg-transparent border-white/[0.06] text-white/50 hover:border-white/10'
                            }`}
                          >
                            <div className="text-xs font-medium capitalize">{preset}</div>
                            <div className="text-[10px] text-white/40 mt-0.5">
                              {QUALITY_PRESETS_DATA[preset].videos} videos
                            </div>
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>


                  {/* Generate Button & Time Estimate */}
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-white/40">
                      Est. time: {getEstimatedTime()}
                    </span>
                    <button
                      onClick={handleGenerate}
                      disabled={!query.trim() || isSearching}
                      className={`flex items-center gap-2 px-5 py-2.5 rounded-md text-sm font-medium transition-all ${
                        query.trim() && !isSearching
                          ? 'bg-white text-black hover:bg-white/90'
                          : 'bg-white/[0.06] text-white/30 cursor-not-allowed'
                      }`}
                    >
                      {isSearching ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          Processing...
                        </>
                      ) : (
                        <>
                          <Wand2 className="w-4 h-4" />
                          Generate Content
                        </>
                      )}
                    </button>
                  </div>
                </motion.div>
              ) : (
                <motion.div
                  key="studio-options"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="w-full"
                >
                  {/* Search step */}
                  {studioStep === 'search' && (
                    <div className="flex items-center justify-end">
                      <button
                        onClick={handleStudioSearch}
                        disabled={!query.trim() || isSearching}
                        className={`flex items-center gap-2 px-5 py-2.5 rounded-md text-sm font-medium transition-all ${
                          query.trim() && !isSearching
                            ? 'bg-white text-black hover:bg-white/90'
                            : 'bg-white/[0.06] text-white/30 cursor-not-allowed'
                        }`}
                      >
                        {isSearching ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            Searching...
                          </>
                        ) : (
                          <>
                            <Search className="w-4 h-4" />
                            Search Videos
                          </>
                        )}
                      </button>
                    </div>
                  )}

                  {/* Video Selection (shown after search) */}
                  {studioStep === 'select' && searchedVideos.length > 0 && (
                    <div className="bg-white/[0.02] border border-white/[0.06] rounded-lg p-5">
                      {/* Header */}
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <h3 className="font-medium text-white text-sm">Select Reference Videos</h3>
                          {refinedQuery && (
                            <p className="text-xs text-white/40 mt-1">
                              Refined query: {refinedQuery}
                            </p>
                          )}
                        </div>
                        <div className="flex items-center gap-3 text-xs">
                          <button
                            onClick={() => setSelectedVideoIds(searchedVideos.map(v => v.video_id))}
                            className="text-white/50 hover:text-white transition-colors"
                          >
                            Select All
                          </button>
                          <span className="text-white/20">|</span>
                          <button
                            onClick={() => setSelectedVideoIds([])}
                            className="text-white/40 hover:text-white/60 transition-colors"
                          >
                            Clear
                          </button>
                        </div>
                      </div>

                      {/* Video Grid */}
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-3 max-h-[280px] overflow-y-auto pr-1">
                        {searchedVideos.map((video) => (
                          <button
                            key={video.video_id}
                            onClick={() => toggleVideoSelection(video.video_id)}
                            className={`relative p-2.5 rounded-md border text-left transition-all ${
                              selectedVideoIds.includes(video.video_id)
                                ? 'bg-white/10 border-white/20'
                                : 'bg-white/[0.02] border-white/[0.06] hover:border-white/10'
                            }`}
                          >
                            {/* Thumbnail */}
                            <div className="relative aspect-video rounded overflow-hidden mb-2 bg-black/20">
                              <img 
                                src={video.thumbnail_url} 
                                alt={video.title}
                                className="w-full h-full object-cover"
                              />
                              {selectedVideoIds.includes(video.video_id) && (
                                <div className="absolute top-2 right-2 w-5 h-5 rounded-full bg-white flex items-center justify-center">
                                  <Check className="w-3 h-3 text-black" />
                                </div>
                              )}
                            </div>
                            {/* Info */}
                            <p className="text-xs font-medium text-white/80 line-clamp-2 mb-0.5">{video.title}</p>
                            <p className="text-[10px] text-white/40">{video.channel} • {(video.views / 1000000).toFixed(1)}M views</p>
                          </button>
                        ))}
                      </div>

                      {/* Footer */}
                      <div className="flex items-center justify-between mt-4 pt-4 border-t border-white/[0.06]">
                        <div className="flex items-center gap-4">
                          <span className="text-xs text-white/50">
                            {selectedVideoIds.length} selected
                          </span>
                          <button
                            onClick={() => setStudioStep('search')}
                            className="text-xs text-white/40 hover:text-white/60 transition-colors"
                          >
                            ← Change search
                          </button>
                        </div>
                        <button
                          onClick={handleGenerate}
                          disabled={selectedVideoIds.length === 0}
                          className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                            selectedVideoIds.length > 0
                              ? 'bg-white text-black hover:bg-white/90'
                              : 'bg-white/[0.06] text-white/30 cursor-not-allowed'
                          }`}
                        >
                          <Wand2 className="w-4 h-4" />
                          Generate
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Advanced Settings Toggle */}
                  {studioStep !== 'search' && (
                    <div className="mt-4">
                      <button
                        onClick={() => setShowAdvanced(!showAdvanced)}
                        className="flex items-center gap-2 text-xs text-white/40 hover:text-white/60 transition-colors"
                      >
                        <ChevronDown className={`w-3.5 h-3.5 transition-transform ${showAdvanced ? 'rotate-180' : ''}`} />
                        Advanced Settings
                      </button>
                      
                      <AnimatePresence>
                        {showAdvanced && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            className="mt-3"
                          >
                            <div className="bg-white/[0.02] border border-white/[0.06] rounded-lg p-4">
                              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                                {/* Model */}
                                <div>
                                  <label className="text-[10px] text-white/40 uppercase tracking-wider mb-1.5 block">Model</label>
                                  <select
                                    value={studioSettings.model}
                                    onChange={(e) => setStudioSettings(s => ({ ...s, model: e.target.value }))}
                                    className="w-full px-3 py-2 rounded-md bg-black/20 border border-white/[0.08] text-sm text-white/80 focus:outline-none focus:border-white/20"
                                  >
                                    <option value="gpt-4o">GPT-4o</option>
                                    <option value="gpt-4o-mini">GPT-4o Mini</option>
                                    <option value="claude-3-5-sonnet">Claude 3.5 Sonnet</option>
                                  </select>
                                </div>

                                {/* Temperature */}
                                <div>
                                  <label className="text-[10px] text-white/40 uppercase tracking-wider mb-1.5 block">
                                    Temperature: {studioSettings.temperature}
                                  </label>
                                  <input
                                    type="range"
                                    min="0"
                                    max="1"
                                    step="0.1"
                                    value={studioSettings.temperature}
                                    onChange={(e) => setStudioSettings(s => ({ ...s, temperature: parseFloat(e.target.value) }))}
                                    className="w-full accent-white/60"
                                  />
                                </div>

                                {/* Thumbnails */}
                                <div>
                                  <label className="text-[10px] text-white/40 uppercase tracking-wider mb-1.5 block">Thumbnails</label>
                                  <div className="flex items-center gap-2">
                                    <button
                                      onClick={() => setStudioSettings(s => ({ ...s, enable_thumbnails: !s.enable_thumbnails }))}
                                      className={`px-3 py-1.5 rounded-md text-xs transition-all ${
                                        studioSettings.enable_thumbnails
                                          ? 'bg-white/10 border border-white/20 text-white'
                                          : 'bg-transparent border border-white/[0.08] text-white/50'
                                      }`}
                                    >
                                      {studioSettings.enable_thumbnails ? 'On' : 'Off'}
                                    </button>
                                    {studioSettings.enable_thumbnails && (
                                      <select
                                        value={studioSettings.num_thumbnails}
                                        onChange={(e) => setStudioSettings(s => ({ ...s, num_thumbnails: parseInt(e.target.value) }))}
                                        className="px-2 py-1.5 rounded-md bg-black/20 border border-white/[0.08] text-xs text-white/70"
                                      >
                                        <option value="1">1</option>
                                        <option value="2">2</option>
                                        <option value="3">3</option>
                                        <option value="4">4</option>
                                      </select>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}

        {/* ============================================ */}
        {/* GENERATING STATE */}
        {/* ============================================ */}
        {showGenerating && (
          <motion.div
            key="generating"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
            className="max-w-4xl mx-auto"
          >
            {/* Header with Query and Stop */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-white/[0.05] flex items-center justify-center">
                  <Loader2 className="w-4 h-4 text-white/60 animate-spin" />
                </div>
                <div>
                  <h2 className="text-sm font-medium text-white">Generating Content</h2>
                  <p className="text-xs text-white/40 truncate max-w-md">{query}</p>
                </div>
              </div>
              <button
                onClick={stopGeneration}
                className="flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium text-red-400 hover:text-red-300 bg-red-500/10 hover:bg-red-500/15 border border-red-500/20 transition-colors"
              >
                <Square className="w-3.5 h-3.5" />
                Stop
              </button>
            </div>

            {/* Progress Steps */}
            <div className="bg-white/[0.02] border border-white/[0.06] rounded-lg p-5 mb-4">
              <div className="flex items-center justify-between mb-4">
                {WORKFLOW_STEPS_DATA.map((step, index) => {
                  const currentIndex = getCurrentStepIndex();
                  const isActive = step.name === progress.currentStep;
                  const isComplete = index < currentIndex || progress.currentStep === 'complete';

                  return (
                    <React.Fragment key={step.name}>
                      <div className="flex flex-col items-center">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center transition-all ${
                          isComplete ? 'bg-emerald-500/20 border border-emerald-500/40' :
                          isActive ? 'bg-white/10 border border-white/20' :
                          'bg-white/[0.03] border border-white/[0.08]'
                        }`}>
                          {isComplete ? (
                            <Check className="w-4 h-4 text-emerald-400" />
                          ) : isActive ? (
                            <Loader2 className="w-4 h-4 text-white/70 animate-spin" />
                          ) : (
                            <div className="w-1.5 h-1.5 rounded-full bg-white/20" />
                          )}
                        </div>
                        <span className={`text-[10px] mt-1.5 ${
                          isActive ? 'text-white/80' : isComplete ? 'text-white/50' : 'text-white/25'
                        }`}>
                          {step.label}
                        </span>
                      </div>
                      {index < WORKFLOW_STEPS_DATA.length - 1 && (
                        <div className={`flex-1 h-px mx-2 ${
                          isComplete ? 'bg-emerald-500/40' : 'bg-white/[0.08]'
                        }`} />
                      )}
                    </React.Fragment>
                  );
                })}
              </div>
              <div className="text-center text-xs text-white/40">
                {progress.message || 'Initializing...'}
              </div>
            </div>

            {/* Live Script Preview */}
            {script && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white/[0.02] border border-white/[0.06] rounded-lg overflow-hidden mb-4"
              >
                <div className="flex items-center justify-between px-5 py-3 border-b border-white/[0.04]">
                  <div className="flex items-center gap-2.5">
                    <FileText className="w-4 h-4 text-white/40" />
                    <span className="text-sm font-medium text-white/70">Script Preview</span>
                    <span className="text-xs text-white/30">
                      {script.split(/\s+/).filter(w => w).length} words
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                    <span className="text-[10px] text-emerald-400/70 uppercase tracking-wider">Live</span>
                  </div>
                </div>
                
                <div 
                  ref={scriptContainerRef}
                  className="max-h-[200px] overflow-y-auto p-5"
                >
                  <div className="text-sm text-white/60 leading-relaxed whitespace-pre-wrap">
                    {script}
                    <span className="inline-block w-0.5 h-4 bg-white/50 ml-0.5 align-middle animate-pulse" />
                  </div>
                </div>
              </motion.div>
            )}

            {/* Live Thumbnails */}
            {thumbnails.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white/[0.02] border border-white/[0.06] rounded-lg p-5"
              >
                <div className="flex items-center gap-2.5 mb-4">
                  <Image className="w-4 h-4 text-white/40" />
                  <span className="text-sm font-medium text-white/70">Thumbnails</span>
                  <span className="text-xs text-white/30">{thumbnails.length} generated</span>
                </div>
                <div className="grid grid-cols-3 gap-3">
                  {thumbnails.map((thumb, i) => (
                    <div
                      key={i}
                      className="aspect-video rounded-md overflow-hidden bg-black/20"
                    >
                      <img 
                        src={`${API_BASE}${thumb.url}`} 
                        alt={`Thumbnail ${i + 1}`}
                        className="w-full h-full object-cover"
                      />
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </motion.div>
        )}

        {/* ============================================ */}
        {/* RESULTS STATE (including persisted results) */}
        {/* ============================================ */}
        {showResults && !showGenerating && (
          <motion.div
            key="results"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="max-w-5xl mx-auto pb-28"
          >
            {/* Thumbnail Zoom Modal */}
            <AnimatePresence>
              {zoomedThumbnail && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="fixed inset-0 z-[100] flex items-center justify-center p-6"
                  onClick={() => setZoomedThumbnail(null)}
                >
                  <div className="fixed inset-0 bg-black/90" />
                  
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    onClick={(e) => e.stopPropagation()}
                    className="relative z-10 w-full max-w-4xl"
                  >
                    <div className="bg-[#0f1015] border border-white/[0.08] rounded-lg overflow-hidden">
                      {/* Header */}
                      <div className="flex items-center justify-between px-5 py-4 border-b border-white/[0.06]">
                        <div>
                          <h3 className="font-medium text-white">Thumbnail {zoomedThumbnail.index + 1}</h3>
                          <p className="text-xs text-white/40">High resolution preview</p>
                        </div>
                        <button
                          onClick={() => setZoomedThumbnail(null)}
                          className="p-2 rounded-md hover:bg-white/[0.05] text-white/50 hover:text-white/80 transition-colors"
                        >
                          <X className="w-5 h-5" />
                        </button>
                      </div>
                      
                      {/* Image */}
                      <div className="p-4">
                        <img 
                          src={`${API_BASE}${zoomedThumbnail.url}`} 
                          alt={`Thumbnail ${zoomedThumbnail.index + 1}`}
                          className="w-full h-auto rounded"
                        />
                      </div>
                      
                      {/* Footer */}
                      <div className="flex items-center justify-between px-5 py-4 border-t border-white/[0.06]">
                        <p className="text-xs text-white/30">Click outside to close</p>
                        <a
                          href={`${API_BASE}${zoomedThumbnail.url}`}
                          download={`thumbnail_${zoomedThumbnail.index + 1}.png`}
                          className="flex items-center gap-2 px-4 py-2 rounded-md bg-white text-black text-sm font-medium hover:bg-white/90 transition-colors"
                        >
                          <Download className="w-4 h-4" />
                          Download
                        </a>
                      </div>
                    </div>
                  </motion.div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Success Header */}
            <div className="mb-8">
              <div className="flex items-center gap-2 mb-3">
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs">
                  <Check className="w-3.5 h-3.5" />
                  {savedResults && !isComplete ? 'Previous Generation' : 'Complete'}
                </div>
              </div>
              <h2 className="text-xl font-semibold text-white mb-2">
                {displayQuery}
              </h2>
              <div className="flex items-center gap-4 text-xs text-white/40">
                <span className="flex items-center gap-1.5">
                  <FileText className="w-3.5 h-3.5" />
                  {displayScript.split(/\s+/).filter(w => w).length} words
                </span>
                <span className="flex items-center gap-1.5">
                  <Eye className="w-3.5 h-3.5" />
                  {displayVideosAnalyzed} videos analyzed
                </span>
                {displayThumbnails.length > 0 && (
                  <span className="flex items-center gap-1.5">
                    <Image className="w-3.5 h-3.5" />
                    {displayThumbnails.length} thumbnails
                  </span>
                )}
              </div>
            </div>

            {/* Script Section */}
            <div className="bg-white/[0.02] border border-white/[0.06] rounded-lg overflow-hidden mb-6">
              {/* Header */}
              <div className="flex items-center justify-between px-5 py-4 border-b border-white/[0.04]">
                <div className="flex items-center gap-3">
                  <FileText className="w-4 h-4 text-white/40" />
                  <div>
                    <h3 className="text-sm font-medium text-white">Script</h3>
                    <div className="flex items-center gap-2 text-xs text-white/40">
                      <span>{displayScript.split(/\s+/).filter(w => w).length} words</span>
                      <span>•</span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        ~{Math.round(displayScript.split(/\s+/).filter(w => w).length / 150)} min read
                      </span>
                    </div>
                  </div>
                </div>
                <button
                  onClick={copyScript}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                    copied 
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' 
                      : 'text-white/50 hover:text-white hover:bg-white/[0.05]'
                  }`}
                >
                  {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                  {copied ? 'Copied' : 'Copy'}
                </button>
              </div>
              
              {/* Script Content */}
              <div className="relative">
                <div className="max-h-[400px] overflow-y-auto p-5 text-sm text-white/70 leading-relaxed whitespace-pre-wrap">
                  {displayScript}
                </div>
              </div>
            </div>

            {/* Thumbnails Section */}
            {displayThumbnails.length > 0 && (
              <div className="mb-6">
                {/* Section Header */}
                <div className="flex items-center gap-2.5 mb-4">
                  <Image className="w-4 h-4 text-white/40" />
                  <h3 className="text-sm font-medium text-white">Thumbnails</h3>
                  <span className="text-xs text-white/30">{displayThumbnails.length} generated</span>
                </div>
                
                {/* Thumbnail Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {displayThumbnails.map((thumb, i) => (
                    <div
                      key={i}
                      className="relative group cursor-pointer"
                      onClick={() => setSelectedThumbnail(selectedThumbnail === i ? null : i)}
                    >
                      <div className={`relative aspect-video rounded-md overflow-hidden border transition-all ${
                        selectedThumbnail === i 
                          ? 'border-white/30' 
                          : 'border-white/[0.06] hover:border-white/15'
                      }`}>
                        <img 
                          src={`${API_BASE}${thumb.url}`} 
                          alt={`Thumbnail ${i + 1}`}
                          className="w-full h-full object-cover"
                        />
                        
                        {/* Number badge */}
                        <div className="absolute top-2 left-2 px-2 py-0.5 rounded text-[10px] font-medium text-white/70 bg-black/60">
                          #{i + 1}
                        </div>
                        
                        {/* Hover Actions */}
                        <div className="absolute inset-0 flex items-center justify-center gap-2 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setZoomedThumbnail({ url: thumb.url, index: i });
                            }}
                            className="w-9 h-9 rounded-md bg-white/10 hover:bg-white/20 flex items-center justify-center text-white transition-colors"
                          >
                            <Maximize2 className="w-4 h-4" />
                          </button>
                          <a
                            href={`${API_BASE}${thumb.url}`}
                            download={`thumbnail_${i + 1}.png`}
                            onClick={(e) => e.stopPropagation()}
                            className="w-9 h-9 rounded-md bg-white/10 hover:bg-white/20 flex items-center justify-center text-white transition-colors"
                          >
                            <Download className="w-4 h-4" />
                          </a>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Action Bar - Fixed at bottom */}
            <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50">
              <div className="flex items-center gap-2 px-2 py-2 rounded-lg bg-[#111115]/95 backdrop-blur-md border border-white/[0.08] shadow-lg">
                {/* Go to Audio Studio - Primary */}
                <button
                  onClick={() => onGenerateAudio?.(displayScript)}
                  className="flex items-center gap-2 px-4 py-2 rounded-md bg-white text-black text-sm font-medium hover:bg-white/90 transition-colors"
                >
                  <Volume2 className="w-4 h-4" />
                  Create Audio
                </button>
                
                <div className="w-px h-6 bg-white/[0.08]" />
                
                {/* Copy */}
                <button
                  onClick={copyScript}
                  className="flex items-center gap-1.5 px-3 py-2 rounded-md text-white/60 hover:text-white hover:bg-white/[0.05] transition-colors"
                >
                  {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                </button>
                
                {/* New */}
                <button
                  onClick={handleReset}
                  className="flex items-center gap-1.5 px-3 py-2 rounded-md text-white/60 hover:text-white hover:bg-white/[0.05] transition-colors"
                >
                  <RotateCcw className="w-4 h-4" />
                  <span className="text-sm hidden sm:inline">New</span>
                </button>
                
                {/* Delete */}
                {savedResults && (
                  <button
                    onClick={handleReset}
                    className="flex items-center px-2 py-2 rounded-md text-white/40 hover:text-red-400 hover:bg-red-500/10 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          </motion.div>
        )}

        {/* ============================================ */}
        {/* ERROR STATE */}
        {/* ============================================ */}
        {error && !isGenerating && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="fixed bottom-6 left-1/2 -translate-x-1/2 max-w-md z-50"
          >
            <div className="px-4 py-3 rounded-lg bg-red-500/10 border border-red-500/20 flex items-start gap-3">
              <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
              <div>
                <div className="text-sm font-medium text-red-400">Generation Failed</div>
                <div className="text-xs text-white/50 mt-0.5">{error.message}</div>
                <button
                  onClick={handleReset}
                  className="mt-2 text-xs text-red-400 hover:text-red-300 transition-colors"
                >
                  Try Again →
                </button>
              </div>
            </div>
          </motion.div>
        )}

        {/* ============================================ */}
        {/* FALLBACK - If no state matches, show input */}
        {/* ============================================ */}
        {!showInput && !showResults && !showGenerating && (
          <motion.div
            key="fallback"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="max-w-md mx-auto text-center py-20"
          >
            <p className="text-sm text-white/40 mb-4">Something went wrong. Let's start fresh.</p>
            <button 
              onClick={handleReset}
              className="flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium text-white/60 hover:text-white bg-white/[0.05] hover:bg-white/[0.08] border border-white/[0.08] transition-colors mx-auto"
            >
              <RotateCcw className="w-4 h-4" />
              Start Over
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
