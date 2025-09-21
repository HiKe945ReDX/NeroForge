const express = require('express');
const cors = require('cors');
const multer = require('multer');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
const PORT = process.env.API_GATEWAY_PORT || 3000;

// Middleware
app.use(cors({
    origin: ['http://localhost:3000', 'http://localhost:4000'],
    credentials: true
}));
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        services: {
            'user-service': 'http://user-service:5001',
            'ai-guidance': 'http://ai-guidance:5002',
            'career-atlas': 'http://career-atlas:5003',
            'portfolio': 'http://portfolio-service:5004',
            'gamification': 'http://gamification-service:5005',
            'simulation': 'http://simulation-service:5006',
            'mock-interview': 'http://mock-interview:5008',
            'notification': 'http://notification-service:5009',
            'news-feeds': 'http://news-feeds-service:5010'
        },
        timestamp: new Date().toISOString()
    });
});

// Service routes
app.get('/services', (req, res) => {
    res.json({
        services: [
            'user-service', 'ai-guidance', 'career-atlas', 'portfolio',
            'gamification', 'simulation', 'mock-interview', 'notification', 'news-feeds'
        ]
    });
});

// Proxy routes to services
app.use('/api/users', createProxyMiddleware({
    target: 'http://user-service:5001',
    changeOrigin: true,
    pathRewrite: { '^/api/users': '' }
}));

app.use('/api/ai', createProxyMiddleware({
    target: 'http://ai-guidance:5002',
    changeOrigin: true,
    pathRewrite: { '^/api/ai': '' }
}));

app.use('/api/career', createProxyMiddleware({
    target: 'http://career-atlas:5003',
    changeOrigin: true,
    pathRewrite: { '^/api/career': '' }
}));

app.use('/api/portfolio', createProxyMiddleware({
    target: 'http://portfolio-service:5004',
    changeOrigin: true,
    pathRewrite: { '^/api/portfolio': '' }
}));

app.use('/api/game', createProxyMiddleware({
    target: 'http://gamification-service:5005',
    changeOrigin: true,
    pathRewrite: { '^/api/game': '' }
}));

app.use('/api/simulation', createProxyMiddleware({
    target: 'http://simulation-service:5006',
    changeOrigin: true,
    pathRewrite: { '^/api/simulation': '' }
}));

app.use('/api/interview', createProxyMiddleware({
    target: 'http://mock-interview:5008',
    changeOrigin: true,
    pathRewrite: { '^/api/interview': '' }
}));

app.use('/api/notifications', createProxyMiddleware({
    target: 'http://notification-service:5009',
    changeOrigin: true,
    pathRewrite: { '^/api/notifications': '' }
}));

app.use('/api/news', createProxyMiddleware({
    target: 'http://news-feeds-service:5010',
    changeOrigin: true,
    pathRewrite: { '^/api/news': '' }
}));

app.listen(PORT, '0.0.0.0', () => {
    console.log(`🌐 API Gateway running on port ${PORT}`);
    console.log(`🚀 All service routes configured`);
});
