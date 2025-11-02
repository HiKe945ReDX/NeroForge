const isProduction = process.env.NODE_ENV === 'production';

const CONFIG = {
  environment: isProduction ? 'production' : 'development',
  port: process.env.PORT || 8080,
  
  services: {
    local: {
      users: 'http://user-service:5001',
      'ai-guidance': 'http://ai-guidance:5002',
      'career-atlas': 'http://career-atlas:5003',
      portfolio: 'http://portfolio:5004',
      gamification: 'http://gamification:5005',
      simulation: 'http://simulation:5006',
      context: 'http://context-service:5007',
      interview: 'http://mock-interview:5008',
      notifications: 'http://notifications:5009',
      news: 'http://news-feeds:5010',
    },
    production: {
      users: 'https://guidora-users-746485305795.us-central1.run.app',
      'ai-guidance': 'https://guidora-ai-746485305795.us-central1.run.app',
      'career-atlas': 'https://guidora-career-746485305795.us-central1.run.app',
      portfolio: 'https://guidora-portfolio-746485305795.us-central1.run.app',
      gamification: 'https://guidora-gamify-746485305795.us-central1.run.app',
      simulation: 'https://guidora-simulation-746485305795.us-central1.run.app',
      context: 'https://guidora-context-746485305795.us-central1.run.app',
      interview: 'https://guidora-interview-746485305795.us-central1.run.app',
      notifications: 'https://guidora-notifications-746485305795.us-central1.run.app',
      news: 'https://guidora-news-746485305795.us-central1.run.app',
    }
  },
  logLevel: process.env.LOG_LEVEL || 'info',
  proxyTimeout: parseInt(process.env.PROXY_TIMEOUT) || 60000,
};

function getServiceMap() {
  return CONFIG.services[isProduction ? 'production' : 'local'];
}

function getServiceUrl(serviceName) {
  const serviceMap = getServiceMap();
  if (!serviceMap[serviceName]) {
    console.warn(`⚠️ Service ${serviceName} not found in config`);
    return null;
  }
  return serviceMap[serviceName];
}

function validateConfig() {
  const serviceMap = getServiceMap();
  console.log(`✅ Configuration validated for ${CONFIG.environment} environment`);
  console.log(`✅ Available services: ${Object.keys(serviceMap).join(', ')}`);
}

module.exports = { CONFIG, getServiceMap, getServiceUrl, validateConfig, isProduction };
