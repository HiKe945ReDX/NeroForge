const express = require('express');
const app = express();

const PORT = process.env.PORT || 8080;

app.get('/health', (req, res) => res.status(200).json({ ok: true }));
app.get('/', (req, res) => res.json({ message: 'API Gateway OK' }));
app.listen(PORT, '0.0.0.0', () => console.log(`✅ Listening on ${PORT}`));
