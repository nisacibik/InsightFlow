const express = require('express');
const router = express.Router();
const datasetService = require('../services/datasetService');
const { asyncHandler } = require('../middleware/errorHandler');
const { validateIdParam } = require('../middleware/validate');

router.get('/', asyncHandler(async (req, res) => {
  const datasets = await datasetService.getAll();
  res.json(datasets);
}));

router.get('/:id', validateIdParam, asyncHandler(async (req, res) => {
  const dataset = await datasetService.getById(req.params.id);
  res.json(dataset);
}));

router.get('/:id/stats', validateIdParam, asyncHandler(async (req, res) => {
  const stats = await datasetService.getStats(req.params.id);
  res.json(stats);
}));

module.exports = router;
