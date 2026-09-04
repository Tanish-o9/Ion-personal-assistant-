import { api } from './api';
import { ChatRequest, ChatMessage } from '../types';

export interface ChatResponse {
  message: ChatMessage;
  responseTimeMs: number;
}

export function postChat(payload: ChatRequest) {
  return api.post<ChatResponse>('/chat', payload).then((response) => response.data);
}
