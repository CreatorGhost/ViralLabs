import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  X, 
  Download, 
  Maximize2,
  Loader2,
  Wand2,
  Image,
  Clock,
  Sparkles,
  RefreshCw,
  Trash2,
  User,
} from 'lucide-react';
import { generateImages, listImages, deleteImage } from '../api/client';

interface ImageItem {
  id: string;
  url: string;
  filename: string;
  created_at: string;
  metadata?: {
    prompt?: string;
    resolution?: string;
    width?: number;
    height?: number;
    include_face?: boolean;
  };
}

interface ImageStudioPageProps {
  includeFace?: boolean;
}

export default function ImageStudioPage({ includeFace = false }: ImageStudioPageProps) {
  // Generation state
  const [prompt, setPrompt] = useState('');
  const [numImages, setNumImages] = useState(1);
  const [resolution, setResolution] = useState<'1K' | '2K' | '4K'>('2K');
  const [useFace, setUseFace] = useState(false);
  const [faceMode, setFaceMode] = useState<'auto' | 'center' | 'left' | 'right'>('auto');
  const [faceStyle, setFaceStyle] = useState<'realistic' | 'professional' | 'cartoon'>('realistic');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationError, setGenerationError] = useState<string | null>(null);
  
  // Gallery state
  const [images, setImages] = useState<ImageItem[]>([]);
  const [selectedImage, setSelectedImage] = useState<ImageItem | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  // Load existing images on mount
  useEffect(() => {
    loadImages();
  }, []);

  // Update useFace when includeFace prop changes
  useEffect(() => {
    setUseFace(includeFace);
  }, [includeFace]);

  const loadImages = async () => {
    setIsLoading(true);
    try {
      const response = await listImages();
      setImages(response.images || []);
    } catch (e) {
      console.error('Failed to load images:', e);
    } finally {
      setIsLoading(false);
    }
  };

  // Generate images
  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    
    setIsGenerating(true);
    setGenerationError(null);
    
    try {
      const response = await generateImages({
        prompt: prompt.trim(),
        num_images: numImages,
        resolution,
        include_face: useFace && includeFace,
        face_mode: faceMode,
        face_style: faceStyle,
      });
      
      if (response.success) {
        // Reload images to show new ones
        await loadImages();
        setPrompt('');
      } else {
        setGenerationError(response.error || 'Generation failed');
      }
    } catch (e) {
      setGenerationError('Failed to generate images. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  // Delete image
  const handleDelete = async (imageId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setDeletingId(imageId);
    try {
      await deleteImage(imageId);
      setImages(prev => prev.filter(img => img.id !== imageId));
      if (selectedImage?.id === imageId) {
        setSelectedImage(null);
      }
    } catch (e) {
      console.error('Failed to delete image:', e);
    } finally {
      setDeletingId(null);
    }
  };

  // Download image
  const downloadImage = async (img: ImageItem) => {
    try {
      const response = await fetch(img.url);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = img.filename || 'image.png';
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
        {selectedImage && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[100] flex items-center justify-center p-6"
            onClick={() => setSelectedImage(null)}
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
                    <h3 className="text-sm font-medium text-white">{selectedImage.filename}</h3>
                    <p className="text-xs text-white/40 mt-0.5">
                      {formatDate(selectedImage.created_at)}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => downloadImage(selectedImage)}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-white/[0.05] hover:bg-white/[0.08] border border-white/[0.08] text-xs text-white/70 transition-colors"
                    >
                      <Download className="w-3.5 h-3.5" />
                      Download
                    </button>
                    <button
                      onClick={() => setSelectedImage(null)}
                      className="w-8 h-8 rounded-md hover:bg-white/[0.05] flex items-center justify-center text-white/40 hover:text-white/70 transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                
                {/* Image */}
                <div className="p-4">
                  <img 
                    src={selectedImage.url} 
                    alt={selectedImage.filename}
                    className="w-full h-auto rounded-lg"
                  />
                  {selectedImage.metadata?.prompt && (
                    <p className="mt-3 text-xs text-white/50 italic">
                      "{selectedImage.metadata.prompt}"
                    </p>
                  )}
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
          <h1 className="text-2xl font-semibold text-white mb-1">Image Studio</h1>
          <p className="text-sm text-white/50">Generate images from any prompt with AI</p>
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
                <Wand2 className="w-4 h-4 text-violet-400" />
                <h2 className="text-sm font-medium text-white">Generate Image</h2>
              </div>
              
              {/* Prompt Input */}
              <div className="mb-4">
                <label className="text-xs font-medium text-white/40 uppercase tracking-wider mb-2 block">
                  Prompt
                </label>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Describe the image you want to create..."
                  rows={4}
                  className="w-full px-3 py-2.5 rounded-lg bg-black/20 border border-white/[0.08] text-sm text-white placeholder-white/30 focus:outline-none focus:border-violet-500/50 resize-none"
                />
              </div>

              {/* Options Grid */}
              <div className="grid grid-cols-2 gap-3 mb-4">
                {/* Number of Images */}
                <div>
                  <label className="text-xs font-medium text-white/40 uppercase tracking-wider mb-2 block">
                    Count
                  </label>
                  <div className="flex gap-1">
                    {[1, 2, 3].map((n) => (
                      <button
                        key={n}
                        onClick={() => setNumImages(n)}
                        className={`flex-1 py-2 rounded-md text-xs font-medium transition-all ${
                          numImages === n
                            ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
                            : 'bg-white/[0.03] text-white/50 border border-white/[0.06] hover:border-white/10'
                        }`}
                      >
                        {n}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Resolution */}
                <div>
                  <label className="text-xs font-medium text-white/40 uppercase tracking-wider mb-2 block">
                    Resolution
                  </label>
                  <div className="flex gap-1">
                    {(['1K', '2K', '4K'] as const).map((res) => (
                      <button
                        key={res}
                        onClick={() => setResolution(res)}
                        className={`flex-1 py-2 rounded-md text-xs font-medium transition-all ${
                          resolution === res
                            ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
                            : 'bg-white/[0.03] text-white/50 border border-white/[0.06] hover:border-white/10'
                        }`}
                      >
                        {res}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Face Options */}
              {includeFace && (
                <div className="mb-4 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4 text-emerald-400" />
                      <span className="text-xs font-medium text-emerald-400">Include Face</span>
                    </div>
                    <button
                      onClick={() => setUseFace(!useFace)}
                      className={`w-10 h-5 rounded-full transition-colors ${
                        useFace ? 'bg-emerald-500' : 'bg-white/10'
                      }`}
                    >
                      <div className={`w-4 h-4 rounded-full bg-white transition-transform ${
                        useFace ? 'translate-x-5' : 'translate-x-0.5'
                      }`} />
                    </button>
                  </div>
                  
                  {useFace && (
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="text-[10px] text-white/40 uppercase mb-1 block">Position</label>
                        <select
                          value={faceMode}
                          onChange={(e) => setFaceMode(e.target.value as typeof faceMode)}
                          className="w-full px-2 py-1.5 rounded bg-black/30 border border-white/10 text-xs text-white"
                        >
                          <option value="auto">Auto</option>
                          <option value="center">Center</option>
                          <option value="left">Left</option>
                          <option value="right">Right</option>
                        </select>
                      </div>
                      <div>
                        <label className="text-[10px] text-white/40 uppercase mb-1 block">Style</label>
                        <select
                          value={faceStyle}
                          onChange={(e) => setFaceStyle(e.target.value as typeof faceStyle)}
                          className="w-full px-2 py-1.5 rounded bg-black/30 border border-white/10 text-xs text-white"
                        >
                          <option value="realistic">Realistic</option>
                          <option value="professional">Professional</option>
                          <option value="cartoon">Cartoon</option>
                        </select>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* No Face Info */}
              {!includeFace && (
                <div className="flex items-center gap-2 p-3 rounded-lg mb-4 bg-white/[0.02] border border-white/[0.06]">
                  <div className="w-2 h-2 rounded-full bg-white/20" />
                  <span className="text-xs text-white/40">
                    Face not available
                  </span>
                  <span className="text-[10px] text-white/30 ml-auto">Upload in Settings</span>
                </div>
              )}

              {/* Error Message */}
              {generationError && (
                <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 mb-4">
                  <p className="text-xs text-red-400">{generationError}</p>
                </div>
              )}

              {/* Generate Button */}
              <button
                onClick={handleGenerate}
                disabled={!prompt.trim() || isGenerating}
                className={`w-full flex items-center justify-center gap-2 py-3 rounded-lg text-sm font-medium transition-all ${
                  prompt.trim() && !isGenerating
                    ? 'bg-gradient-to-r from-violet-600 to-purple-600 text-white hover:from-violet-500 hover:to-purple-500'
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
                    Generate
                  </>
                )}
              </button>

              {/* Generation Info */}
              <p className="text-[10px] text-white/30 text-center mt-3">
                ~15-30 seconds per image
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
                  <h2 className="text-sm font-medium text-white">Your Images</h2>
                  <span className="text-xs text-white/40 px-2 py-0.5 rounded bg-white/[0.05]">
                    {images.length}
                  </span>
                </div>
                <button
                  onClick={loadImages}
                  disabled={isLoading}
                  className="p-2 rounded-md hover:bg-white/[0.05] text-white/40 hover:text-white/70 transition-colors disabled:opacity-50"
                  title="Refresh"
                >
                  <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                </button>
              </div>

              {/* Images Grid */}
              {isLoading ? (
                <div className="flex items-center justify-center py-16">
                  <Loader2 className="w-6 h-6 text-white/30 animate-spin" />
                </div>
              ) : images.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-16 text-center">
                  <div className="w-12 h-12 rounded-full bg-white/[0.03] flex items-center justify-center mb-3">
                    <Image className="w-5 h-5 text-white/20" />
                  </div>
                  <p className="text-sm text-white/40 mb-1">No images yet</p>
                  <p className="text-xs text-white/25">Generate your first image using the form</p>
                </div>
              ) : (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {images.map((img, index) => (
                    <motion.div
                      key={img.id}
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: index * 0.03 }}
                      className="group relative aspect-video rounded-lg overflow-hidden bg-black/20 border border-white/[0.06] hover:border-violet-500/30 transition-all cursor-pointer"
                      onClick={() => setSelectedImage(img)}
                    >
                      {/* Image */}
                      <img 
                        src={img.url} 
                        alt={img.filename}
                        className="w-full h-full object-cover transition-transform group-hover:scale-105"
                      />
                      
                      {/* Hover Overlay */}
                      <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedImage(img);
                          }}
                          className="w-9 h-9 rounded-lg bg-white/10 hover:bg-white/20 flex items-center justify-center text-white transition-colors"
                        >
                          <Maximize2 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            downloadImage(img);
                          }}
                          className="w-9 h-9 rounded-lg bg-white/10 hover:bg-white/20 flex items-center justify-center text-white transition-colors"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                        <button
                          onClick={(e) => handleDelete(img.id, e)}
                          disabled={deletingId === img.id}
                          className="w-9 h-9 rounded-lg bg-red-500/20 hover:bg-red-500/30 flex items-center justify-center text-red-400 transition-colors disabled:opacity-50"
                        >
                          {deletingId === img.id ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <Trash2 className="w-4 h-4" />
                          )}
                        </button>
                      </div>

                      {/* Date Badge */}
                      <div className="absolute bottom-2 left-2 px-2 py-1 rounded bg-black/60 backdrop-blur-sm">
                        <p className="text-[10px] text-white/70 flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {formatDate(img.created_at)}
                        </p>
                      </div>

                      {/* Face Badge */}
                      {img.metadata?.include_face && (
                        <div className="absolute top-2 right-2 px-2 py-1 rounded bg-emerald-500/20 backdrop-blur-sm">
                          <User className="w-3 h-3 text-emerald-400" />
                        </div>
                      )}
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

