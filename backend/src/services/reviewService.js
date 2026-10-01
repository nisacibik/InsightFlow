const reviewRepository = require('../repositories/reviewRepository');

async function getReviews({ dataset_id, sentiment, rating, product_area, search, limit = 20, offset = 0, sort = 'newest' }) {
  const { rows, total } = await reviewRepository.findMany({
    datasetId: dataset_id,
    sentiment,
    rating,
    productArea: product_area,
    search,
    limit,
    offset,
    sort,
  });

  return {
    data: rows,
    pagination: {
      total,
      limit: parseInt(limit),
      offset: parseInt(offset),
      has_more: parseInt(offset) + parseInt(limit) < total,
    },
  };
}

async function getById(id) {
  const review = await reviewRepository.findById(id);
  if (!review) {
    const err = new Error('Review not found');
    err.statusCode = 404;
    throw err;
  }
  return review;
}

async function getSummary() {
  return reviewRepository.getSummary();
}

module.exports = { getReviews, getById, getSummary };
