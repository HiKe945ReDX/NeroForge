const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const { createProxyMiddleware } = require('http-proxy-middleware');
const { CONFIG, getServiceUrl, validateConfig, isProduction } = require('./config');

const app = express();
const PORT = CONFIG.port;

try {
  validateConfig();
} catch (error) {
  console.error('❌ Configuration validation failed:', error.message);
  process.exit(1);
}

app.use(helmet());
app.use(cors());
app.use(morgan('combined'));
app.use(express.json());

app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'api-gateway',
    environment: CONFIG.environment,
    timestamp: new Date().toISOString()
  });
});

const createProxy = (serviceName, pathRewrite = {}) => {
  const target = getServiceUrl(serviceName);
  
  if (!target) {
    console.error(`❌ Service URL not found for: ${serviceName}`);
    return (req, res) => {
      res.status(503).json({
        error: 'Service Unavailable',
        message: `Service ${serviceName} is not configured`
      });
    };
  }

  return createProxyMiddleware({
    target,
    changeOrigin: true,
    pathRewrite,
    timeout: CONFIG.proxyTimeout,
    logLevel: CONFIG.logLevel === 'debug' ? 'debug' : 'warn',
    onProxyReq: (proxyReq, req) => {
      console.log(`→ Proxying to ${serviceName}: ${target}${req.path}`);
    },
    onProxyRes: (proxyRes, req) => {
      console.log(`← Response from ${serviceName}: ${proxyRes.statusCode}`);
    },
    onError: (err, req, res) => {
      console.error(`❌ Proxy Error (${serviceName}):`, err.message);
      res.status(502).json({
        error: 'Bad Gateway',
        service: serviceName,
        message: err.message,
        timestamp: new Date().toISOString()
      });
    }
  });
};

app.use('/api/users', createProxy('users', { '^/api/users': '' }));
app.use('/api/ai', createProxy('ai-guidance', { '^/api/ai': '' }));
app.use('/api/careers', createProxy('career-atlas', { '^/api/careers': '' }));
app.use('/api/portfolio', createProxy('portfolio', { '^/api/portfolio': '' }));
app.use('/api/gamification', createProxy('gamification', { '^/api/gamification': '' }));
app.use('/api/simulation', createProxy('simulation', { '^/api/simulation': '' }));
app.use('/api/context', createProxy('context', { '^/api/context': '' }));
app.use('/api/interview', createProxy('interview', { '^/api/interview': '' }));
app.use('/api/notifications', createProxy('notifications', { '^/api/notifications': '' }));
app.use('/api/news', createProxy('news', { '^/api/news': '' }));

app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Not Found',
    message: `Route ${req.originalUrl} does not exist`,
    timestamp: new Date().toISOString()
  });
});

app.use((err, req, res, next) => {
  console.error('❌ Unhandled error:', err);
  res.status(500).json({
    error: 'Internal Server Error',
    message: err.message,
    timestamp: new Date().toISOString()
  });
});

app.listen(PORT, () => {
  console.log('');
  console.log('='.repeat(60));
  console.log('✅ GUIDORA API GATEWAY - RUNNING');
  console.log('='.repeat(60));
  console.log(`🌍 Environment: ${CONFIG.environment}`);
  console.log(`🚀 Port: ${PORT}`);
  console.log(`📡 Services: 10 configured`);
  console.log('='.repeat(60));
  console.log('');
});

module.exports = app;
