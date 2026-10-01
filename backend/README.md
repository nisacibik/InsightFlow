# InsightFlow Backend

Express.js + PostgreSQL REST API. Katmanlı mimari ile yapılandırılmıştır.

## Mimari

```
İstek → Route (HTTP) → Service (İş Mantığı) → Repository (SQL) → PostgreSQL
```

- **Route'lar** sadece request/response yönetir, iş mantığı içermez
- **Service'ler** iş kurallarını, validasyonu ve fallback stratejilerini yönetir
- **Repository'ler** veritabanı sorgularını içerir — SQL sadece burada bulunur
- **Middleware** hata yakalama, auth ve parametre doğrulamayı yönetir

## Çalıştırma

```bash
npm install
node server.js    # http://localhost:3001/api/health
```

## Ortam Değişkenleri (.env)

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=insightflow_db
DB_USER=postgres
DB_PASSWORD=...
PORT=3001
```
