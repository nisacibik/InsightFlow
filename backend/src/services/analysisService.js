const analysisRepo = require('../repositories/analysisRepository');

async function fetchTopics({ datasetId, limit = 30 }) {
  const parsedLimit = Math.min(Math.max(parseInt(limit, 10) || 30, 1), 100);

  if (datasetId) {
    return analysisRepo.getTopicsByDataset(datasetId, parsedLimit);
  }

  const summaryRows = await analysisRepo.getTopicsFromSummary(parsedLimit);
  if (summaryRows.length > 0) return summaryRows;

  const topicRows = await analysisRepo.getTopicsFromReviewTopics(parsedLimit);
  if (topicRows.length > 0) return topicRows;

  return analysisRepo.getTopicsFromProductAreas(parsedLimit);
}

async function fetchPainPoints({ datasetId, limit = 10 }) {
  const parsedLimit = Math.min(Math.max(parseInt(limit, 10) || 10, 1), 50);

  if (await analysisRepo.hasPainPointColumn()) {
    const rows = await analysisRepo.getPainPointsFromAnalysis(datasetId, parsedLimit);
    if (rows.length > 0) return rows;
  }

  return analysisRepo.getPainPointsFromTopics(datasetId, parsedLimit);
}

async function fetchFeatureRequests({ datasetId, limit = 10 }) {
  const parsedLimit = Math.min(Math.max(parseInt(limit, 10) || 10, 1), 50);

  if (await analysisRepo.hasFeatureRequestColumn()) {
    const rows = await analysisRepo.getFeatureRequestsFromAnalysis(datasetId, parsedLimit);
    if (rows.length > 0) return rows;
  }

  return analysisRepo.getFeatureRequestsFromTopics(datasetId, parsedLimit);
}

async function getSentimentDistribution(datasetId) {
  return analysisRepo.getSentimentDistribution(datasetId);
}

async function getRatingDistribution(datasetId) {
  return analysisRepo.getRatingDistribution(datasetId);
}

async function getDashboard() {
  const [overview, sentiments, ratings, datasets, recentReviews, products] = await Promise.all([
    analysisRepo.getDashboardOverview(),
    analysisRepo.getDashboardSentiment(),
    analysisRepo.getDashboardRating(),
    analysisRepo.getDashboardDatasets(),
    analysisRepo.getDashboardRecentReviews(),
    analysisRepo.getDashboardProducts(),
  ]);

  const [topics, painPoints, featureRequests] = await Promise.all([
    fetchTopics({ limit: 8 }),
    fetchPainPoints({ limit: 5 }),
    fetchFeatureRequests({ limit: 5 }),
  ]);

  return {
    overview,
    sentiment_distribution: sentiments,
    rating_distribution: ratings,
    datasets,
    recent_reviews: recentReviews,
    product_distribution: products,
    top_topics: topics,
    top_pain_points: painPoints,
    top_feature_requests: featureRequests,
  };
}

module.exports = {
  fetchTopics,
  fetchPainPoints,
  fetchFeatureRequests,
  getSentimentDistribution,
  getRatingDistribution,
  getDashboard,
};
