import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  X,
  Download,
  Maximize2,
  Loader2,
  Wand2,
  Image,
  Check,
  Trash2,
  Clock,
  Sparkles,
  RefreshCw,
  Coins,
} from 'lucide-react';
import { generateThumbnails, listThumbnails, getThumbnailUrl } from '../api/client';
import { getSessionId } from '../config';
import { useCredits } from '../context';

interface ThumbnailItem {
  id?: string;
  filename: string;
  path: string;
  created: string;
  url?: string;
  metadata?: Record<string, unknown>;
}

interface ThumbnailStudioPageProps {
  includeFace?: boolean;
}

export default function ThumbnailStudioPage({ includeFace = false }: ThumbnailStudioPageProps) {
  const sessionId = getSessionId();
  const navigate = useNavigate();
  const { user, credits, hasCredits, refreshCredits } = useCredits();

  // Generation state
  const [prompt, setPrompt] = useState('');
  const [numThumbnails, setNumThumbnails] = useState(3);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationError, setGenerationError] = useState<string | null>(null);
  
  // Gallery state
  const [thumbnails, setThumbnails] = useState<ThumbnailItem[]>([]);
  const [selectedThumbnail, setSelectedThumbnail] = useState<ThumbnailItem | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load existing thumbnails on mount
  useEffect(() => {
    loadThumbnails();
  }, []);

  const loadThumbnails = async () => {
    setIsLoading(true);
    try {
      const response = await listThumbnails();
      const thumbsWithUrls = response.thumbnails.map(t => ({
        ...t,
        // Use the URL from response if available (R2), otherwise construct from filename
        url: t.url || t.path || getThumbnailUrl(t.filename),
      }));
      setThumbnails(thumbsWithUrls); // Already sorted newest first by backend
    } catch (e) {
      console.error('Failed to load thumbnails:', e);
    } finally {
      setIsLoading(false);
    }
  };

  // Generate thumbnails
  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    if (!hasCredits) {
      setGenerationError('No credits remaining. Please purchase more credits.');
      return;
    }

    setIsGenerating(true);
    setGenerationError(null);

    try {
      const response = await generateThumbnails({
        topic: prompt.trim(),
        num_thumbnails: numThumbnails,
        include_face: includeFace,
      }, sessionId);

      if (response.success) {
        // Reload thumbnails to show new ones
        await loadThumbnails();
        // Refresh credits after successful generation
        await refreshCredits();
        setPrompt('');
      } else {
        setGenerationError(response.error || 'Generation failed');
      }
    } catch (e: unknown) {
      // Check if it's a 402 Payment Required error
      if (e instanceof Error && e.message.includes('402')) {
        setGenerationError('No credits remaining. Please purchase more credits.');
      } else {
        setGenerationError('Failed to generate thumbnails. Please try again.');
      }
    } finally {
      setIsGenerating(false);
    }
  };

  // Download thumbnail
  const downloadThumbnail = async (thumb: ThumbnailItem) => {
    try {
      const response = await fetch(thumb.url!);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = thumb.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (e) {
      console.error('Download failed:', e);
    }
  };

  // Format date
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="flex flex-col items-center min-h-[calc(100vh-120px)] px-6 pt-8 pb-16">
      {/* Zoom Modal */}
      <AnimatePresence>
        {selectedThumbnail && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[100] flex items-center justify-center p-6"
            onClick={() => setSelectedThumbnail(null)}
          >
            <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" />
            
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              onClick={(e) => e.stopPropagation()}
              className="relative z-10 w-full max-w-4xl"
            >
              <div className="bg-[#0f1014] border border-white/[0.08] rounded-xl overflow-hidden">
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-white/[0.06]">
                  <div>
                    <h3 className="text-sm font-medium text-white">{selectedThumbnail.filename}</h3>
                    <p className="text-xs text-white/40 mt-0.5">
                      {formatDate(selectedThumbnail.created)}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => downloadThumbnail(selectedThumbnail)}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-white/[0.05] hover:bg-white/[0.08] border border-white/[0.08] text-xs text-white/70 transition-colors"
                    >
                      <Download className="w-3.5 h-3.5" />
                      Download
                    </button>
                    <button
                      onClick={() => setSelectedThumbnail(null)}
                      className="w-8 h-8 rounded-md hover:bg-white/[0.05] flex items-center justify-center text-white/40 hover:text-white/70 transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                
                {/* Image */}
                <div className="p-4">
                  <img 
                    src={selectedThumbnail.url} 
                    alt={selectedThumbnail.filename}
                    className="w-full h-auto rounded-lg"
                  />
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="w-full max-w-5xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-2xl font-semibold text-white mb-1">Thumbnail Studio</h1>
          <p className="text-sm text-white/50">Generate eye-catching thumbnails for your videos</p>
        </motion.div>

        {/* Main Content - Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Generation */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="lg:col-span-1"
          >
            <div className="bg-white/[0.02] border border-white/[0.06] rounded-xl p-5 sticky top-28">
              <div className="flex items-center gap-2 mb-5">
                <Wand2 className="w-4 h-4 text-white/50" />
                <h2 className="text-sm font-medium text-white">Generate New</h2>
              </div>
              
              {/* Prompt Input */}
              <div className="mb-4">
                <label className="text-xs font-medium text-white/40 uppercase tracking-wider mb-2 block">
                  Topic / Description
                </label>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="e.g., Best AI coding tools in 2025..."
                  rows={3}
                  className="w-full px-3 py-2.5 rounded-lg bg-black/20 border border-white/[0.08] text-sm text-white placeholder-white/30 focus:outline-none focus:border-white/20 resize-none"
                />
              </div>

              {/* Options Grid */}
              <div className="grid grid-cols-1 gap-3 mb-4">
                {/* Number of Thumbnails */}
                <div>
                  <label className="text-xs font-medium text-white/40 uppercase tracking-wider mb-2 block">
                    Count
                  </label>
                  <div className="flex gap-1">
                    {[1, 2, 3, 4].map((n) => (
                      <button
                        key={n}
                        onClick={() => setNumThumbnails(n)}
                        className={`flex-1 py-2 rounded-md text-xs font-medium transition-all ${
                          numThumbnails === n
                            ? 'bg-white/10 text-white border border-white/20'
                            : 'bg-white/[0.03] text-white/50 border border-white/[0.06] hover:border-white/10'
                        }`}
                      >
                        {n}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Credits Display */}
              <div className={`flex items-center justify-between p-3 rounded-lg mb-4 ${
                hasCredits
                  ? 'bg-white/[0.02] border border-white/[0.06]'
                  : 'bg-red-500/10 border border-red-500/20'
              }`}>
                <div className="flex items-center gap-2">
                  <Coins className="w-4 h-4 text-amber-400" />
                  <span className="text-xs text-white/60">Available Credits</span>
                </div>
                <span className={`text-sm font-medium ${hasCredits ? 'text-white' : 'text-red-400'}`}>
                  {user?.credits ?? 0}
                </span>
              </div>

              {!hasCredits && (
                <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 mb-4">
                  <p className="text-xs text-red-400 mb-2">You need credits to generate thumbnails.</p>
                  <button
                    onClick={() => navigate('/pricing')}
                    className="text-xs text-violet-400 hover:text-violet-300 font-medium"
                  >
                    Buy Credits →
                  </button>
                </div>
              )}

              {/* Face Status Indicator */}
              <div className={`flex items-center gap-2 p-3 rounded-lg mb-4 ${
                includeFace
                  ? 'bg-emerald-500/10 border border-emerald-500/20'
                  : 'bg-white/[0.02] border border-white/[0.06]'
              }`}>
                <div className={`w-2 h-2 rounded-full ${includeFace ? 'bg-emerald-400' : 'bg-white/20'}`} />
                <span className={`text-xs ${includeFace ? 'text-emerald-400' : 'text-white/40'}`}>
                  {includeFace ? 'Your face will be included' : 'Face not included'}
                </span>
                <span className="text-[10px] text-white/30 ml-auto">via nav toggle</span>
              </div>

              {/* Error Message */}
              {generationError && (
                <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 mb-4">
                  <p className="text-xs text-red-400">{generationError}</p>
                </div>
              )}

              {/* Generate Button */}
              <button
                onClick={handleGenerate}
                disabled={!prompt.trim() || isGenerating || !hasCredits}
                className={`w-full flex items-center justify-center gap-2 py-3 rounded-lg text-sm font-medium transition-all ${
                  prompt.trim() && !isGenerating && hasCredits
                    ? 'bg-white text-black hover:bg-white/90'
                    : 'bg-white/[0.06] text-white/30 cursor-not-allowed'
                }`}
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Generate Thumbnails
                  </>
                )}
              </button>

              {/* Generation Info */}
              <p className="text-[10px] text-white/30 text-center mt-3">
                ~30-60 seconds per thumbnail · Uses 1 credit
              </p>
            </div>
          </motion.div>

          {/* Right Column - Gallery */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="lg:col-span-2"
          >
            <div className="bg-white/[0.02] border border-white/[0.06] rounded-xl p-5">
              {/* Gallery Header */}
              <div className="flex items-center justify-between mb-5">
                <div className="flex items-center gap-2">
                  <Image className="w-4 h-4 text-white/50" />
                  <h2 className="text-sm font-medium text-white">Your Thumbnails</h2>
                  <span className="text-xs text-white/40 px-2 py-0.5 rounded bg-white/[0.05]">
                    {thumbnails.length}
                  </span>
                </div>
                <button
                  onClick={loadThumbnails}
                  disabled={isLoading}
                  className="p-2 rounded-md hover:bg-white/[0.05] text-white/40 hover:text-white/70 transition-colors disabled:opacity-50"
                  title="Refresh"
                >
                  <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                </button>
              </div>

              {/* Thumbnails Grid */}
              {isLoading ? (
                <div className="flex items-center justify-center py-16">
                  <Loader2 className="w-6 h-6 text-white/30 animate-spin" />
                </div>
              ) : thumbnails.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-16 text-center">
                  <div className="w-12 h-12 rounded-full bg-white/[0.03] flex items-center justify-center mb-3">
                    <Image className="w-5 h-5 text-white/20" />
                  </div>
                  <p className="text-sm text-white/40 mb-1">No thumbnails yet</p>
                  <p className="text-xs text-white/25">Generate your first thumbnail using the form</p>
                </div>
              ) : (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {thumbnails.map((thumb, index) => (
                    <motion.div
                      key={thumb.filename}
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: index * 0.03 }}
                      className="group relative aspect-video rounded-lg overflow-hidden bg-black/20 border border-white/[0.06] hover:border-white/[0.12] transition-all cursor-pointer"
                      onClick={() => setSelectedThumbnail(thumb)}
                    >
                      {/* Thumbnail Image */}
                      <img 
                        src={thumb.url} 
                        alt={thumb.filename}
                        className="w-full h-full object-cover transition-transform group-hover:scale-105"
                      />
                      
                      {/* Hover Overlay */}
                      <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedThumbnail(thumb);
                          }}
                          className="w-9 h-9 rounded-lg bg-white/10 hover:bg-white/20 flex items-center justify-center text-white transition-colors"
                        >
                          <Maximize2 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            downloadThumbnail(thumb);
                          }}
                          className="w-9 h-9 rounded-lg bg-white/10 hover:bg-white/20 flex items-center justify-center text-white transition-colors"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                      </div>

                      {/* Date Badge */}
                      <div className="absolute bottom-2 left-2 px-2 py-1 rounded bg-black/60 backdrop-blur-sm">
                        <p className="text-[10px] text-white/70 flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {formatDate(thumb.created)}
                        </p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
