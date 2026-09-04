import { useEffect, useRef, useState, useCallback } from 'react';

export interface ToolExecution {
  tool_name: string;
  args: Record<string, any>;
  result?: any;
  success?: boolean;
  timestamp: string;
}

export interface TaskStepItem {
  step_id: number;
  description: string;
  status: string;
  tool_name?: string;
  result?: any;
  error?: string;
  retry_count?: number;
}

export interface TaskPlan {
  plan_id?: string;
  goal?: string;
  task_description?: string;
  route?: string;
  steps: TaskStepItem[];
  status?: string;
  verification_status?: string;
  confidence?: string;
  replan_count?: number;
}

export interface ResearchSourceItem {
  title?: string;
  url: string;
  snippet?: string;
  relevance_score?: number;
}

export interface MultimodalPayloadFile {
  input_type: string;
  filename: string;
  mime_type?: string;
  content_base64: string;
}

export function useWebSocket(sessionId: string, userId: string = 'default_user', token: string | null = null) {
  const [isConnected, setIsConnected] = useState(false);
  const [activityEvents, setActivityEvents] = useState<string[]>([]);
  const [toolExecutions, setToolExecutions] = useState<ToolExecution[]>([]);
  const [taskPlan, setTaskPlan] = useState<TaskPlan | null>(null);
  const [researchSources, setResearchSources] = useState<ResearchSourceItem[]>([]);
  const [transcript, setTranscript] = useState<string>('');
  const [latestAudioBase64, setLatestAudioBase64] = useState<string | null>(null);
  const [finalAnswer, setFinalAnswer] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<any>(null);
  const isUnmountedRef = useRef(false);

  const connect = useCallback(() => {
    if (!sessionId || isUnmountedRef.current) return;

    if (wsRef.current && (wsRef.current.readyState === WebSocket.CONNECTING || wsRef.current.readyState === WebSocket.OPEN)) {
      return;
    }

    const authToken = token || (typeof window !== 'undefined' ? localStorage.getItem('ion_token') || localStorage.getItem('jarvis_token') : null);
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const baseUrl = import.meta.env.VITE_WS_URL || `${wsProtocol}//${window.location.hostname}:8000/ws/${sessionId}`;
    const host = authToken ? `${baseUrl}?token=${encodeURIComponent(authToken)}` : baseUrl;

    try {
      const socket = new WebSocket(host);
      wsRef.current = socket;

      socket.onopen = () => {
        setIsConnected(true);
        setActivityEvents((prev) => [...prev, '✓ WebSocket connected & authenticated']);
      };

      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          const evType = payload.event;

          if (evType === 'thinking') {
            setActivityEvents((prev) => [...prev, `→ ${payload.data}`]);
          } else if (evType === 'speech_started') {
            setActivityEvents((prev) => [...prev, '🎙 Speech recognition started...']);
          } else if (evType === 'transcript') {
            setTranscript(payload.text || '');
            setActivityEvents((prev) => [...prev, `✓ Transcript: "${payload.text}"`]);
          } else if (evType === 'speech_finished') {
            setActivityEvents((prev) => [...prev, '✓ Speech processing complete']);
          } else if (evType === 'audio_chunk') {
            setLatestAudioBase64(payload.audio_base64 || null);
            setActivityEvents((prev) => [...prev, '🔊 Audio response chunk received']);
          } else if (evType === 'tool_call') {
            const tc = payload.data || {};
            setToolExecutions((prev) => [
              ...prev,
              {
                tool_name: tc.tool_name || 'unknown',
                args: tc.args || {},
                timestamp: new Date().toLocaleTimeString(),
              },
            ]);
            setActivityEvents((prev) => [...prev, `→ Executing tool: ${tc.tool_name}`]);
          } else if (evType === 'tool_result') {
            const tr = payload.data || {};
            setToolExecutions((prev) => {
              const updated = [...prev];
              if (updated.length > 0) {
                updated[updated.length - 1] = {
                  ...updated[updated.length - 1],
                  result: tr.output || tr.error,
                  success: tr.success !== false,
                };
              }
              return updated;
            });
            setActivityEvents((prev) => [...prev, `✓ Tool ${tr.tool_name} completed`]);
          } else if (evType === 'plan_created') {
            setTaskPlan(payload.data);
            setActivityEvents((prev) => [...prev, '✓ Task plan created']);
          } else if (evType === 'sources_retrieved') {
            setResearchSources(payload.data || []);
            setActivityEvents((prev) => [...prev, `✓ Retrieved ${payload.data?.length || 0} research sources`]);
          } else if (evType === 'image_processed') {
            setActivityEvents((prev) => [...prev, '✓ Image visual context extracted']);
          } else if (evType === 'document_processed') {
            setActivityEvents((prev) => [...prev, '✓ Document text extracted']);
          } else if (evType === 'final_answer') {
            setFinalAnswer(payload.text || '');
            setActivityEvents((prev) => [...prev, '✓ Final response generated']);
          } else if (evType === 'cancelled') {
            setActivityEvents((prev) => [...prev, '⚠ Session cancelled']);
          } else if (evType === 'error') {
            setActivityEvents((prev) => [...prev, `✖ Error: ${payload.message}`]);
          }
        } catch (err) {
          console.error('Failed to parse WebSocket event:', err);
        }
      };

      socket.onclose = () => {
        setIsConnected(false);
        if (!isUnmountedRef.current) {
          setActivityEvents((prev) => [...prev, '✖ WebSocket disconnected. Reconnecting...']);
          if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, 1500);
        }
      };

      socket.onerror = () => {
        setIsConnected(false);
      };
    } catch (err) {
      console.error('WebSocket connection error:', err);
    }
  }, [sessionId, token]);

  useEffect(() => {
    isUnmountedRef.current = false;
    connect();

    return () => {
      isUnmountedRef.current = true;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  const sendTextMessage = useCallback((text: string, files?: MultimodalPayloadFile[]) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
    setFinalAnswer(null);
    wsRef.current.send(
      JSON.stringify({
        text,
        user_id: userId,
        files,
      })
    );
  }, [userId]);

  const sendVoiceMessage = useCallback((audioBase64: string) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
    setFinalAnswer(null);
    setTranscript('');
    wsRef.current.send(
      JSON.stringify({
        audio_base64: audioBase64,
        user_id: userId,
      })
    );
  }, [userId]);

  const sendCancel = useCallback(() => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
    wsRef.current.send(
      JSON.stringify({
        action: 'cancel',
      })
    );
  }, []);

  const clearActivity = useCallback(() => {
    setActivityEvents([]);
    setToolExecutions([]);
    setTaskPlan(null);
    setResearchSources([]);
    setTranscript('');
    setLatestAudioBase64(null);
    setFinalAnswer(null);
  }, []);

  return {
    isConnected,
    activityEvents,
    toolExecutions,
    taskPlan,
    researchSources,
    transcript,
    latestAudioBase64,
    finalAnswer,
    sendTextMessage,
    sendVoiceMessage,
    sendCancel,
    clearActivity,
  };
}
