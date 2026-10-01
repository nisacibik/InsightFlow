const { pool } = require('../config/database');
const { tableExists } = require('../db/helpers');

async function getTopicsByDataset(datasetId, limit) {
  if (!(await tableExists('review_topics'))) return [];
  const result = await pool.query(
    `
    SELECT
      rt.topic,
      COUNT(*)::int AS review_count,
      COUNT(*) FILTER (WHERE ra.sentiment = 'positive')::int AS positive_count,
      COUNT(*) FILTER (WHERE ra.sentiment = 'negative')::int AS negative_count,
      COUNT(*) FILTER (WHERE ra.sentiment = 'neutral')::int AS neutral_count,
      ROUND(AVG(r.rating)::numeric, 2) AS average_rating
    FROM review_topics rt
    JOIN reviews r ON r.id = rt.review_id
    LEFT JOIN review_analysis ra ON ra.review_id = r.id
    WHERE r.dataset_id = $1
    GROUP BY rt.topic
    ORDER BY review_count DESC
    LIMIT $2
    `,
    [parseInt(datasetId, 10), limit]
  );
  return result.rows;
}

async function getTopicsFromSummary(limit) {
  if (!(await tableExists('topic_summary'))) return [];
  const result = await pool.query(
    `
    SELECT
      topic,
      SUM(review_count)::int AS review_count,
      SUM(positive_count)::int AS positive_count,
      SUM(negative_count)::int AS negative_count,
      SUM(neutral_count)::int AS neutral_count,
      ROUND(AVG(average_rating)::numeric, 2) AS average_rating,
      MAX(product_area) AS product_area
    FROM topic_summary
    GROUP BY topic
    ORDER BY review_count DESC
    LIMIT $1
    `,
    [limit]
  );
  return result.rows;
}

async function getTopicsFromReviewTopics(limit) {
  if (!(await tableExists('review_topics'))) return [];
  const result = await pool.query(
    `
    SELECT
      rt.topic,
      COUNT(*)::int AS review_count,
      COUNT(*) FILTER (WHERE ra.sentiment = 'positive')::int AS positive_count,
      COUNT(*) FILTER (WHERE ra.sentiment = 'negative')::int AS negative_count,
      COUNT(*) FILTER (WHERE ra.sentiment = 'neutral')::int AS neutral_count,
      ROUND(AVG(r.rating)::numeric, 2) AS average_rating
    FROM review_topics rt
    JOIN reviews r ON r.id = rt.review_id
    LEFT JOIN review_analysis ra ON ra.review_id = r.id
    GROUP BY rt.topic
    ORDER BY review_count DESC
    LIMIT $1
    `,
    [limit]
  );
  return result.rows;
}

async function getTopicsFromProductAreas(limit) {
  const result = await pool.query(
    `
    SELECT
      r.product_area AS topic,
      COUNT(*)::int AS review_count,
      COUNT(*) FILTER (WHERE ra.sentiment = 'positive')::int AS positive_count,
      COUNT(*) FILTER (WHERE ra.sentiment = 'negative')::int AS negative_count,
      COUNT(*) FILTER (WHERE ra.sentiment = 'neutral')::int AS neutral_count,
      ROUND(AVG(r.rating)::numeric, 2) AS average_rating
    FROM reviews r
    LEFT JOIN review_analysis ra ON ra.review_id = r.id
    WHERE r.product_area IS NOT NULL AND r.product_area != ''
    GROUP BY r.product_area
    ORDER BY review_count DESC
    LIMIT $1
    `,
    [limit]
  );
  return result.rows;
}

