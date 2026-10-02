# InsightFlow

Kullanıcı yorumlarından içgörü çıkaran full-stack analiz platformu.
NLP sentiment analizi, topic modelleme ve interaktif dashboard ile 145.000+ yorumu analiz eder.

## ✨ Özellikler

- **Sentiment analizi:** Yorumları Pozitif / Negatif / Nötr olarak sınıflandırır
- **Topic modelleme:** Yorumlardaki ana konuları ortaya çıkarır
- **İnteraktif dashboard:** Özet metrikler, duygu dağılımı ve puan analizleri
- **Yorum keşfi:** Filtreleme, arama ve sonsuz scroll
- **Kimlik doğrulama:** Kayıt, giriş ve token tabanlı oturum

## 🛠 Teknolojiler

| Katman | Teknolojiler |
|---|---|
| Backend | Node.js, Express, PostgreSQL |
| Mobil | React Native, Expo Router, TypeScript |
| Veri Bilimi | Python (NLP, sentiment, topic modelleme) |

## 🚀 Başlangıç

> Önce `backend/.env` dosyasını oluşturup veritabanı ve port bilgilerini gir.

**Backend**
```bash
cd backend
npm install
node server.js   # http://localhost:3001
```

**Mobil**
```bash
cd mobile
npm install
npx expo start   # QR kod ile telefonda aç
```

## 📁 Proje Yapısı

```
InsightFlow/
├── backend/
│   ├── server.js        # Giriş noktası
│   └── src/
│       ├── config/      # Veritabanı bağlantısı, ortam değişkenleri
│       ├── db/          # Tablo ve indeks oluşturma
│       ├── repositories/# SQL sorguları (veritabanı katmanı)
│       ├── services/    # İş mantığı
│       ├── routes/      # HTTP endpoint'leri
│       └── middleware/  # Auth, hata yakalama, doğrulama
│
├── mobile/
│   ├── app/             # Ekranlar (file-based routing, alt sekmeler dahil)
│   ├── components/      # Yeniden kullanılabilir UI bileşenleri
│   ├── constants/       # Tema ve API ayarları
│   ├── contexts/        # Oturum yönetimi
│   └── services/        # API istemcisi, güvenli token depolama
│
├── analysis/            # Python veri bilimi pipeline'ı
└── data/
    ├── raw/             # Orijinal veri setleri
    └── processed/       # Temizlenmiş ve analiz edilmiş veri
```

## 🔬 Veri Pipeline'ı

`analysis/` içindeki scriptler sırayla çalıştırılır:

1. **01–05:** Veri inceleme, temizleme, kalite kontrol
2. **06–09:** Sentiment analizi, NLP, topic modelleme
3. **10–16:** Veritabanı aktarımı
