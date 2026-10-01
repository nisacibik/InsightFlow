const express = require('express');
const router = express.Router();
const analysisService = require('../services/analysisService');
const { asyncHandler } = require('../middleware/errorHandler');

router.get('/topics', asyncHandler(async (req, res) => {
  const rows = await analysisService.fetchTopics({
    datasetId: req.query.dataset_id,
    limit: req.query.limit,
  });
  res.json(rows);
}));

router.get('/sentiment-distribution', asyncHandler(async (req, res) => {
  const rows = await analysisService.getSentimentDistribution(req.query.dataset_id);
  res.json(rows);
}));

router.get('/rating-distribution', asyncHandler(async (req, res) => {
  const rows = await analysisService.getRatingDistribution(req.query.dataset_id);
  res.json(rows);
}));

router.get('/top-pain-points', asyncHandler(async (req, res) => {
  const rows = await analysisService.fetchPainPoints({
    datasetId: req.query.dataset_id,
    limit: req.query.limit,
  });
  res.json(rows);
}));

router.get('/top-feature-requests', asyncHandler(async (req, res) => {
  const rows = await analysisService.fetchFeatureRequests({
    datasetId: req.query.dataset_id,
    limit: req.query.limit,
  });
  res.json(rows);
}));

router.get('/dashboard', asyncHandler(async (req, res) => {
  const data = await analysisService.getDashboard();
  res.json(data);
}));

module.exports = router;
