# InsightFlow

**Kullanıcı yorumlarından içgörü çıkaran full-stack analiz platformu.**

InsightFlow; NLP tabanlı duygu (sentiment) analizi, konu (topic) modelleme ve interaktif dashboard ile **145.000+ kullanıcı yorumunu** analiz eder ve sonuçları REST API ile mobil uygulamaya sunar.

---

## İçindekiler

- [Özellikler](#özellikler)
- [Teknoloji Yığını](#teknoloji-yığını)
- [Mimari](#mimari)
- [Proje Yapısı](#proje-yapısı)
- [Başlangıç](#başlangıç)
- [API Referansı](#api-referansı)
- [Veri Bilimi Pipeline'ı](#veri-bilimi-pipelineı)

---

## Özellikler

- **Sentiment analizi:** Yorumları Pozitif / Negatif / Nötr olarak sınıflandırır.
- **Topic modelleme:** Yorumlardaki ana konuları ve eğilimleri ortaya çıkarır.
- **İnteraktif dashboard:** Özet metrikler, duygu dağılımı ve puan analizleri tek ekranda.
- **Yorum keşfi:** Filtreleme, arama ve sonsuz scroll ile sayfalanmış yorum listesi.
- **Çoklu dataset desteği:** Birden fazla veri setini listeleme ve detaylı inceleme.
- **Kimlik doğrulama:** Kayıt, giriş ve token tabanlı oturum yönetimi.

---

## Teknoloji Yığını

| Katman | Teknolojiler |
|---|---|
| **Backend** | Node.js, Express, PostgreSQL |
| **Mobil** | React Native, Expo Router, TypeScript |
| **Veri Bilimi** | Python (NLP, sentiment analizi, topic modelleme) |
| **Güvenlik** | Token doğrulama, şifre hashing, SecureStore |

---

## Mimari

Backend, sorumlulukların net ayrıldığı katmanlı bir yapıya sahiptir:

```
İstek → Route → Middleware → Service → Repository → PostgreSQL
```

| Katman | Sorumluluk |
|---|---|
| **Routes** | HTTP endpoint tanımları (ince controller'lar) |
| **Middleware** | Token doğrulama, istek doğrulama, merkezi hata yakalama |
| **Services** | İş mantığı (kimlik doğrulama, filtreleme, analiz) |
| **Repositories** | SQL sorguları ve veritabanı erişimi |

---

## Proje Yapısı

```
InsightFlow/
├── backend/                  # REST API (Node.js + Express + PostgreSQL)
│   ├── server.js             # Giriş noktası
│   ├── .env                  # Veritabanı ve port ayarları
│   └── src/
│       ├── app.js            # Express fabrikası (middleware + route bağlama)
│       ├── config/           # Veritabanı havuzu, ortam değişkenleri
│       ├── db/               # Şema/indeks oluşturma, DB yardımcıları
│       ├── repositories/     # Veritabanı erişim katmanı
│       ├── services/         # İş mantığı katmanı
│       ├── routes/           # Endpoint tanımları
│       └── middleware/       # auth, errorHandler, validate
│
├── mobile/                   # Mobil uygulama (React Native + Expo Router)
│   ├── app/                  # Sayfalar (file-based routing)
│   │   ├── login.tsx, register.tsx
│   │   ├── dataset/[id].tsx, review/[id].tsx
│   │   └── (tabs)/           # Dashboard, Datasets, Reviews, Topics, Analysis, Profile
│   ├── components/           # EmptyState, LoadingSpinner, RatingStars,
│   │                         # ReviewCard, SentimentBadge, StatCard
│   ├── constants/            # theme.ts (tasarım sistemi), config.ts (API adresi)
│   ├── contexts/             # AuthContext (oturum yönetimi)
│   └── services/             # api.ts (HTTP istemcisi), storage.ts (SecureStore)
│
├── analysis/                 # Python veri bilimi pipeline'ı
├── data/
│   ├── raw/                  # Ham veri setleri (CSV, JSONL)
│   └── processed/            # Temizlenmiş ve analiz edilmiş veriler
└── .gitignore
```

<details>
<summary><b>Backend detayları</b></summary>

- `config/database.js` — PostgreSQL bağlantı havuzu
- `config/environment.js` — Ortam değişkeni yönetimi
- `db/schema.js` — Tablo ve indeksleri uygulama açılışında oluşturur
- `db/helpers.js` — Tablo/kolon varlık kontrolleri
- `authService.js` — Kayıt, giriş, şifre hashing
- `datasetService.js` — Dataset CRUD işlemleri
- `reviewService.js` — Yorum filtreleme ve sayfalama
- `analysisService.js` — Sentiment, topic ve dashboard mantığı
- `middleware/auth.js` — `requireAuth` / `optionalAuth`

</details>

---

## Başlangıç

### Gereksinimler

- Node.js ve npm
- PostgreSQL
- Mobil test için Expo Go (veya emülatör)

### Backend

```bash
cd backend
npm install
node server.js
```

Sunucu varsayılan olarak `http://localhost:3001` adresinde çalışır. Başlamadan önce `backend/.env` dosyasında veritabanı ve port ayarlarını yapılandırın. Tablolar uygulama açılışında otomatik oluşturulur.

### Mobil

```bash
cd mobile
npm install
npx expo start
```

Terminalde çıkan QR kodu Expo Go ile okutarak uygulamayı telefonunuzda açabilirsiniz. API adresini `mobile/constants/config.ts` dosyasından ayarlayın.

---

## API Referansı

| Metot | Yol | Açıklama |
|---|---|---|
| `GET` | `/api/health` | Sunucu ve veritabanı sağlık kontrolü |
| `POST` | `/api/auth/register` | Yeni hesap oluştur |
| `POST` | `/api/auth/login` | Giriş yap (token al) |
| `GET` | `/api/datasets` | Tüm datasetleri listele |
| `GET` | `/api/reviews?limit=20&offset=0` | Yorumları filtrele ve sayfalama |
| `GET` | `/api/analysis/dashboard` | Dashboard özet verisi |
| `GET` | `/api/analysis/topics` | Konu analizi |
| `GET` | `/api/analysis/sentiment-distribution` | Duygu dağılımı |

---

## Veri Bilimi Pipeline'ı

`analysis/` klasöründeki Python scriptleri **sıralı** çalıştırılmak üzere tasarlanmıştır:

| Aşama | Scriptler | İçerik |
|---|---|---|
| 1 | `01–05` | Veri inceleme, temizleme, kalite kontrol |
| 2 | `06–09` | Sentiment analizi, NLP, topic modelleme |
| 3 | `10–16` | Veritabanı aktarım scriptleri |
| 4 | `1_–9_mobil_*` | Mobil dataset'e özel analiz pipeline'ı |
