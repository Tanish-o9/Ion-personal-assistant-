export type VoiceStatus = 'idle' | 'listening' | 'processing' | 'speaking' | 'offline';

export type ModelOption = 'claude' | 'huggingFace' | 'gemini' | 'openai';

export type EmotionLabel =
  | 'Happy'
  | 'Sad'
  | 'Angry'
  | 'Calm'
  | 'Excited'
  | 'Curious'
  | 'Professional'
  | 'Supportive'
  | 'Friendly'
  | 'Motivated'
  | 'Energetic'
  | 'Confused';

export interface ChatMessage {
  id: string;
  role: 'assistant' | 'user' | 'system';
  content: string;
  createdAt: string;
  isStreaming?: boolean;
}

export interface MemoryEntry {
  id: string;
  category: 'short-term' | 'long-term';
  title: string;
  value: string;
  createdAt: string;
}

export interface EmotionRecord {
  id: string;
  label: EmotionLabel;
  confidence: number;
  createdAt: string;
}

export interface AnalyticsSummary {
  totalConversations: number;
  memoryEntries: number;
  apiUsage: number;
  avgResponseTime: number;
  emotionDistribution: Record<EmotionLabel, number>;
  mostUsedCommands: string[];
}

export interface ChatRequest {
  question: string;
  context: ChatMessage[];
  model: ModelOption;
}
