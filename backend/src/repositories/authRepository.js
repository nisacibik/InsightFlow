const { pool } = require('../config/database');

async function findUserByEmail(email) {
  const result = await pool.query(
    'SELECT id, email, password_hash FROM users WHERE email = $1',
    [email]
  );
  return result.rows[0] || null;
}

async function findUserIdByEmail(email) {
  const result = await pool.query(
    'SELECT id FROM users WHERE email = $1',
    [email]
  );
  return result.rows[0] || null;
}

async function createUser(email, passwordHash) {
  const result = await pool.query(
    `INSERT INTO users (email, password_hash)
     VALUES ($1, $2)
     RETURNING id, email, created_at`,
    [email, passwordHash]
  );
  return result.rows[0];
}

async function createToken(token, userId) {
  await pool.query(
    'INSERT INTO auth_tokens (token, user_id) VALUES ($1, $2)',
    [token, userId]
  );
}

async function deleteToken(token) {
  await pool.query(
    'DELETE FROM auth_tokens WHERE token = $1',
    [token]
  );
}

async function findUserByToken(token) {
  const result = await pool.query(
    `SELECT u.id, u.email
     FROM auth_tokens t
     JOIN users u ON u.id = t.user_id
     WHERE t.token = $1`,
    [token]
  );
  return result.rows[0] || null;
}

module.exports = {
  findUserByEmail,
  findUserIdByEmail,
  createUser,
  createToken,
  deleteToken,
  findUserByToken,
};
