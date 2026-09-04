import { api } from './api';
import { EmotionRecord } from '../types';

export function getEmotionHistory() {
  return api.get<EmotionRecord[]>('/emotion').then((response) => response.data);
}
