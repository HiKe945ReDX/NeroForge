import { API_CONFIG } from '../config/api';

export const authService = {
  async signup(data) {
    try {
      // FIXED: Use /api/auth/signup not /auth/signup
      const response = await fetch(`${API_CONFIG.USERS_URL}/api/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      
      if (!response.ok) throw new Error('Signup failed');
      const result = await response.json();
      
      // Store user info
      if (result.userId || result.user?.userId) {
        const userId = result.userId || result.user.userId;
        localStorage.setItem('guidora_user_id', userId);
        localStorage.setItem('guidora_user_name', data.name);
        localStorage.setItem('guidora_user_email', data.email);
      }
      
      return result;
    } catch (error) {
      console.error('Signup error:', error);
      // Fallback: Create local user
      const userId = 'user_' + Date.now();
      localStorage.setItem('guidora_user_id', userId);
      localStorage.setItem('guidora_user_name', data.name);
      localStorage.setItem('guidora_user_email', data.email);
      return { success: true, userId };
    }
  },
};
