import { api } from './api';

export interface VoicePayload {
  audioInput?: string;
  audio_base64?: string;
  session_id?: string;
  model?: string;
}

export function postVoice(payload: VoicePayload) {
  return api.post('/voice', {
    text_input: payload.audioInput,
    audioInput: payload.audioInput,
    audio_base64: payload.audio_base64 || '',
    session_id: payload.session_id,
    model: payload.model,
  }).then((response) => response.data);
}
