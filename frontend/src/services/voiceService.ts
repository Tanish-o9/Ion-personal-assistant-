import { api } from './api';

export interface VoicePayload {
  audioInput: string;
  model: string;
}

export function postVoice(payload: VoicePayload) {
  return api.post('/voice', payload).then((response) => response.data);
}
