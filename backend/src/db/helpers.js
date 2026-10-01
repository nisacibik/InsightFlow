const { pool } = require('../config/database');

async function tableExists(tableName) {
  const result = await pool.query(
    `SELECT 1 FROM information_schema.tables
     WHERE table_schema = 'public' AND table_name = $1`,
    [tableName]
  );
  return result.rowCount > 0;
}

async function columnExists(tableName, columnName) {
  const result = await pool.query(
    `SELECT 1 FROM information_schema.columns
     WHERE table_schema = 'public' AND table_name = $1 AND column_name = $2`,
    [tableName, columnName]
  );
  return result.rowCount > 0;
}

module.exports = { tableExists, columnExists };
