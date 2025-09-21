import axios from 'axios';
import toast from 'react-hot-toast';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:3000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.message || error.message || 'Something went wrong!';
    toast.error(message);
    return Promise.reject(error);
  }
);

// API Services
export const userService = {
  register: (data) => api.post('/user-service/register', data),
  getProfile: (userId) => api.get(`/user-service/profile/${userId}`),
  updateProfile: (userId, data) => api.put(`/user-service/profile/${userId}`, data),
  logActivity: (data) => api.post('/user-service/activity/log', data),
  getActivities: (userId) => api.get(`/user-service/activity/user/${userId}`),
};

export const aiService = {
  analyzeResume: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/ai-guidance/analyze-resume', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  createPersona: (data) => api.post('/ai-guidance/create-persona', data),
  psychometricAssessment: (data) => api.post('/ai-guidance/psychometric-assessment', data),
  generateRoadmap: (data) => api.post('/ai-guidance/generate-roadmap', data),
  analyzeGitHub: (data) => api.post('/ai-guidance/github/analyze', data),
  optimizeLinkedIn: (data) => api.post('/ai-guidance/linkedin/optimize', data),
  careerMatch: (data) => api.post('/ai-guidance/career/match', data),
  skillsGapAnalysis: (data) => api.post('/ai-guidance/skills/gap-analysis', data),
};

export const careerService = {
  getCareerPaths: (data) => api.post('/career-atlas/career-paths', data),
  getKnowledgeGraph: (params) => api.get('/career-atlas/knowledge-graph', { params }),
  mapSkills: (data) => api.post('/career-atlas/skills/map', data),
  getAIEngineerKnowledge: () => api.get('/career-atlas/knowledge/ai-engineer'),
  getMarketAnalysis: (params) => api.get('/career-atlas/market/analysis', { params }),
  getMLInsights: () => api.get('/career-atlas/insights/machine-learning'),
};

export const portfolioService = {
  generatePortfolio: (data) => api.post('/portfolio/generate-portfolio', data),
  getTemplates: () => api.get('/portfolio/templates'),
  exportPortfolio: (data) => api.post('/portfolio/export', data),
};

export const gamificationService = {
  awardPoints: (data) => api.post('/gamification/points/award', data),
  getUserPoints: (userId) => api.get(`/gamification/points/${userId}`),
  getAchievements: () => api.get('/gamification/achievements'),
  getUserAchievements: (userId) => api.get(`/gamification/achievements/${userId}`),
  getLeaderboard: (type = 'global') => api.get(`/gamification/leaderboard/${type}`),
};

export const interviewService = {
  generateQuestions: (data) => api.post('/mock-interview/questions/generate', data),
  startSession: (data) => api.post('/mock-interview/session/start', data),
  submitFeedback: (data) => api.post('/mock-interview/feedback/submit', data),
};

export const simulationService = {
  simulate: (data) => api.post('/simulation/simulate', data),
  analyzeRisk: (data) => api.post('/simulation/risk/analyze', data),
};

export const notificationService = {
  send: (data) => api.post('/notification/send', data),
  getPreferences: (userId) => api.get(`/notification/preferences/${userId}`),
  getHistory: (userId) => api.get(`/notification/history/${userId}`),
};

export const newsService = {
  getFeed: (userId) => api.get(`/news-feeds/feed/${userId}`),
  getCareerNews: () => api.get('/news-feeds/news/career'),
  getTechNews: () => api.get('/news-feeds/news/technology'),
  getTrending: () => api.get('/news-feeds/trending'),
};

export default api;
