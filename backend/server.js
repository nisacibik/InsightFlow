const { initSchema } = require('./src/db/schema');
const { createApp } = require('./src/app');
const env = require('./src/config/environment');

const app = createApp();
const PORT = env.server.port;

async function start() {
  try {
    await initSchema();
  } catch (err) {
    console.error('Schema init failed:', err.message);
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`\n===========================================`);
    console.log(`  InsightFlow API Server`);
    console.log(`  Running on http://0.0.0.0:${PORT}`);
    console.log(`  Health: http://localhost:${PORT}/api/health`);
    console.log(`===========================================\n`);
  });
}

start();
