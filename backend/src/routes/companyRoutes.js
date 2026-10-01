const express = require('express');
const router = express.Router();
const companyService = require('../services/companyService');
const { asyncHandler } = require('../middleware/errorHandler');

router.get('/me', asyncHandler(async (req, res) => {
  const company = await companyService.getByUserId(req.user.id);
  res.json({ company });
}));

router.post('/', asyncHandler(async (req, res) => {
  const company = await companyService.createForUser(req.user.id, req.body);
  res.status(201).json(company);
}));

router.put('/me', asyncHandler(async (req, res) => {
  const company = await companyService.updateForUser(req.user.id, req.body);
  res.json(company);
}));

module.exports = router;
