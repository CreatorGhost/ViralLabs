// Re-export auth types
export * from './auth';

// ============================================
// API TYPES
// ============================================

export interface ScriptGenerateRequest {
  topic: string;
  model?: string;
  refine_model?: string;
  temperature?: number;
  max_videos?: number;
  top_n_videos?: number;
  subscriber_threshold?: number;
  max_workers?: number;
}

export interface ThumbnailGenerateRequest {
  topic: string;
  num_thumbnails?: number;
  resolution?: string;
  use_reference_images?: boolean;
  include_face?: boolean;
  face_mode?: string;
  face_style?: string;
}

export interface FullWorkflowRequest {
  topic: string;
  // Script settings
  model?: string;
  refine_model?: string;
  temperature?: number;
  max_videos?: number;
  top_n_videos?: number;
  subscriber_threshold?: number;
  max_workers?: number;
  selected_video_ids?: string[]; // Pre-selected videos (skips search if provided)
  // Thumbnail settings
  enable_thumbnails?: boolean;
  num_thumbnails?: number;
  resolution?: string;
  use_reference_images?: boolean;
  include_face?: boolean;
  face_mode?: string;
  face_style?: string;
}

// Video Search Types
export interface SearchVideosRequest {
  topic: string;
  max_videos?: number;
  subscriber_threshold?: number;
  refine_model?: string;
}

export interface VideoItem {
  video_id: string;
  title: string;
  channel: string;
  channel_id: string;
  views: number;
  likes: number;
  comments: number;
  duration: number; // seconds
  score: number;
  thumbnail_url: string;
}

export interface SearchVideosResponse {
  success: boolean;
  refined_query?: string;
  original_query?: string;
  videos?: VideoItem[];
  error?: string;
}

export interface VideoMetadata {
  title: string;
  channel: string;
  video_id: string;
  views: number;
  subscriber_count: number;
  transcript_available?: boolean;
}

export interface ScriptStats {
  total_time?: number;
  search_time?: number;
  rank_time?: number;
  transcript_time?: number;
  generation_time?: number;
  word_count: number;
  char_count: number;
  estimated_duration_min: number;
}

export interface ScriptResponse {
  success: boolean;
  script?: string;
  refined_query?: string;
  original_query?: string;
  videos_analyzed?: number;
  stats?: ScriptStats;
  metadata?: {
    videos?: VideoMetadata[];
    total_videos?: number;
    successful_transcripts?: number;
  };
  combined_transcripts?: string;
  error?: string;
}

export interface ThumbnailItem {
  success: boolean;
  filepath?: string;
  width?: number;
  height?: number;
  resolution?: string;
  error?: string;
  references_used?: number;
  face_mode?: string;
  face_style?: string;
}

export interface ThumbnailResponse {
  success: boolean;
  thumbnails?: ThumbnailItem[];
  successful_count?: number;
  error?: string;
}

export interface FullWorkflowResponse {
  success: boolean;
  script?: ScriptResponse;
  thumbnails?: ThumbnailResponse;
  error?: string;
}

export interface FaceUploadResponse {
  success: boolean;
  face_id?: string;
  filepath?: string;
  error?: string;
}

// Audio Types
export interface AudioGenerateRequest {
  script: string;
  voice?: string; // "male" or "female"
  persona?: string; // Persona ID (storyteller, anime, tech, etc.)
  custom_instructions?: string;
  filename?: string;
}

export interface AudioResponse {
  success: boolean;
  filepath?: string;
  filename?: string;
  audio_url?: string;
  voice?: string;
  persona?: string;
  persona_name?: string;
  model?: string;
  script_length?: number;
  chunks_processed?: number;
  error?: string;
}

export interface PersonaInfo {
  id: string;
  name: string;
  description: string;
  icon: string;
}

export interface AudioOptionsResponse {
  voices: string[];
  personas: PersonaInfo[];
}

// Image Generation Types (Simple prompt-based generation)
export interface ImageGenerateRequest {
  prompt: string;
  num_images?: number;
  resolution?: '1K' | '2K' | '4K';
  include_face?: boolean;
  face_mode?: 'auto' | 'center' | 'left' | 'right';
  face_style?: 'realistic' | 'professional' | 'cartoon';
}

