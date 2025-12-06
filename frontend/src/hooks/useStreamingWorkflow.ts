import { useState, useCallback, useRef } from 'react';
import type {
  FullWorkflowRequest,
  StepName,
  ProgressState,
  StreamingThumbnail,
  StreamingError,
  SSEEvent,
} from '../types';
import { API_BASE } from '../config';

interface UseStreamingWorkflowReturn {
  startGeneration: (request: FullWorkflowRequest, sessionId: string) => void;
  stopGeneration: () => void;
  progress: ProgressState;
  script: string;
  thumbnails: StreamingThumbnail[];
  error: StreamingError | null;
  isGenerating: boolean;
  isComplete: boolean;
  refinedQuery: string;
  videosAnalyzed: number;
  resetState: () => void;
}

const initialProgress: ProgressState = {
  currentStep: 'idle',
  message: '',
  data: {},
};

export function useStreamingWorkflow(): UseStreamingWorkflowReturn {
  const [progress, setProgress] = useState<ProgressState>(initialProgress);
  const [script, setScript] = useState('');
  const [thumbnails, setThumbnails] = useState<StreamingThumbnail[]>([]);
  const [error, setError] = useState<StreamingError | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [refinedQuery, setRefinedQuery] = useState('');
  const [videosAnalyzed, setVideosAnalyzed] = useState(0);
  
  const abortControllerRef = useRef<AbortController | null>(null);

  const resetState = useCallback(() => {
    setProgress(initialProgress);
    setScript('');
    setThumbnails([]);
    setError(null);
    setIsComplete(false);
    setRefinedQuery('');
    setVideosAnalyzed(0);
  }, []);

  const stopGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsGenerating(false);
  }, []);

  const parseSSELine = (line: string): SSEEvent | null => {
    if (!line.startsWith('data: ')) return null;
    try {
      const jsonStr = line.slice(6); // Remove "data: " prefix
      return JSON.parse(jsonStr) as SSEEvent;
    } catch {
      console.error('Failed to parse SSE line:', line);
      return null;
    }
  };

  const handleEvent = useCallback((event: SSEEvent) => {
    const { type, step, message, data } = event;

    switch (type) {
      case 'progress':
        setProgress({
          currentStep: step as StepName,
          message,
          data,
        });
        
        // Extract refined query when available
        if (step === 'refining' && data.refined) {
          setRefinedQuery(data.refined);
        }
        
        // Extract videos analyzed count
        if (step === 'transcripts' && data.success !== undefined) {
          setVideosAnalyzed(data.success);
        }
        if (step === 'ranking' && data.count !== undefined) {
          setVideosAnalyzed(data.count);
        }
        break;

      case 'script_chunk':
        if (data.chunk) {
          setScript((prev) => prev + data.chunk);
        }
        break;

      case 'thumbnail':
        if (data.url) {
          const newThumbnail: StreamingThumbnail = {
            index: data.index || 0,
            url: data.url,
            filepath: data.filepath,
          };
          setThumbnails((prev) => [...prev, newThumbnail]);
        }
        break;

      case 'complete':
        setProgress({
          currentStep: 'complete',
          message: 'Workflow complete!',
          data,
        });
        
        // Set final values from complete event
        if (data.refined_query) {
          setRefinedQuery(data.refined_query);
        }
        if (data.videos_analyzed !== undefined) {
          setVideosAnalyzed(data.videos_analyzed);
        }
        
        setIsComplete(true);
        setIsGenerating(false);
        break;

      case 'error':
        setError({
          step: (data.step || step) as StepName,
          message,
          details: data.error,
        });
        setIsGenerating(false);
        break;
    }
  }, []);

  const startGeneration = useCallback(
    async (request: FullWorkflowRequest, sessionId: string) => {
      // Cleanup any existing connection
      stopGeneration();
      resetState();
      
      setIsGenerating(true);
      setProgress({
        currentStep: 'initializing',
        message: 'Starting generation...',
        data: { original: request.topic },
      });

      abortControllerRef.current = new AbortController();

      try {
        const response = await fetch(
          `${API_BASE}/generate/full-workflow/stream?session_id=${sessionId}`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'text/event-stream',
            },
            body: JSON.stringify(request),
            signal: abortControllerRef.current.signal,
          }
        );

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        if (!response.body) {
          throw new Error('Response body is null');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          
          if (done) {
            // Process any remaining buffer content
            if (buffer.trim()) {
              const lines = buffer.split('\n');
              for (const line of lines) {
                if (line.trim()) {
                  const event = parseSSELine(line.trim());
                  if (event) {
                    handleEvent(event);
                  }
                }
              }
            }
            break;
          }

          buffer += decoder.decode(value, { stream: true });
          
          // Process complete SSE messages (each ends with \n\n)
          const messages = buffer.split('\n\n');
          buffer = messages.pop() || ''; // Keep incomplete message in buffer

          for (const message of messages) {
            const lines = message.split('\n');
            for (const line of lines) {
              if (line.trim()) {
                const event = parseSSELine(line.trim());
                if (event) {
                  handleEvent(event);
                }
              }
            }
          }
        }

        // If we finished without a complete event, mark as complete
        if (isGenerating) {
          setIsGenerating(false);
        }

      } catch (err) {
        if (err instanceof Error && err.name === 'AbortError') {
          // User cancelled - this is expected
          console.log('Generation cancelled by user');
        } else {
          console.error('Streaming error:', err);
          setError({
            step: progress.currentStep,
            message: err instanceof Error ? err.message : 'Unknown error occurred',
            details: String(err),
          });
        }
        setIsGenerating(false);
      }
    },
    [stopGeneration, resetState, handleEvent, isGenerating, progress.currentStep]
  );

  return {
    startGeneration,
    stopGeneration,
    progress,
    script,
    thumbnails,
    error,
    isGenerating,
    isComplete,
    refinedQuery,
    videosAnalyzed,
    resetState,
  };
}

