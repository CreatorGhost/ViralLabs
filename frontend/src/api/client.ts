import { API_BASE } from '../config';
import { authFetch, getAuthHeaders } from './auth';
import type {
  ScriptGenerateRequest,
  ThumbnailGenerateRequest,
  FullWorkflowRequest,
  ScriptResponse,
  ThumbnailResponse,
  FullWorkflowResponse,
  FaceUploadResponse,
  SessionState,
  SearchVideosRequest,
  SearchVideosResponse,
  AudioGenerateRequest,
  AudioResponse,
  AudioOptionsResponse,
  ImageGenerateRequest,
  ImageGenerateResponse,
} from '../types';

// ============================================
// HEALTH CHECK
// ============================================

export const healthCheck = async (): Promise<{
  status: string;
  openai_key: boolean;
  gemini_key: boolean;
  youtube_key: boolean;
}> => {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) throw new Error('Health check failed');
  return response.json();
};

// ============================================
// VIDEO SEARCH
// ============================================

export const searchVideos = async (
  request: SearchVideosRequest,
  sessionId: string = 'default'
): Promise<SearchVideosResponse> => {
  const response = await authFetch(`${API_BASE}/search/videos?session_id=${sessionId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!response.ok) throw new Error('Video search failed');
  return response.json();
};

// ============================================
// SESSION
// ============================================

export const getSession = async (sessionId: string): Promise<SessionState> => {
  const response = await authFetch(`${API_BASE}/session/${sessionId}`);
  if (!response.ok) throw new Error('Failed to get session');
  return response.json();
};

// ============================================
// SCRIPT GENERATION
// ============================================

export const generateScript = async (
  request: ScriptGenerateRequest,
  sessionId: string = 'default'
): Promise<ScriptResponse> => {
  const response = await authFetch(`${API_BASE}/generate/script?session_id=${sessionId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!response.ok) throw new Error('Script generation failed');
  return response.json();
};

// ============================================
// THUMBNAIL GENERATION
// ============================================

export const generateThumbnails = async (
  request: ThumbnailGenerateRequest,
  sessionId: string = 'default'
): Promise<ThumbnailResponse> => {
  const response = await authFetch(`${API_BASE}/generate/thumbnails?session_id=${sessionId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!response.ok) throw new Error('Thumbnail generation failed');
  return response.json();
};

// ============================================
// FULL WORKFLOW
// ============================================

export const runFullWorkflow = async (
  request: FullWorkflowRequest,
  sessionId: string = 'default'
): Promise<FullWorkflowResponse> => {
  const response = await authFetch(`${API_BASE}/generate/full-workflow?session_id=${sessionId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!response.ok) throw new Error('Full workflow failed');
  return response.json();
};

// ============================================
// FACE UPLOAD
// ============================================

export const uploadFace = async (
  file: File,
  sessionId: string = 'default'
): Promise<FaceUploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await authFetch(`${API_BASE}/upload/face?session_id=${sessionId}`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) throw new Error('Face upload failed');
  return response.json();
};

export const deleteFace = async (sessionId: string = 'default'): Promise<{ success: boolean }> => {
  const response = await authFetch(`${API_BASE}/upload/face?session_id=${sessionId}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete face');
  return response.json();
};

export const getFaceUrl = (sessionId: string = 'default'): string => {
  return `${API_BASE}/face/${sessionId}`;
};

// ============================================
// THUMBNAILS
// ============================================

export const getThumbnailUrl = (filename: string): string => {
  // Handle both full R2 URLs and relative paths
  if (filename.startsWith('http://') || filename.startsWith('https://')) {
    return filename;
  }
  return `${API_BASE}/thumbnail/${filename}`;
};

export const listThumbnails = async (): Promise<{
  thumbnails: Array<{ 
    id?: string;
    filename: string; 
    path: string; 
    url?: string;
    created: string;
    metadata?: Record<string, unknown>;
  }>;
}> => {
  const response = await authFetch(`${API_BASE}/thumbnail/list`);
  if (!response.ok) throw new Error('Failed to list thumbnails');
  return response.json();
};

export const deleteThumbnail = async (filename: string): Promise<{ success: boolean; message: string }> => {
  const response = await authFetch(`${API_BASE}/thumbnail/${filename}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete thumbnail');
  return response.json();
};

// ============================================
// AUDIO GENERATION
// ============================================

export const getAudioOptions = async (): Promise<AudioOptionsResponse> => {
  const response = await authFetch(`${API_BASE}/audio/options`);
  if (!response.ok) throw new Error('Failed to get audio options');
  return response.json();
};

export const generateAudio = async (
  request: AudioGenerateRequest
): Promise<AudioResponse> => {
  const response = await authFetch(`${API_BASE}/audio/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!response.ok) throw new Error('Audio generation failed');
  return response.json();
};

export const getAudioUrl = (filename: string): string => {
  return `${API_BASE}/audio/files/${filename}`;
};

export const listAudioFiles = async (): Promise<{
  success: boolean;
  count: number;
  files: Array<{ filename: string; url: string; size_bytes: number; created_at: number }>;
}> => {
  const response = await authFetch(`${API_BASE}/audio/list`);
  if (!response.ok) throw new Error('Failed to list audio files');
  return response.json();
};

export const deleteAudioFile = async (filename: string): Promise<{ success: boolean; message: string }> => {
  const response = await authFetch(`${API_BASE}/audio/files/${filename}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete audio file');
  return response.json();
};

// ============================================
// IMAGE GENERATION (Simple prompt-based)
// ============================================

export const generateImages = async (
  request: ImageGenerateRequest
): Promise<ImageGenerateResponse> => {
  const response = await authFetch(`${API_BASE}/image/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!response.ok) throw new Error('Image generation failed');
  return response.json();
};

export const listImages = async (): Promise<{
  success: boolean;
  count: number;
  images: Array<{
    id: string;
    url: string;
    filename: string;
    created_at: string;
    metadata?: Record<string, unknown>;
  }>;
}> => {
  const response = await authFetch(`${API_BASE}/image/list`);
  if (!response.ok) throw new Error('Failed to list images');
  return response.json();
};

export const deleteImage = async (imageId: string): Promise<{ success: boolean; message: string }> => {
  const response = await authFetch(`${API_BASE}/image/${imageId}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete image');
  return response.json();
};

// Export the base URL for direct image access
export { API_BASE };