export interface GeneratedImage {
  success: boolean;
  id?: string;
  filepath?: string;
  url?: string;
  width?: number;
  height?: number;
  error?: string;
}

export interface ImageGenerateResponse {
  success: boolean;
  images: GeneratedImage[];
  successful_count: number;
  error?: string;
}

export interface ImageListItem {
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

export interface SessionState {
  has_face: boolean;
  face_id?: string;
  face_path?: string;
  last_script?: ScriptResponse;
  last_thumbnails?: ThumbnailItem[];
}

// ============================================
// UI STATE TYPES
// ============================================

export type WorkflowMode = 'quick' | 'studio';

export type QualityPreset = 'fast' | 'balanced' | 'thorough';

export interface QuickModeSettings {
  includeThumbnails: boolean;
  quality: QualityPreset;
}

export interface StudioModeSettings {
  // Script settings
  model: string;
  refine_model: string;
  temperature: number;
  max_videos: number;
  top_n_videos: number;
  subscriber_threshold: number;
  max_workers: number;
  // Thumbnail settings
  enable_thumbnails: boolean;
  num_thumbnails: number;
  resolution: string;
  use_reference_images: boolean;
  include_face: boolean;
  face_mode: string;
  face_style: string;
}

export const QUALITY_PRESETS: Record<QualityPreset, { videos: number; description: string; time: string }> = {
  fast: { videos: 3, description: 'Quick results', time: '~2 min' },
  balanced: { videos: 5, description: 'Best balance', time: '~3 min' },
  thorough: { videos: 10, description: 'Deep analysis', time: '~5 min' },
};

export const DEFAULT_QUICK_SETTINGS: QuickModeSettings = {
  includeThumbnails: true,
  quality: 'balanced',
};

export const DEFAULT_STUDIO_SETTINGS: StudioModeSettings = {
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
  use_reference_images: true,  // Use YouTube thumbnails as style references
  include_face: false,
  face_mode: 'auto',
  face_style: 'realistic',
};

// ============================================
// SSE STREAMING TYPES
// ============================================

export type StepName = 
  | 'idle' 
  | 'initializing'
  | 'refining' 
  | 'searching' 
  | 'ranking' 
  | 'transcripts' 
  | 'generating' 
  | 'thumbnails' 
  | 'complete';

export type StepStatus = 'pending' | 'in_progress' | 'completed' | 'failed';

export interface VideoSummary {
  title: string;
  channel: string;
  views: number;
}

export interface ProgressData {
  // For refining
  original?: string;
  refined?: string;
  // For search/ranking
  count?: number;
  videos?: VideoSummary[];
  // For transcripts
  current?: number;
  total?: number;
  video_title?: string;
  success?: number;
  // For script
  word_count?: number;
  // For thumbnails
  index?: number;
  url?: string;
  filepath?: string;
  // For errors
  error?: string;
  step?: string;
}

export interface ProgressState {
  currentStep: StepName;
  message: string;
  data: ProgressData;
}

export interface StreamingThumbnail {
  index: number;
  url: string;
  filepath?: string;
}

export interface SSEEvent {
  type: 'progress' | 'script_chunk' | 'thumbnail' | 'complete' | 'error';
  step: string;
  message: string;
  data: ProgressData & {
    chunk?: string;
    script?: string;
    script_word_count?: number;
    refined_query?: string;
    videos_analyzed?: number;
    thumbnails?: Array<{ url: string; filepath?: string }>;
  };
}

export interface StreamingError {
  step: StepName;
  message: string;
  details?: string;
}

// ============================================
// STEP METADATA
// ============================================

export interface StepMeta {
  name: StepName;
  label: string;
  description: string;
}

export const WORKFLOW_STEPS: StepMeta[] = [
  { name: 'refining', label: 'Refining', description: 'Optimizing your search query' },
  { name: 'searching', label: 'Searching', description: 'Finding relevant videos' },
  { name: 'ranking', label: 'Ranking', description: 'Selecting best videos' },
  { name: 'transcripts', label: 'Transcripts', description: 'Extracting video content' },
  { name: 'generating', label: 'Writing', description: 'Creating your script' },
  { name: 'thumbnails', label: 'Thumbnails', description: 'Generating visuals' },
];

