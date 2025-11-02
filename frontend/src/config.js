// Frontend API Configuration
const isProduction = process.env.NODE_ENV === 'production';

export const API_CONFIG = {
  GATEWAY_URL: isProduction 
    ? 'https://guidora-gateway-746485305795.us-central1.run.app' 
    : 'http://localhost:8080',
  
  // Direct service URLs (deprecated - use gateway)
  USER_SERVICE: isProduction
    ? 'https://guidora-users-746485305795.us-central1.run.app'
    : 'http://localhost:5001',
    
  AI_SERVICE: isProduction
    ? 'https://guidora-ai-746485305795.us-central1.run.app'
    : 'http://localhost:5002',
};

// Export individual URLs for backwards compatibility
export const GATEWAY_URL = API_CONFIG.GATEWAY_URL;
export const USER_SERVICE_URL = API_CONFIG.USER_SERVICE;
export const AI_SERVICE_URL = API_CONFIG.AI_SERVICE;

export default API_CONFIG;
