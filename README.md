# InsightFlow

Kullanıcı yorumlarından içgörü çıkaran full-stack analiz platformu.  
NLP sentiment analizi, topic modelleme ve interaktif dashboard ile 145.000+ yorumu analiz eder.

---

## 📁 Proje Yapısı

```
InsightFlow/
│
├── backend/                    ← REST API sunucusu (Node.js + Express + PostgreSQL)
│   ├── server.js               ← Giriş noktası — sunucuyu başlatır
│   ├── .env                    ← Veritabanı ve port ayarları
│   └── src/
│       ├── app.js              ← Express uygulama fabrikası (middleware + route bağlama)
│       ├── config/
│       │   ├── database.js     ← PostgreSQL bağlantı havuzu
│       │   └── environment.js  ← Ortam değişkeni yönetimi
│       ├── db/
│       │   ├── schema.js       ← Tablo ve indeks oluşturma (uygulama açılışında çalışır)
│       │   └── helpers.js      ← Veritabanı yardımcıları (tablo/kolon varlık kontrolü)
│       ├── repositories/       ← SQL sorguları — veritabanı erişim katmanı
│       │   ├── authRepository.js
│       │   ├── datasetRepository.js
│       │   ├── reviewRepository.js
│       │   └── analysisRepository.js
│       ├── services/           ← İş mantığı katmanı
│       │   ├── authService.js       ← Kayıt, giriş, şifre hashing
│       │   ├── datasetService.js    ← Dataset CRUD işlemleri
│       │   ├── reviewService.js     ← Yorum filtreleme ve sayfalama
│       │   └── analysisService.js   ← Sentiment, topic ve dashboard mantığı
│       ├── routes/             ← HTTP endpoint tanımları (ince controller'lar)
│       │   ├── authRoutes.js
│       │   ├── datasetRoutes.js
│       │   ├── reviewRoutes.js
│       │   └── analysisRoutes.js
│       └── middleware/
│           ├── auth.js         ← Token doğrulama (requireAuth / optionalAuth)
│           ├── errorHandler.js ← Merkezi hata yakalama + asyncHandler
│           └── validate.js     ← İstek parametresi doğrulama
│
├── mobile/                     ← Mobil uygulama (React Native + Expo Router)
│   ├── app/                    ← Sayfa dosyaları (file-based routing)
│   │   ├── _layout.tsx         ← Kök navigasyon yapısı
│   │   ├── index.tsx           ← Açılış yönlendirmesi (login veya dashboard'a)
│   │   ├── login.tsx           ← Giriş ekranı
│   │   ├── register.tsx        ← Kayıt ekranı
│   │   ├── dataset/[id].tsx    ← Dataset detay sayfası
│   │   ├── review/[id].tsx     ← Yorum detay sayfası
│   │   └── (tabs)/            ← Alt navigasyon sekmeleri
│   │       ├── _layout.tsx     ← Tab bar konfigürasyonu
│   │       ├── index.tsx       ← Dashboard (ana sayfa)
│   │       ├── datasets.tsx    ← Dataset listesi
│   │       ├── reviews.tsx     ← Yorum listesi (filtre + arama + sonsuz scroll)
│   │       ├── topics.tsx      ← Konu analizi
│   │       ├── analysis.tsx    ← Sentiment ve rating analizleri
│   │       └── profile.tsx     ← Kullanıcı profili ve çıkış
│   ├── components/             ← Yeniden kullanılabilir UI bileşenleri
│   │   ├── EmptyState.tsx      ← Boş veri durumu göstergesi
│   │   ├── LoadingSpinner.tsx  ← Yükleniyor animasyonu
│   │   ├── RatingStars.tsx     ← Yıldız puanlama gösterimi
│   │   ├── ReviewCard.tsx      ← Yorum kartı bileşeni
│   │   ├── SentimentBadge.tsx  ← Duygu etiketi (Pozitif/Negatif/Nötr)
│   │   └── StatCard.tsx        ← İstatistik kartı
│   ├── constants/
│   │   ├── theme.ts            ← Tasarım sistemi (renkler, boyutlar, aralıklar)
│   │   └── config.ts           ← API adresi ve endpoint tanımları
│   ├── contexts/
│   │   └── AuthContext.tsx     ← Oturum yönetimi (login/logout/register)
│   └── services/
│       ├── api.ts              ← HTTP istemci sınıfı (tüm API çağrıları)
│       └── storage.ts          ← Güvenli token depolama (SecureStore)
│
├── analysis/                   ← Veri bilimi pipeline'ı (Python)
│   │                             Sıralı çalıştırılacak veri temizleme, NLP ve
│   │                             veritabanı aktarım scriptleri.
│   ├── 01–05: Veri inceleme, temizleme, kalite kontrol
│   ├── 06–09: Sentiment analizi, NLP, topic modelleme
│   ├── 10–16: Veritabanı aktarım scriptleri
│   └── 1_–9_mobil_*: Mobil dataset'e özel analiz pipeline'ı
│
├── data/                       ← Ham ve işlenmiş veri dosyaları
│   ├── raw/                    ← Orijinal veri setleri (CSV, JSONL)
│   └── processed/              ← Temizlenmiş ve analiz edilmiş veriler
│
└── .gitignore
```

## 🚀 Başlangıç

### Backend
```bash
cd backend
npm install
node server.js          # http://localhost:3001
```

### Mobile
```bash
cd mobile
npm install
npx expo start          # QR kod ile telefonda aç
```

## 🔗 API Endpoint'leri

| Yol | Açıklama |
|-----|----------|
| `GET /api/health` | Sunucu ve veritabanı sağlık kontrolü |
| `POST /api/auth/register` | Yeni hesap oluştur |
| `POST /api/auth/login` | Giriş yap (token al) |
| `GET /api/datasets` | Tüm datasetleri listele |
| `GET /api/reviews?limit=20&offset=0` | Yorumları filtrele ve sayfalama |
| `GET /api/analysis/dashboard` | Dashboard özet verisi |
| `GET /api/analysis/topics` | Konu analizi |
| `GET /api/analysis/sentiment-distribution` | Sentiment dağılımı |