async function getSentimentDistribution(datasetId) {
  if (datasetId) {
    const result = await pool.query(
      `
      SELECT
        ra.sentiment,
        COUNT(*) AS count,
        ROUND(AVG(ra.confidence_score), 3) AS avg_confidence
      FROM review_analysis ra
      JOIN reviews r ON r.id = ra.review_id
      WHERE r.dataset_id = $1
        AND ra.sentiment IS NOT NULL
      GROUP BY ra.sentiment
      ORDER BY count DESC;
      `,
      [parseInt(datasetId)]
    );
    return result.rows;
  }

  const result = await pool.query(`
    SELECT
      ra.sentiment,
      COUNT(*) AS count,
      ROUND(AVG(ra.confidence_score), 3) AS avg_confidence
    FROM review_analysis ra
    WHERE ra.sentiment IS NOT NULL
    GROUP BY ra.sentiment
    ORDER BY count DESC;
  `);
  return result.rows;
}

async function getRatingDistribution(datasetId) {
  if (datasetId) {
    const result = await pool.query(
      `
      SELECT
        r.rating,
        COUNT(*) AS count
      FROM reviews r
      WHERE r.dataset_id = $1
      GROUP BY r.rating
      ORDER BY r.rating;
      `,
      [parseInt(datasetId)]
    );
    return result.rows;
  }

  const result = await pool.query(`
    SELECT
      r.rating,
      COUNT(*) AS count
    FROM reviews r
    GROUP BY r.rating
    ORDER BY r.rating;
  `);
  return result.rows;
}

async function hasPainPointColumn() {
  const result = await pool.query(
    `SELECT 1 FROM information_schema.columns
     WHERE table_name = 'review_analysis' AND column_name = 'pain_point'`
  );
  return result.rowCount > 0;
}

async function getPainPointsFromAnalysis(datasetId, limit) {
  const params = datasetId ? [parseInt(datasetId, 10), limit] : [limit];
  const whereDataset = datasetId ? 'AND r.dataset_id = $1' : '';
  const limitParam = datasetId ? '$2' : '$1';
  const result = await pool.query(
    `
    SELECT ra.pain_point, COUNT(*)::int AS count
    FROM review_analysis ra
    JOIN reviews r ON r.id = ra.review_id
    WHERE ra.pain_point IS NOT NULL AND ra.pain_point != ''
    ${whereDataset}
    GROUP BY ra.pain_point
    ORDER BY count DESC
    LIMIT ${limitParam}
    `,
    params
  );
  return result.rows;
}

async function getPainPointsFromTopics(datasetId, limit) {
  if (!(await tableExists('review_topics'))) return [];
  const params = datasetId ? [parseInt(datasetId, 10), limit] : [limit];
  const whereDataset = datasetId ? 'AND r.dataset_id = $1' : '';
  const limitParam = datasetId ? '$2' : '$1';
  const result = await pool.query(
    `
    SELECT rt.topic AS pain_point, COUNT(*)::int AS count
    FROM review_topics rt
    JOIN reviews r ON r.id = rt.review_id
    JOIN review_analysis ra ON ra.review_id = r.id
    WHERE ra.sentiment = 'negative'
    ${whereDataset}
    GROUP BY rt.topic
    ORDER BY count DESC
    LIMIT ${limitParam}
    `,
    params
  );
  return result.rows;
}

async function hasFeatureRequestColumn() {
  const result = await pool.query(
    `SELECT 1 FROM information_schema.columns
     WHERE table_name = 'review_analysis' AND column_name = 'feature_request'`
  );
  return result.rowCount > 0;
}

async function getFeatureRequestsFromAnalysis(datasetId, limit) {
  const params = datasetId ? [parseInt(datasetId, 10), limit] : [limit];
  const whereDataset = datasetId ? 'AND r.dataset_id = $1' : '';
  const limitParam = datasetId ? '$2' : '$1';
  const result = await pool.query(
    `
    SELECT ra.feature_request, COUNT(*)::int AS count
    FROM review_analysis ra
    JOIN reviews r ON r.id = ra.review_id
    WHERE ra.feature_request IS NOT NULL AND ra.feature_request != ''
    ${whereDataset}
    GROUP BY ra.feature_request
    ORDER BY count DESC
    LIMIT ${limitParam}
    `,
    params
  );
  return result.rows;
}

