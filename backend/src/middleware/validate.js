function validateIdParam(req, res, next) {
  const id = parseInt(req.params.id, 10);
  if (isNaN(id) || id <= 0) {
    return res.status(400).json({ error: 'Geçersiz ID parametresi.' });
  }
  req.params.id = id;
  next();
}

function validateQueryInt(paramName, { min = 0, max = Infinity, defaultValue } = {}) {
  return (req, res, next) => {
    const raw = req.query[paramName];
    if (raw === undefined || raw === '') {
      if (defaultValue !== undefined) {
        req.query[paramName] = defaultValue;
      }
      return next();
    }
    const value = parseInt(raw, 10);
    if (isNaN(value) || value < min || value > max) {
      return res.status(400).json({
        error: `Geçersiz '${paramName}' değeri. ${min}-${max} arasında bir tam sayı olmalı.`,
      });
    }
    req.query[paramName] = value;
    next();
  };
}

module.exports = { validateIdParam, validateQueryInt };
