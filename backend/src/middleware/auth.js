const authService = require('../services/authService');

function extractToken(req) {
  const header = req.headers.authorization || '';
  return header.startsWith('Bearer ') ? header.slice(7).trim() : '';
}

async function optionalAuth(req, res, next) {
  const token = extractToken(req);
  if (!token) {
    req.user = null;
    return next();
  }

  try {
    req.user = await authService.findUserByToken(token);
  } catch (err) {
    console.error('Auth lookup error:', err);
    req.user = null;
  }
  next();
}

async function requireAuth(req, res, next) {
  await optionalAuth(req, res, () => {
    if (!req.user) {
      return res.status(401).json({ error: 'Giriş yapmanız gerekiyor.' });
    }
    next();
  });
}

module.exports = { requireAuth, optionalAuth, extractToken };
