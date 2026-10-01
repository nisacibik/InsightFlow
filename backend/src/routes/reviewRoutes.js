const express = require('express');
const router = express.Router();
const reviewService = require('../services/reviewService');
const { asyncHandler } = require('../middleware/errorHandler');
const { validateIdParam } = require('../middleware/validate');

router.get('/', asyncHandler(async (req, res) => {
  const result = await reviewService.getReviews(req.query);
  res.json(result);
}));

router.get('/stats/summary', asyncHandler(async (req, res) => {
  const summary = await reviewService.getSummary();
  res.json(summary);
}));

router.get('/:id', validateIdParam, asyncHandler(async (req, res) => {
  const review = await reviewService.getById(req.params.id);
  res.json(review);
}));

module.exports = router;
