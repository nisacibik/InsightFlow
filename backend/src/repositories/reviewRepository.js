const { pool } = require('../config/database');

async function findMany({ datasetId, sentiment, rating, productArea, search, limit, offset, sort }) {
  let whereConditions = [];
  let params = [];
  let paramIndex = 1;

  if (datasetId) {
    whereConditions.push(`r.dataset_id = $${paramIndex++}`);
    params.push(parseInt(datasetId));
  }

  if (sentiment) {
    whereConditions.push(`ra.sentiment = $${paramIndex++}`);
    params.push(sentiment);
  }

  if (rating) {
    whereConditions.push(`r.rating = $${paramIndex++}`);
    params.push(parseInt(rating));
  }

  if (productArea) {
    whereConditions.push(`r.product_area = $${paramIndex++}`);
    params.push(productArea);
  }

  if (search) {
    whereConditions.push(`r.review_text ILIKE $${paramIndex++}`);
    params.push(`%${search}%`);
  }

  const whereClause = whereConditions.length > 0
    ? 'WHERE ' + whereConditions.join(' AND ')
    : '';

  let orderBy = 'r.review_date DESC NULLS LAST';
  if (sort === 'oldest') orderBy = 'r.review_date ASC NULLS LAST';
  if (sort === 'rating_high') orderBy = 'r.rating DESC';
  if (sort === 'rating_low') orderBy = 'r.rating ASC';
  if (sort === 'helpful') orderBy = 'r.helpful_count DESC NULLS LAST';

  const countJoin = sentiment ? 'LEFT JOIN review_analysis ra ON ra.review_id = r.id' : '';
  const countQuery = `
    SELECT COUNT(*) AS total
    FROM reviews r
    ${countJoin}
    ${whereClause};
  `;
  const countResult = await pool.query(countQuery, params);
  const total = parseInt(countResult.rows[0].total, 10);

  const dataQuery = `
    SELECT
      r.id,
      r.review_id,
      r.dataset_id,
      r.product_id,
      r.review_text,
      r.source,
      r.rating,
      r.language,
      r.product_area,
      r.review_date,
      r.helpful_count,
      r.verified_purchase,
      ra.sentiment,
      ra.sentiment_score,
      ra.confidence_score,
      ra.pain_point,
      ra.feature_request,
      d.name AS dataset_name,
      (
        SELECT rt.topic
        FROM review_topics rt
        WHERE rt.review_id = r.id
        ORDER BY rt.score DESC NULLS LAST
        LIMIT 1
      ) AS topic
    FROM reviews r
    LEFT JOIN review_analysis ra ON ra.review_id = r.id
    LEFT JOIN datasets d ON d.id = r.dataset_id
    ${whereClause}
    ORDER BY ${orderBy}
    LIMIT $${paramIndex++} OFFSET $${paramIndex++};
  `;
  params.push(parseInt(limit), parseInt(offset));

  const dataResult = await pool.query(dataQuery, params);

  return { rows: dataResult.rows, total };
}

async function findById(id) {
  const result = await pool.query(`
    SELECT
      r.*,
      ra.sentiment,
      ra.sentiment_score,
      ra.confidence_score,
      ra.pain_point,
      ra.feature_request,
      ra.created_at AS analysis_date,
      d.name AS dataset_name,
      (
        SELECT COALESCE(json_agg(rt.topic ORDER BY rt.score DESC NULLS LAST), '[]'::json)
        FROM review_topics rt
        WHERE rt.review_id = r.id
      ) AS topics
    FROM reviews r
    LEFT JOIN review_analysis ra ON ra.review_id = r.id
    LEFT JOIN datasets d ON d.id = r.dataset_id
    WHERE r.id = $1;
  `, [id]);
  return result.rows[0] || null;
}

async function getSummary() {
  const totalResult = await pool.query(`
    SELECT
      COUNT(*) AS total_reviews,
      ROUND(AVG(rating), 2) AS avg_rating,
      COUNT(CASE WHEN verified_purchase = true THEN 1 END) AS verified_count
    FROM reviews;
  `);

  const sentimentResult = await pool.query(`
    SELECT
      sentiment,
      COUNT(*) AS count
    FROM review_analysis
    WHERE sentiment IS NOT NULL
    GROUP BY sentiment
    ORDER BY count DESC;
  `);

  const datasetResult = await pool.query(`
    SELECT
      d.id,
      d.name,
      COUNT(r.id) AS review_count
    FROM datasets d
    LEFT JOIN reviews r ON r.dataset_id = d.id
    GROUP BY d.id
    ORDER BY d.id;
  `);

  return {
    overview: totalResult.rows[0],
    sentiment_summary: sentimentResult.rows,
    datasets_summary: datasetResult.rows,
  };
}

module.exports = { findMany, findById, getSummary };
