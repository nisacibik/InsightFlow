import { Platform } from 'react-native';
import Constants from 'expo-constants';

export const DEV_LAN_IP = '192.168.1.188';

function getBaseUrl() {
  const hostUri =
    Constants.expoConfig?.hostUri ||
    (Constants as any).manifest2?.extra?.expoGo?.debuggerHost ||
    (Constants as any).manifest?.debuggerHost ||
    '';

  const ipMatch = String(hostUri).match(/(\d{1,3}(?:\.\d{1,3}){3})/);
  if (ipMatch) {
    return `http://${ipMatch[1]}:3001`;
  }

  return `http://${DEV_LAN_IP}:3001`;
}

export const API_BASE_URL = getBaseUrl();

export const ENDPOINTS = {
  health: '/api/health',
  login: '/api/auth/login',
  register: '/api/auth/register',
  logout: '/api/auth/logout',
  me: '/api/auth/me',
  datasets: '/api/datasets',
  reviews: '/api/reviews',
  reviewsSummary: '/api/reviews/stats/summary',
  sentimentDistribution: '/api/analysis/sentiment-distribution',
  ratingDistribution: '/api/analysis/rating-distribution',
  topPainPoints: '/api/analysis/top-pain-points',
  topFeatureRequests: '/api/analysis/top-feature-requests',
  topics: '/api/analysis/topics',
  dashboard: '/api/analysis/dashboard',
  companyMe: '/api/company/me',
  companyCreate: '/api/company',
};
