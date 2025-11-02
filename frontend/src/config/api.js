const API_BASE = process.env.REACT_APP_API_URL || 'https://guidora-gateway-746485305795.us-central1.run.app';
export const API_ENDPOINTS = { AUTH_LOGIN: `${API_BASE}/api/auth/login`, AUTH_SIGNUP: `${API_BASE}/api/auth/signup`, CAREERS_LIST: `${API_BASE}/api/careers`, CAREER_DETAIL: (id) => `${API_BASE}/api/careers/${id}`, CAREER_MARKET: (id) => `${API_BASE}/api/careers/${id}/market`, CAREER_JOBS: (id) => `${API_BASE}/api/careers/${id}/jobs`, AI_ROADMAP: `${API_BASE}/api/ai/roadmap/generate`, };
export const API_CONFIG = API_ENDPOINTS;
export default API_ENDPOINTS;
