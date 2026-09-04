import axios from 'axios';

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: apiBaseUrl,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.response?.data?.message || error.message || 'Unknown error';
    return Promise.reject(new Error(message));
  }
);

export async function fetchHealth() {
  const res = await api.get('/health');
  return res.data;
}

export async function fetchConversations() {
  const res = await api.get('/conversations');
  return res.data;
}

export async function fetchSessionMessages(sessionId: string) {
  const res = await api.get(`/conversations/${encodeURIComponent(sessionId)}/messages`);
  return res.data;
}

export async function fetchUserMemories(userId: string = 'default_user') {
  const res = await api.get(`/memory/${encodeURIComponent(userId)}`);
  return res.data;
}

export async function deleteUserMemory(userId: string, memoryId: string) {
  const res = await api.delete(`/memory/${encodeURIComponent(userId)}/${encodeURIComponent(memoryId)}`);
  return res.data;
}

export async function fetchUserProfile(userId: string = 'default_user') {
  const res = await api.get(`/profile/${encodeURIComponent(userId)}`);
  return res.data;
}

export async function submitJob(sessionId: string, jobType: string, payloadData: string = '') {
  const res = await api.post('/jobs', { session_id: sessionId, job_type: jobType, payload_data: payloadData });
  return res.data;
}

export async function fetchUserJobs() {
  const res = await api.get('/jobs');
  return res.data;
}

export async function cancelJob(jobId: string) {
  const res = await api.post(`/jobs/${encodeURIComponent(jobId)}/cancel`);
  return res.data;
}

export async function getAutomations() {
  const res = await api.get('/automations');
  return res.data;
}

export async function createAutomation(data: {
  name: string;
  workflow_text: string;
  schedule_cron?: string;
  timezone?: string;
}) {
  const res = await api.post('/automations', data);
  return res.data;
}

export async function runAutomation(id: string) {
  const res = await api.post(`/automations/${encodeURIComponent(id)}/run`);
  return res.data;
}

export async function pauseAutomation(id: string) {
  const res = await api.post(`/automations/${encodeURIComponent(id)}/pause`);
  return res.data;
}

export async function resumeAutomation(id: string) {
  const res = await api.post(`/automations/${encodeURIComponent(id)}/resume`);
  return res.data;
}

export async function deleteAutomation(id: string) {
  const res = await api.delete(`/automations/${encodeURIComponent(id)}`);
  return res.data;
}

export async function postChat(payload: {
  session_id?: string;
  text: string;
  files?: Array<{
    input_type: string;
    filename: string;
    mime_type?: string;
    content_base64: string;
  }>;
}) {
  const res = await api.post('/chat', payload);
  return res.data;
}

export async function postVoice(payload: {
  session_id?: string;
  audio_base64: string;
  audio_format?: string;
}) {
  const res = await api.post('/voice', payload);
  return res.data;
}
