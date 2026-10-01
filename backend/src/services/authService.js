const crypto = require('crypto');
const authRepository = require('../repositories/authRepository');

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function hashPassword(password) {
  const salt = crypto.randomBytes(16).toString('hex');
  const hash = crypto.scryptSync(password, salt, 64).toString('hex');
  return `${salt}:${hash}`;
}

function verifyPassword(password, stored) {
  if (!stored || !stored.includes(':')) return false;
  const [salt, hash] = stored.split(':');
  const test = crypto.scryptSync(password, salt, 64).toString('hex');
  try {
    return crypto.timingSafeEqual(Buffer.from(hash, 'hex'), Buffer.from(test, 'hex'));
  } catch {
    return false;
  }
}

function createTokenString() {
  return crypto.randomBytes(32).toString('hex');
}

async function register(email, password) {
  const normalizedEmail = String(email || '').trim().toLowerCase();
  const pwd = String(password || '');

  if (!EMAIL_REGEX.test(normalizedEmail)) {
    const err = new Error('Geçerli bir e-posta adresi girin.');
    err.statusCode = 400;
    throw err;
  }
  if (pwd.length < 6) {
    const err = new Error('Şifre en az 6 karakter olmalı.');
    err.statusCode = 400;
    throw err;
  }

  const existing = await authRepository.findUserIdByEmail(normalizedEmail);
  if (existing) {
    const err = new Error('Bu e-posta ile zaten bir hesap var.');
    err.statusCode = 400;
    throw err;
  }

  const user = await authRepository.createUser(normalizedEmail, hashPassword(pwd));
  const token = createTokenString();
  await authRepository.createToken(token, user.id);

  return { token, user: { id: user.id, email: user.email } };
}

async function login(email, password) {
  const normalizedEmail = String(email || '').trim().toLowerCase();
  const pwd = String(password || '');

  if (!normalizedEmail || !pwd) {
    const err = new Error('E-posta ve şifre gerekli.');
    err.statusCode = 400;
    throw err;
  }

  const user = await authRepository.findUserByEmail(normalizedEmail);
  if (!user || !verifyPassword(pwd, user.password_hash)) {
    const err = new Error('E-posta veya şifre hatalı.');
    err.statusCode = 401;
    throw err;
  }

  const token = createTokenString();
  await authRepository.createToken(token, user.id);

  return { token, user: { id: user.id, email: user.email } };
}

async function logout(token) {
  if (token) {
    await authRepository.deleteToken(token);
  }
}

async function findUserByToken(token) {
  return authRepository.findUserByToken(token);
}

module.exports = { register, login, logout, findUserByToken };
