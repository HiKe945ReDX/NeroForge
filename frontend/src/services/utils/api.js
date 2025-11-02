import { API_ENDPOINTS } from '../config/api';

class ApiClient {
  constructor() {
    this.userId = localStorage.getItem('guidora_user_id') || null;
  }

  async request(url, options = {}) {
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Step 1: Basic Info
  async registerUser(userData) {
    const response = await this.request(API_ENDPOINTS.REGISTER, {
      method: 'POST',
      body: JSON.stringify(userData),
    });
    
    if (response.userId) {
      this.userId = response.userId;
      localStorage.setItem('guidora_user_id', response.userId);
    }
    
    return response;
  }

  // Step 2: Skills
  async searchSkills(query) {
    return await this.request(`${API_ENDPOINTS.SKILLS_SEARCH}?q=${encodeURIComponent(query)}`);
  }

  async getAllSkills() {
    return await this.request(API_ENDPOINTS.SKILLS_ALL);
  }

  // Step 3: Psychometric Test
  async getPsychometricQuestions() {
    return await this.request(API_ENDPOINTS.PSYCHOMETRIC_QUESTIONS);
  }

  async submitPsychometric(answers) {
    return await this.request(API_ENDPOINTS.PSYCHOMETRIC_COMPLETE, {
      method: 'POST',
      body: JSON.stringify({
        userId: this.userId,
        answers,
      }),
    });
  }

  // Step 4: Empathy Test
  async getEmpathyQuestions() {
    return await this.request(API_ENDPOINTS.EMPATHY_QUESTIONS);
  }

  async submitEmpathy(answers) {
    return await this.request(API_ENDPOINTS.EMPATHY_COMPLETE, {
      method: 'POST',
      body: JSON.stringify({
        userId: this.userId,
        responses: answers,
      }),
    });
  }

  // Step 5: Career Preferences
  async saveCareerPreferences(preferences) {
    return await this.request(API_ENDPOINTS.CAREER_PREFERENCES, {
      method: 'POST',
      body: JSON.stringify({
        userId: this.userId,
        ...preferences,
      }),
    });
  }

  // Get User Profile
  async getUserProfile() {
    if (!this.userId) return null;
    return await this.request(API_ENDPOINTS.USER_PROFILE(this.userId));
  }
}

export default new ApiClient();
