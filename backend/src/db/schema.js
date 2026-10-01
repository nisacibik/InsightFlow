const { pool } = require('../config/database');
const { tableExists } = require('./helpers');

async function initSchema() {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS users (
      id SERIAL PRIMARY KEY,
      email VARCHAR(255) UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `);

  await pool.query(`
    CREATE TABLE IF NOT EXISTS auth_tokens (
      token TEXT PRIMARY KEY,
      user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `);

  if (await tableExists('reviews')) {
    await pool.query(`
      CREATE TABLE IF NOT EXISTS review_topics (
        id SERIAL PRIMARY KEY,
        review_id INTEGER NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
        topic VARCHAR(100) NOT NULL,
        score NUMERIC(5,4),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (review_id, topic)
      );
    `);
  }

  await pool.query(`
    CREATE TABLE IF NOT EXISTS topic_summary (
      id SERIAL PRIMARY KEY,
      sector VARCHAR(100),
      product_area VARCHAR(100),
      topic VARCHAR(200) NOT NULL,
      review_count INTEGER DEFAULT 0,
      positive_count INTEGER DEFAULT 0,
      negative_count INTEGER DEFAULT 0,
      neutral_count INTEGER DEFAULT 0,
      average_rating NUMERIC(4,2),
      period VARCHAR(100)
    );
  `);

  if (await tableExists('review_analysis')) {
    await pool.query(`
      ALTER TABLE review_analysis
      ADD COLUMN IF NOT EXISTS pain_point TEXT,
      ADD COLUMN IF NOT EXISTS feature_request TEXT;
    `);
  }

  if (await tableExists('reviews')) {
    await pool.query(`
      CREATE INDEX IF NOT EXISTS idx_reviews_dataset_id ON reviews(dataset_id);
      CREATE INDEX IF NOT EXISTS idx_reviews_rating ON reviews(rating);
      CREATE INDEX IF NOT EXISTS idx_reviews_review_date ON reviews(review_date);
      CREATE INDEX IF NOT EXISTS idx_reviews_product_area ON reviews(product_area);
      CREATE INDEX IF NOT EXISTS idx_reviews_dataset_rating ON reviews(dataset_id, rating);
    `);
  }

  if (await tableExists('review_analysis')) {
    await pool.query(`
      CREATE INDEX IF NOT EXISTS idx_review_analysis_review_id ON review_analysis(review_id);
      CREATE INDEX IF NOT EXISTS idx_review_analysis_sentiment ON review_analysis(sentiment);
    `);
  }

  if (await tableExists('review_topics')) {
    await pool.query(`
      CREATE INDEX IF NOT EXISTS idx_review_topics_review_id_score ON review_topics(review_id, score DESC);
      CREATE INDEX IF NOT EXISTS idx_review_topics_topic ON review_topics(topic);
    `);
  }

  await pool.query(`
    CREATE INDEX IF NOT EXISTS idx_auth_tokens_token ON auth_tokens(token);
  `);

  if (await tableExists('companies')) {
    await pool.query(`
      ALTER TABLE users
      ADD COLUMN IF NOT EXISTS company_id BIGINT REFERENCES companies(id) ON DELETE SET NULL;
    `);
    await pool.query(`
      CREATE INDEX IF NOT EXISTS idx_users_company_id ON users(company_id);
    `);
  }

  console.log('Database schema and index check complete.');
}

module.exports = { initSchema };
