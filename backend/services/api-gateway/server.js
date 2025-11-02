const http = require('http');
const PORT = process.env.PORT || 8080;

const server = http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'application/json' });
  
  if (req.url === '/health') {
    res.end(JSON.stringify({ ok: true }));
  } else if (req.url === '/') {
    res.end(JSON.stringify({ message: 'API Gateway OK' }));
  } else {
    res.writeHead(404);
    res.end(JSON.stringify({ error: 'Not Found' }));
  }
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`✅ Server listening on port ${PORT}`);
  process.stdout.write('');
});

process.on('SIGTERM', () => process.exit(0));