async function getFeatureRequestsFromTopics(datasetId, limit) {
  if (!(await tableExists('review_topics'))) return [];
  const params = datasetId ? [parseInt(datasetId, 10), limit] : [limit];
  const whereDataset = datasetId ? 'AND r.dataset_id = $1' : '';
  const limitParam = datasetId ? '$2' : '$1';
  const result = await pool.query(
    `
    SELECT rt.topic AS feature_request, COUNT(*)::int AS count
    FROM review_topics rt
    JOIN reviews r ON r.id = rt.review_id
    JOIN review_analysis ra ON ra.review_id = r.id
    WHERE ra.sentiment = 'positive'
    ${whereDataset}
    GROUP BY rt.topic
    ORDER BY count DESC
    LIMIT ${limitParam}
    `,
    params
  );
  return result.rows;
}

async function getDashboardOverview() {
  const result = await pool.query(`
    SELECT
      (SELECT COUNT(*) FROM datasets) AS total_datasets,
      (SELECT COUNT(*) FROM reviews) AS total_reviews,
      (SELECT COUNT(*) FROM review_analysis) AS total_analyses,
      (SELECT ROUND(AVG(rating), 2) FROM reviews) AS avg_rating;
  `);
  return result.rows[0];
}

async function getDashboardSentiment() {
  const result = await pool.query(`
    SELECT
      ra.sentiment,
      COUNT(*) AS count
    FROM review_analysis ra
    WHERE ra.sentiment IS NOT NULL
    GROUP BY ra.sentiment
    ORDER BY count DESC;
  `);
  return result.rows;
}

async function getDashboardRating() {
  const result = await pool.query(`
    SELECT
      r.rating,
      COUNT(*) AS count
    FROM reviews r
    GROUP BY r.rating
    ORDER BY r.rating;
  `);
  return result.rows;
}

async function getDashboardDatasets() {
  const result = await pool.query(`
    SELECT
      d.id,
      d.name,
      d.subsector,
      COUNT(r.id) AS review_count,
      ROUND(AVG(r.rating), 2) AS avg_rating
    FROM datasets d
    LEFT JOIN reviews r ON r.dataset_id = d.id
    GROUP BY d.id
    ORDER BY d.id;
  `);
  return result.rows;
}

async function getDashboardRecentReviews() {
  const result = await pool.query(`
    SELECT
      r.id,
      r.review_text,
      r.rating,
      r.product_area,
      r.review_date,
      ra.sentiment,
      ra.sentiment_score,
      d.name AS dataset_name
    FROM reviews r
    LEFT JOIN review_analysis ra ON ra.review_id = r.id
    LEFT JOIN datasets d ON d.id = r.dataset_id
    ORDER BY r.review_date DESC NULLS LAST
    LIMIT 10;
  `);
  return result.rows;
}

async function getDashboardProducts() {
  const result = await pool.query(`
    SELECT
      r.product_area,
      COUNT(*) AS count
    FROM reviews r
    WHERE r.product_area IS NOT NULL
    GROUP BY r.product_area
    ORDER BY count DESC
    LIMIT 10;
  `);
  return result.rows;
}

module.exports = {
  getTopicsByDataset,
  getTopicsFromSummary,
  getTopicsFromReviewTopics,
  getTopicsFromProductAreas,
  getSentimentDistribution,
  getRatingDistribution,
  hasPainPointColumn,
  getPainPointsFromAnalysis,
  getPainPointsFromTopics,
  hasFeatureRequestColumn,
  getFeatureRequestsFromAnalysis,
  getFeatureRequestsFromTopics,
  getDashboardOverview,
  getDashboardSentiment,
  getDashboardRating,
  getDashboardDatasets,
  getDashboardRecentReviews,
  getDashboardProducts,
};
