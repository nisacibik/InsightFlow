const datasetRepository = require('../repositories/datasetRepository');

async function getAll() {
  return datasetRepository.findAll();
}

async function getById(id) {
  const dataset = await datasetRepository.findById(id);
  if (!dataset) {
    const err = new Error('Dataset not found');
    err.statusCode = 404;
    throw err;
  }
  return dataset;
}

async function getStats(id) {
  return datasetRepository.getStats(id);
}

module.exports = { getAll, getById, getStats };
