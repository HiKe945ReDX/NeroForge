/**
 * GUIDORA API GATEWAY - Advanced Health Check
 * Checks health of all backend services
 */

const express = require('express');
const { getServiceMap } = require('./config');

const router = express.Router();

/**
 * Comprehensive health check - pings all services
 */
router.get('/health/full', async (req, res) => {
  try {
    const serviceMap = getServiceMap();
    const serviceNames = Object.keys(serviceMap);
    
    console.log(`🔍 Running full health check for ${serviceNames.length} services...`);
    
    const healthChecks = await Promise.allSettled(
      serviceNames.map(async (serviceName) => {
        const serviceUrl = serviceMap[serviceName];
        const healthUrl = `${serviceUrl}/health`;
        
        try {
          const controller = new AbortController();
          const timeout = setTimeout(() => controller.abort(), 5000);
          
          const response = await fetch(healthUrl, {
            signal: controller.signal,
            headers: { 'User-Agent': 'Guidora-API-Gateway/1.0' }
          });
          
          clearTimeout(timeout);
          
          return {
            service: serviceName,
            url: serviceUrl,
            status: response.ok ? 'healthy' : 'unhealthy',
            statusCode: response.status,
            responseTime: response.headers.get('x-response-time') || 'N/A'
          };
        } catch (error) {
          return {
            service: serviceName,
            url: serviceUrl,
            status: 'error',
            error: error.message
          };
        }
      })
    );

    // Aggregate results
    const results = healthChecks.map((result, index) => {
      if (result.status === 'fulfilled') {
        return result.value;
      } else {
        return {
          service: serviceNames[index],
          url: serviceMap[serviceNames[index]],
          status: 'error',
          error: result.reason?.message || 'Unknown error'
        };
      }
    });

    const healthyCount = results.filter(r => r.status === 'healthy').length;
    const totalCount = results.length;
    const allHealthy = healthyCount === totalCount;

    res.status(allHealthy ? 200 : 503).json({
      status: allHealthy ? 'healthy' : 'degraded',
      summary: `${healthyCount}/${totalCount} services healthy`,
      services: results,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('❌ Health check failed:', error);
    res.status(500).json({
      status: 'error',
      message: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * Quick health check (just API Gateway)
 */
router.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'api-gateway',
    timestamp: new Date().toISOString()
  });
});

module.exports = router;
