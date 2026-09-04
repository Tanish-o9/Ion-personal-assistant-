import { api } from './api';
import { ChatMessage } from '../types';

export function getHistory() {
  return api.get<ChatMessage[]>('/history').then((response) => response.data);
}
