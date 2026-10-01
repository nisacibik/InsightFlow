const { pool } = require('../config/database');

async function findAll() {
  const result = await pool.query(`
    SELECT
      d.id,
      d.name,
      d.subsector,
      d.data_period,
      d.description,
      d.record_count,
      d.source,
      d.url,
      d.license,
      d.created_at,
      COUNT(r.id) AS actual_review_count
    FROM datasets d
    LEFT JOIN reviews r ON r.dataset_id = d.id
    GROUP BY d.id
    ORDER BY d.id;
  `);
  return result.rows;
}

async function findById(id) {
  const result = await pool.query(`
    SELECT
      d.*,
      COUNT(r.id) AS actual_review_count
    FROM datasets d
    LEFT JOIN reviews r ON r.dataset_id = d.id
    WHERE d.id = $1
    GROUP BY d.id;
  `, [id]);
  return result.rows[0] || null;
}

async function getStats(id) {
  const countResult = await pool.query(`
    SELECT
      COUNT(r.id) AS total_reviews,
      ROUND(AVG(r.rating), 2) AS avg_rating,
      COUNT(ra.id) AS analyzed_reviews
    FROM reviews r
    LEFT JOIN review_analysis ra ON ra.review_id = r.id
    WHERE r.dataset_id = $1;
  `, [id]);

  const sentimentResult = await pool.query(`
    SELECT
      ra.sentiment,
      COUNT(*) AS count
    FROM reviews r
    JOIN review_analysis ra ON ra.review_id = r.id
    WHERE r.dataset_id = $1
    GROUP BY ra.sentiment
    ORDER BY count DESC;
  `, [id]);

  const ratingResult = await pool.query(`
    SELECT
      r.rating,
      COUNT(*) AS count
    FROM reviews r
    WHERE r.dataset_id = $1
    GROUP BY r.rating
    ORDER BY r.rating;
  `, [id]);

  const productResult = await pool.query(`
    SELECT
      r.product_area,
      COUNT(*) AS count
    FROM reviews r
    WHERE r.dataset_id = $1
      AND r.product_area IS NOT NULL
    GROUP BY r.product_area
    ORDER BY count DESC
    LIMIT 10;
  `, [id]);

  return {
    overview: countResult.rows[0],
    sentiment_distribution: sentimentResult.rows,
    rating_distribution: ratingResult.rows,
    product_distribution: productResult.rows,
  };
}

module.exports = { findAll, findById, getStats };
