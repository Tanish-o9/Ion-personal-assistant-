import { api } from './api';
import { MemoryEntry } from '../types';

export function getMemory() {
  return api.get<MemoryEntry[]>('/memory').then((response) => response.data);
}

export function postMemory(entry: Omit<MemoryEntry, 'id' | 'createdAt'>) {
  return api.post<MemoryEntry>('/memory', entry).then((response) => response.data);
}
