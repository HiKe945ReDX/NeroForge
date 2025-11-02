// frontend/src/services/api.js
// Complete API client with ALL endpoints from your API Gateway

import axios from 'axios';

const GATEWAY_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001';

const apiClient = axios.create({
  baseURL: GATEWAY_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Add token interceptor for all requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response error interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ========== AUTH API (USER SERVICE) ==========
export const authAPI = {
  login: (credentials) => apiClient.post('/api/users/auth/login', credentials),
  signup: (userData) => apiClient.post('/api/users/auth/signup', userData),
  logout: () => apiClient.post('/api/users/auth/logout'),
  refresh: () => apiClient.post('/api/users/auth/refresh'),
  verifyEmail: (token) => apiClient.post('/api/users/auth/verify-email', { token }),
  resetPassword: (data) => apiClient.post('/api/users/auth/reset-password', data),
};

// ========== ONBOARDING API (USER SERVICE) ==========
export const onboardingAPI = {
  step1BasicInfo: (data) => apiClient.post('/api/users/onboarding/step1/basic-info', data),
  step2UploadExperience: (data) => apiClient.post('/api/users/onboarding/step2/upload-experience', data),
  step3SkillsPicker: (data) => apiClient.post('/api/users/onboarding/step3/skills-picker', data),
  step4Psychometric: (data) => apiClient.post('/api/users/onboarding/step4/psychometric-submit', data),
  step5Empathy: (data) => apiClient.post('/api/users/onboarding/step5/empathy-submit', data),
  step6CareerPreferences: (data) => apiClient.post('/api/users/onboarding/step6/career-preferences', data),
  getStatus: () => apiClient.get('/api/users/onboarding/status'),
};

// ========== CAREER DISCOVERY API (CAREER ATLAS SERVICE) ==========
export const careerAPI = {
  discover: (answers) => apiClient.post('/api/careers/discover/suggest-careers', { answers }),
  getRecommendations: (userId) => apiClient.get(`/api/careers/${userId}/recommendations`),
  getCareerById: (careerId) => apiClient.get(`/api/careers/${careerId}`),
  searchCareers: (query) => apiClient.get('/api/careers/search', { params: { query } }),
};

// ========== AI GUIDANCE API (AI GUIDANCE SERVICE) ==========
export const aiAPI = {
  getPsychometricQuestions: () => apiClient.get('/api/ai/psychometric/questions'),
  submitPsychometric: (answers) => apiClient.post('/api/ai/psychometric/complete', { answers }),
  getEmpathyQuestions: () => apiClient.get('/api/empathy/questions'),
  submitEmpathy: (answers) => apiClient.post('/api/empathy/assess', { answers }),
  generateRoadmap: (userId, careerGoals) =>
    apiClient.post(`/api/ai/roadmap/generate`, { userId, careerGoals }),
};

// ========== USER PREFERENCES & PROFILE API ==========
export const userAPI = {
  getProfile: () => apiClient.get('/api/users/profile'),
  updateProfile: (data) => apiClient.put('/api/users/profile', data),
  getPreferences: () => apiClient.get('/api/users/preferences'),
  savePreferences: (preferences) => apiClient.post('/api/users/preferences/save', preferences),
  getActivity: () => apiClient.get('/api/users/activity'),
  getActivityStats: () => apiClient.get('/api/users/activity/stats'),
};

// ========== SKILLS API ==========
export const skillsAPI = {
  getAllSkills: () => apiClient.get('/api/users/skills'),
  searchSkills: (query) => apiClient.get('/api/users/skills/search', { params: { q: query } }),
  getSkillsByCategory: (category) => apiClient.get(`/api/users/skills/category/${category}`),
};

// ========== PORTFOLIO API (PORTFOLIO SERVICE) ==========
export const portfolioAPI = {
  getPortfolio: (userId) => apiClient.get(`/api/portfolio/${userId}`),
  updatePortfolio: (data) => apiClient.put('/api/portfolio', data),
  addProject: (project) => apiClient.post('/api/portfolio/projects', project),
  removeProject: (projectId) => apiClient.delete(`/api/portfolio/projects/${projectId}`),
};

// ========== GAMIFICATION API (GAMIFICATION SERVICE) ==========
export const gamificationAPI = {
  getChallenges: (filters) => apiClient.get('/api/gamification/challenges', { params: filters }),
  joinChallenge: (challengeId) => apiClient.post(`/api/gamification/challenges/${challengeId}/join`),
  updateProgress: (challengeId, progress) =>
    apiClient.post(`/api/gamification/challenges/${challengeId}/progress`, progress),
  getAchievements: () => apiClient.get('/api/gamification/achievements'),
  getLeaderboard: () => apiClient.get('/api/gamification/leaderboard'),
  getPoints: () => apiClient.get('/api/gamification/points'),
};

// ========== INTERVIEW PREP API (MOCK INTERVIEW SERVICE) ==========
export const interviewAPI = {
  createSession: (config) => apiClient.post('/api/interview/sessions/create', config),
  getQuestions: (sessionId) => apiClient.get(`/api/interview/sessions/${sessionId}/questions`),
  submitResponse: (sessionId, response) =>
    apiClient.post(`/api/interview/sessions/${sessionId}/response`, response),
  getSessionFeedback: (sessionId) => apiClient.get(`/api/interview/sessions/${sessionId}/feedback`),
};

// ========== SIMULATION API (SIMULATION SERVICE) ==========
export const simulationAPI = {
  startSimulation: (type) => apiClient.post('/api/simulation/start', { type }),
  submitAnswer: (simulationId, answer) =>
    apiClient.post(`/api/simulation/${simulationId}/answer`, { answer }),
  getResults: (simulationId) => apiClient.get(`/api/simulation/${simulationId}/results`),
};

// ========== NOTIFICATIONS API (NOTIFICATIONS SERVICE) ==========
export const notificationsAPI = {
  getNotifications: () => apiClient.get('/api/notifications'),
  markAsRead: (notificationId) =>
    apiClient.put(`/api/notifications/${notificationId}/read`),
  deleteNotification: (notificationId) =>
    apiClient.delete(`/api/notifications/${notificationId}`),
};

// ========== NEWS/UPDATES API (NEWS FEEDS SERVICE) ==========
export const newsAPI = {
  getUpdates: () => apiClient.get('/api/news/updates'),
  getByCategory: (category) => apiClient.get(`/api/news/category/${category}`),
};

export default apiClient;
