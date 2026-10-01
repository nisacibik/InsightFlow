const companyRepository = require('../repositories/companyRepository');

async function getByUserId(userId) {
  return companyRepository.findByUserId(userId);
}

async function createForUser(userId, data) {
  if (!data.company_name || !data.company_name.trim()) {
    const err = new Error('Şirket adı zorunludur.');
    err.statusCode = 400;
    throw err;
  }

  const company = await companyRepository.create({
    company_name: data.company_name.trim(),
    sector: data.sector || 'Bilişim',
    subsector: data.subsector || null,
    product_area: data.product_area || null,
    business_model: data.business_model || null,
    product_stage: data.product_stage || null,
    description: data.description || null,
  });

  await companyRepository.linkToUser(userId, company.id);
  return company;
}

async function updateForUser(userId, data) {
  const existing = await companyRepository.findByUserId(userId);
  if (!existing) {
    const err = new Error('Şirket bilgisi bulunamadı.');
    err.statusCode = 404;
    throw err;
  }

  if (!data.company_name || !data.company_name.trim()) {
    const err = new Error('Şirket adı zorunludur.');
    err.statusCode = 400;
    throw err;
  }

  return companyRepository.update(existing.id, {
    company_name: data.company_name.trim(),
    sector: data.sector || 'Bilişim',
    subsector: data.subsector || null,
    product_area: data.product_area || null,
    business_model: data.business_model || null,
    product_stage: data.product_stage || null,
    description: data.description || null,
  });
}

module.exports = { getByUserId, createForUser, updateForUser };
