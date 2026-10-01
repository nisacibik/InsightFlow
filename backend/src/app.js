const express = require('express');
const cors = require('cors');
const { pool } = require('./config/database');
const { requireAuth } = require('./middleware/auth');
const { errorHandler, asyncHandler } = require('./middleware/errorHandler');

const authRoutes = require('./routes/authRoutes');
const datasetRoutes = require('./routes/datasetRoutes');
const reviewRoutes = require('./routes/reviewRoutes');
const analysisRoutes = require('./routes/analysisRoutes');
const companyRoutes = require('./routes/companyRoutes');
const analysisService = require('./services/analysisService');

function createApp() {
  const app = express();

  app.use(cors());
  app.use(express.json());

  app.get('/api/health', asyncHandler(async (req, res) => {
    const result = await pool.query('SELECT NOW()');
    res.json({
      status: 'ok',
      database: 'connected',
      timestamp: result.rows[0].now,
    });
  }));

  app.use('/api/auth', authRoutes);
  app.use('/api/datasets', requireAuth, datasetRoutes);
  app.use('/api/reviews', requireAuth, reviewRoutes);
  app.use('/api/analysis', requireAuth, analysisRoutes);
  app.use('/api/company', requireAuth, companyRoutes);

  app.get(['/api/topics', '/api/topics/'], requireAuth, asyncHandler(async (req, res) => {
    const rows = await analysisService.fetchTopics({
      datasetId: req.query.dataset_id,
      limit: req.query.limit,
    });
    res.json(rows);
  }));

  app.use(errorHandler);

  return app;
}

module.exports = { createApp };
