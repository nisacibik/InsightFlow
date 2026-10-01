# Analysis — Veri Bilimi Pipeline'ı

Bu klasör, ham veri setlerini temizlemek, NLP analizi yapmak ve sonuçları
PostgreSQL veritabanına aktarmak için kullanılan Python scriptlerini içerir.

## Çalıştırma Sırası

Scriptler numaralandırılmıştır ve sırayla çalıştırılmalıdır.

### SaaS + AI Veri Setleri
| Script | Açıklama |
|--------|----------|
| `01_*` | Veri seti inceleme ve ilk AI kontrol |
| `02_*` | Örneklem alma ve detaylı AI kontrol |
| `03_*` | Veri temizleme ve kalite kontrol |
| `04_*` | Final veri hazırlama ve dataset DB aktarımı |
| `05_*` | Review'ları veritabanına aktarma |
| `06_*` | AI sentiment analizi ve karşılaştırma |
| `07_*` | NLP analiz (bigram, keyword extraction) |
| `08_*` | Rating-sentiment ilişki analizi ve topic modelleme |
| `09_*` | Tema-sentiment analizi ve topic DB aktarımı |
| `12_*` | AI sentiment sonuçlarını DB'ye aktarma |
| `13_*` | Topic summary DB aktarımı |
| `14–16_*` | Problem yoğunluğu ve review_topics DB aktarımı |

### Mobil Uygulama Veri Seti
| Script | Açıklama |
|--------|----------|
| `1_mobil_*` | Mobil dataset inceleme |
| `2_mobil_*` | Veri kalite kontrol |
| `3_mobil_*` | Veri temizleme |
| `4_mobil_*` | Keşifsel veri analizi (EDA) |
| `5_mobil_*` | Sentiment analizi |
| `6_mobil_*` | Rating-sentiment analizi |
| `7_mobil_*` | Tema analizi |
| `8_mobil_*` | Tema-rating-sentiment birleşik analiz |
| `9_mobil_*` | Insight özeti |
| `10–13_mobil_*` | Veritabanı aktarım scriptleri |

## Gereksinimler

```bash
pip install pandas numpy scikit-learn transformers psycopg2-binary
```
