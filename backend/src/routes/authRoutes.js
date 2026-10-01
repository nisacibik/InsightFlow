const express = require('express');
const router = express.Router();
const authService = require('../services/authService');
const { requireAuth, extractToken } = require('../middleware/auth');
const { asyncHandler } = require('../middleware/errorHandler');

router.post('/register', asyncHandler(async (req, res) => {
  const result = await authService.register(req.body?.email, req.body?.password);
  res.status(201).json(result);
}));

router.post('/login', asyncHandler(async (req, res) => {
  const result = await authService.login(req.body?.email, req.body?.password);
  res.json(result);
}));

router.post('/logout', requireAuth, asyncHandler(async (req, res) => {
  const token = extractToken(req);
  await authService.logout(token);
  res.json({ success: true });
}));

router.get('/me', requireAuth, asyncHandler(async (req, res) => {
  res.json({ user: req.user });
}));

module.exports = router;
