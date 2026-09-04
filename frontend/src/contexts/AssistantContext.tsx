import { createContext, ReactNode, useCallback, useMemo, useState } from 'react';
import { ChatMessage, EmotionLabel, MemoryEntry, ModelOption, VoiceStatus } from '../types';

interface AssistantContextState {
  currentModel: ModelOption;
  voiceStatus: VoiceStatus;
  emotion: {
    label: EmotionLabel;
    confidence: number;
  };
  memoryEntries: MemoryEntry[];
  chatHistory: ChatMessage[];
  selectedConversationId: string | null;
  setModel: (model: ModelOption) => void;
  setVoiceStatus: (status: VoiceStatus) => void;
  addMessage: (message: Omit<ChatMessage, 'id' | 'createdAt'>) => void;
  clearChat: () => void;
  updateEmotion: (label: EmotionLabel, confidence: number) => void;
  addMemoryEntry: (entry: Omit<MemoryEntry, 'id' | 'createdAt'>) => void;
  deleteMemoryEntry: (id: string) => void;
  clearMemory: () => void;
}

const defaultEmotion = { label: 'Calm' as EmotionLabel, confidence: 0.86 };

export const AssistantContext = createContext<AssistantContextState>({
  currentModel: 'claude',
  voiceStatus: 'idle',
  emotion: defaultEmotion,
  memoryEntries: [],
  chatHistory: [],
  selectedConversationId: null,
  setModel: () => {},
  setVoiceStatus: () => {},
  addMessage: () => {},
  clearChat: () => {},
  updateEmotion: () => {},
  addMemoryEntry: () => {},
  deleteMemoryEntry: () => {},
  clearMemory: () => {},
});

interface AssistantProviderProps {
  children: ReactNode;
}

export function AssistantProvider({ children }: AssistantProviderProps) {
  const [currentModel, setCurrentModel] = useState<ModelOption>('claude');
  const [voiceStatus, setVoiceStatus] = useState<VoiceStatus>('idle');
  const [emotion, setEmotion] = useState(defaultEmotion);
  const [memoryEntries, setMemoryEntries] = useState<MemoryEntry[]>([]);
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);

  const addMessage = useCallback((message: Omit<ChatMessage, 'id' | 'createdAt'>) => {
    setChatHistory((prev) => [
      ...prev,
      {
        ...message,
        id: crypto.randomUUID(),
        createdAt: new Date().toISOString(),
      },
    ]);
  }, []);

  const clearChat = useCallback(() => {
    setChatHistory([]);
  }, []);

  const addMemoryEntry = useCallback((entry: Omit<MemoryEntry, 'id' | 'createdAt'>) => {
    setMemoryEntries((prev) => [
      {
        ...entry,
        id: crypto.randomUUID(),
        createdAt: new Date().toISOString(),
      },
      ...prev,
    ]);
  }, []);

  const deleteMemoryEntry = useCallback((id: string) => {
    setMemoryEntries((prev) => prev.filter((entry) => entry.id !== id));
  }, []);

  const clearMemory = useCallback(() => {
    setMemoryEntries([]);
  }, []);

  const updateEmotion = useCallback((label: EmotionLabel, confidence: number) => {
    setEmotion({ label, confidence });
  }, []);

  const value = useMemo(
    () => ({
      currentModel,
      voiceStatus,
      emotion,
      memoryEntries,
      chatHistory,
      selectedConversationId: null,
      setModel: setCurrentModel,
      setVoiceStatus,
      addMessage,
      clearChat,
      updateEmotion,
      addMemoryEntry,
      deleteMemoryEntry,
      clearMemory,
    }),
    [currentModel, voiceStatus, emotion, memoryEntries, chatHistory, addMessage, clearChat, updateEmotion, addMemoryEntry, deleteMemoryEntry, clearMemory]
  );

  return <AssistantContext.Provider value={value}>{children}</AssistantContext.Provider>;
}
