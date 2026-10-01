const { pool } = require('../config/database');

async function findByUserId(userId) {
  const result = await pool.query(
    `SELECT c.* FROM companies c
     JOIN users u ON u.company_id = c.id
     WHERE u.id = $1`,
    [userId]
  );
  return result.rows[0] || null;
}

async function create(data) {
  const result = await pool.query(
    `INSERT INTO companies (company_name, sector, subsector, product_area, business_model, product_stage, description)
     VALUES ($1, $2, $3, $4, $5, $6, $7)
     RETURNING *`,
    [data.company_name, data.sector, data.subsector, data.product_area, data.business_model, data.product_stage, data.description]
  );
  return result.rows[0];
}

async function update(companyId, data) {
  const result = await pool.query(
    `UPDATE companies
     SET company_name = $1, sector = $2, subsector = $3, product_area = $4,
         business_model = $5, product_stage = $6, description = $7
     WHERE id = $8
     RETURNING *`,
    [data.company_name, data.sector, data.subsector, data.product_area, data.business_model, data.product_stage, data.description, companyId]
  );
  return result.rows[0] || null;
}

async function linkToUser(userId, companyId) {
  await pool.query(
    'UPDATE users SET company_id = $1 WHERE id = $2',
    [companyId, userId]
  );
}

module.exports = { findByUserId, create, update, linkToUser };
