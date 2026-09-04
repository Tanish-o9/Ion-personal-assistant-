import { api } from './api';
import { AnalyticsSummary } from '../types';

export function getAnalytics() {
  return api.get<AnalyticsSummary>('/analytics').then((response) => response.data);
}
