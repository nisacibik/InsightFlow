function errorHandler(err, req, res, next) {
  const statusCode = err.statusCode || 500;
  const message = statusCode === 500
    ? 'Sunucu hatası. Lütfen tekrar deneyin.'
    : err.message;

  if (statusCode === 500) {
    console.error('Server error:', err.stack);
  }

  res.status(statusCode).json({ error: message });
}

function asyncHandler(fn) {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
}

module.exports = { errorHandler, asyncHandler };
