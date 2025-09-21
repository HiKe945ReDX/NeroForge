import axios from 'axios';

// API Base URLs
const API_BASE_URL = 'http://localhost:3000/api/v1';
const AI_GUIDANCE_URL = 'http://localhost:5002';
const CAREER_ATLAS_URL = 'http://localhost:5003';
const PORTFOLIO_URL = 'http://localhost:5004';
const GAMIFICATION_URL = 'http://localhost:5005';

// Create axios instances
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

const aiClient = axios.create({
  baseURL: AI_GUIDANCE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

const careerClient = axios.create({
  baseURL: CAREER_ATLAS_URL,
  timeout: 30000,
});

const portfolioClient = axios.create({
  baseURL: PORTFOLIO_URL,
  timeout: 30000,
});

const gamificationClient = axios.create({
  baseURL: GAMIFICATION_URL,
  timeout: 30000,
});

// Interceptors for error handling
const handleApiError = (error) => {
  console.error('API Error:', error);
  if (error.response?.status === 404) {
    return { error: 'Service not available', data: null };
  }
  return { error: error.message || 'Service error', data: null };
};

apiClient.interceptors.response.use(
  (response) => response,
  handleApiError
);

// AI Guidance Service
export const aiGuidanceService = {
  // Resume Analysis
  analyzeResume: async (resumeData) => {
    try {
      const response = await aiClient.post('/analyze-resume', resumeData);
      return { data: response.data, error: null };
    } catch (error) {
      console.log('Resume analysis service unavailable, using demo data');
      return {
        data: {
          analysis: {
            strengths: [
              "Strong technical skills in AI/ML and full-stack development",
              "Good project portfolio with practical applications", 
              "Solid educational background in relevant field"
            ],
            improvements: [
              "Add more quantifiable achievements and metrics",
              "Include leadership and soft skills examples",
              "Expand on internship responsibilities and impact"
            ],
            score: 78,
            recommendations: [
              "Highlight specific technologies used in projects",
              "Add metrics to demonstrate project impact",
              "Include relevant certifications and courses"
            ]
          }
        },
        error: null
      };
    }
  },

  // Career Roadmap Generation
  generateRoadmap: async (profileData) => {
    try {
      const response = await aiClient.post('/generate-roadmap', profileData);
      return { data: response.data, error: null };
    } catch (error) {
      console.log('Roadmap generation service unavailable, using demo data');
      return {
        data: {
          roadmap: {
            title: "AI Engineering Career Path",
            timeline: "2-3 years",
            phases: [
              {
                phase: "Foundation Building (Months 1-6)",
                skills: ["Python Mastery", "ML Algorithms", "Data Structures"],
                resources: ["Machine Learning Specialization", "LeetCode Practice"],
                milestones: ["Build 3 ML projects", "Get Python certification"]
              },
              {
                phase: "Specialization (Months 7-18)", 
                skills: ["Deep Learning", "Cloud Platforms", "MLOps"],
                resources: ["Deep Learning Specialization", "AWS ML Training"],
                milestones: ["Deploy ML models to production", "Get cloud certification"]
              },
              {
                phase: "Advanced Practice (Months 19-36)",
                skills: ["Research", "System Design", "Leadership"],
                resources: ["Research Papers", "System Design Interviews"],
                milestones: ["Lead ML projects", "Publish research/articles"]
              }
            ]
          }
        },
        error: null
      };
    }
  },

  // Skill Gap Analysis
  analyzeSkillGaps: async (currentSkills, targetRole) => {
    try {
      const response = await aiClient.post('/analyze-skill-gaps', { currentSkills, targetRole });
      return { data: response.data, error: null };
    } catch (error) {
      console.log('Skill gap analysis service unavailable, using demo data');
      return {
        data: {
          skillGaps: {
            missing: ["Kubernetes", "Apache Kafka", "System Design"],
            developing: ["MLOps", "Cloud Architecture", "Team Leadership"],
            strong: ["Python", "Machine Learning", "FastAPI", "React"],
            recommendations: [
              "Focus on learning container orchestration with Kubernetes",
              "Practice system design for scalable ML systems",
              "Gain experience with streaming data using Kafka"
            ]
          }
        },
        error: null
      };
    }
  }
};

// Career Atlas Service  
export const careerAtlasService = {
  // Get Career Insights
  getCareerInsights: async (field) => {
    try {
      const response = await careerClient.get(`/insights/${field}`);
      return { data: response.data, error: null };
    } catch (error) {
      console.log('Career insights service unavailable, using demo data');
      return {
        data: {
          insights: {
            field: "Artificial Intelligence",
            overview: "AI is one of the fastest-growing tech fields with high demand across industries.",
            trends: [
              "Increased adoption of generative AI in enterprises",
              "Growing focus on AI ethics and responsible AI",
              "Rise of AI-powered automation in various sectors"
            ],
            opportunities: [
              {
                role: "AI/ML Engineer",
                demand: "Very High", 
                salaryRange: "$120K-$200K",
                growth: "+22% annually"
              },
              {
                role: "Data Scientist",
                demand: "High",
                salaryRange: "$110K-$180K", 
                growth: "+19% annually"
              },
              {
                role: "AI Research Scientist",
                demand: "High",
                salaryRange: "$150K-$250K",
                growth: "+18% annually"
              }
            ]
          }
        },
        error: null
      };
    }
  },

  // Get Industry Trends
  getIndustryTrends: async () => {
    try {
      const response = await careerClient.get('/trends');
      return { data: response.data, error: null };
    } catch (error) {
      return {
        data: {
          trends: [
            {
              title: "Generative AI Revolution",
              impact: "High",
              description: "ChatGPT and similar models are transforming how businesses operate"
            },
            {
              title: "AI-Powered Automation",
              impact: "High", 
              description: "Companies are automating complex workflows using AI"
            },
            {
              title: "Edge AI Computing",
              impact: "Medium",
              description: "AI processing moving closer to data sources"
            }
          ]
        },
        error: null
      };
    }
  }
};

// Portfolio Service
export const portfolioService = {
  // Generate Portfolio
  generatePortfolio: async (userData) => {
    try {
      const response = await portfolioClient.post('/generate', userData);
      return { data: response.data, error: null };
    } catch (error) {
      return {
        data: {
          portfolio: {
            sections: [
              {
                title: "About Me",
                content: "AI & Data Science engineer passionate about building intelligent systems."
              },
              {
                title: "Projects", 
                content: "AI-powered resume analyzer, ML prediction models, full-stack applications."
              },
              {
                title: "Skills",
                content: "Python, TensorFlow, React, FastAPI, Docker, MongoDB, AWS."
              }
            ],
            template: "modern",
            preview_url: "/portfolio/preview"
          }
        },
        error: null
      };
    }
  }
};

// Gamification Service
export const gamificationService = {
  // Get User Points
  getUserPoints: async (userId) => {
    try {
      const response = await gamificationClient.get(`/points/${userId}`);
      return { data: response.data, error: null };
    } catch (error) {
      return {
        data: {
          points: {
            total_points: 2850,
            level: "Expert",
            streak: 12,
            weekly_points: 380
          }
        },
        error: null
      };
    }
  },

  // Get Leaderboard
  getLeaderboard: async () => {
    try {
      const response = await gamificationClient.get('/leaderboard/global');
      return { data: response.data, error: null };
    } catch (error) {
      return {
        data: {
          leaderboard: [
            { rank: 1, name: "Alex Chen", points: 3420, level: "Master" },
            { rank: 2, name: "Sarah Johnson", points: 3180, level: "Master" },
            { rank: 3, name: "Michael Rodriguez", points: 2950, level: "Expert" }
          ]
        },
        error: null
      };
    }
  }
};

// User Service
export const userService = {
  // Get Profile
  getProfile: async (userId) => {
    try {
      const response = await apiClient.get(`/users/${userId}`);
      return { data: response.data, error: null };
    } catch (error) {
      return { data: null, error: error.message };
    }
  },

  // Update Profile
  updateProfile: async (userId, profileData) => {
    try {
      const response = await apiClient.put(`/users/${userId}`, profileData);
      return { data: response.data, error: null };
    } catch (error) {
      return { data: null, error: error.message };
    }
  }
};

export default {
  aiGuidanceService,
  careerAtlasService,
  portfolioService,
  gamificationService,
  userService
};

// Mock Interview Service (for InterviewPrep page compatibility)
export const interviewService = {
  startSession: async () => {
    return { data: { sessionId: 'mock_session_123' }, error: null };
  },
  
  submitAnswer: async (questionId, answer) => {
    return { data: { success: true }, error: null };
  }
};

// Career Service (alias for careerAtlasService for compatibility)
export const careerService = careerAtlasService;
