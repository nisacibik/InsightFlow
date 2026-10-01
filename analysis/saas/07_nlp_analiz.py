import os
import psycopg2
import torch

from dotenv import load_dotenv
from transformers import pipeline
from psycopg2.extras import execute_batch
from collections import Counter
from time import time

print("=" * 70)
print("INSIGHTFLOW - SENTIMENT ANALİZİ")
print("=" * 70)

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

if not DB_PASSWORD:
    raise ValueError(
        "DB_PASSWORD bulunamadı. .env dosyanı kontrol et."
    )


device = -1

print("Sentiment analizi CPU üzerinde çalışacak.")

print("\nSentiment modeli yükleniyor...")

sentiment_model = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
    top_k=None,
    device=device
)

print("Model hazır.")

TOTAL_LIMIT = 49918

BATCH_SIZE = 8

DB_BATCH_SIZE = 500

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

cursor = conn.cursor()

print("Database bağlantısı başarılı.")

cursor.execute("""
CREATE TABLE IF NOT EXISTS review_analysis (
    id SERIAL PRIMARY KEY,
    review_id INTEGER UNIQUE NOT NULL
        REFERENCES reviews(id)
        ON DELETE CASCADE,
    sentiment VARCHAR(20),
    sentiment_score NUMERIC(6,4),
    confidence_score NUMERIC(6,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

conn.commit()

print("review_analysis tablosu hazır.")

print("\nAnaliz edilecek yorumlar database'den alınıyor...")

cursor.execute("""
SELECT
    r.id,
    r.review_text
FROM reviews r
LEFT JOIN review_analysis ra
    ON r.id = ra.review_id
WHERE ra.review_id IS NULL
ORDER BY r.id
LIMIT %s;
""", (TOTAL_LIMIT,))

reviews = cursor.fetchall()

print(
    f"Yeni analiz edilecek yorum sayısı: {len(reviews):,}"
)

if not reviews:

    print("\nAnaliz edilecek yeni yorum bulunamadı.")

    cursor.execute("""
        SELECT COUNT(*)
        FROM review_analysis;
    """)

    total_analysis = cursor.fetchone()[0]

    print(
        f"review_analysis toplam kayıt: {total_analysis:,}"
    )

    cursor.close()
    conn.close()

    raise SystemExit

start_time = time()

sentiment_counts = Counter()

db_records = []

total = len(reviews)

print("\nSentiment analizi başlıyor...")

for start in range(0, total, BATCH_SIZE):

    batch = reviews[start:start + BATCH_SIZE]

    texts = []

    valid_reviews = []

    for review_id, review_text in batch:

        if not review_text:
            continue

        text = str(review_text).strip()

        if not text:
            continue

        texts.append(text)
        valid_reviews.append(review_id)

    if not texts:
        continue

    try:

        results = sentiment_model(
         texts,
         batch_size=BATCH_SIZE,
         truncation=True,
         max_length=512
)

    except RuntimeError as e:

      print("\nSentiment analizi sırasında hata oluştu.")
      print("Hatalı batch başlangıcı:", start)
      print("Hata:", e)

      conn.rollback()

      cursor.close()
      conn.close()

      raise

    for review_id, result_list in zip(
        valid_reviews,
        results
    ):

        scores = {
            item["label"].lower():
            float(item["score"])
            for item in result_list
        }

        sentiment = max(
            scores,
            key=scores.get
        )

        confidence = scores[sentiment]


        if sentiment == "negative":

            sentiment_score = -confidence

        elif sentiment == "positive":

            sentiment_score = confidence

        else:

            sentiment_score = 0.0


        sentiment_counts[sentiment] += 1


        db_records.append(
            (
                review_id,
                sentiment,
                round(sentiment_score, 4),
                round(confidence, 4)
            )
        )

    processed = min(
        start + BATCH_SIZE,
        total
    )

    if processed % 1000 < BATCH_SIZE or processed == total:

        print(
            f"İşlenen: "
            f"{processed:,} / {total:,} "
            f"(%{processed / total * 100:.1f})"
        )

    if len(db_records) >= DB_BATCH_SIZE:

        execute_batch(
            cursor,
            """
            INSERT INTO review_analysis
            (
                review_id,
                sentiment,
                sentiment_score,
                confidence_score
            )
            VALUES (%s, %s, %s, %s)

            ON CONFLICT (review_id)
            DO UPDATE SET
                sentiment = EXCLUDED.sentiment,
                sentiment_score = EXCLUDED.sentiment_score,
                confidence_score = EXCLUDED.confidence_score;
            """,
            db_records,
            page_size=DB_BATCH_SIZE
        )

        conn.commit()

        db_records.clear()

if db_records:

    execute_batch(
        cursor,
        """
        INSERT INTO review_analysis
        (
            review_id,
            sentiment,
            sentiment_score,
            confidence_score
        )
        VALUES (%s, %s, %s, %s)

        ON CONFLICT (review_id)
        DO UPDATE SET
            sentiment = EXCLUDED.sentiment,
            sentiment_score = EXCLUDED.sentiment_score,
            confidence_score = EXCLUDED.confidence_score;
        """,
        db_records,
        page_size=DB_BATCH_SIZE
    )

    conn.commit()

cursor.execute("""
SELECT COUNT(*)
FROM review_analysis;
""")

db_count = cursor.fetchone()[0]

cursor.execute("""
SELECT
    sentiment,
    COUNT(*)
FROM review_analysis
GROUP BY sentiment
ORDER BY COUNT(*) DESC;
""")

distribution = cursor.fetchall()
elapsed = time() - start_time

print("\n" + "=" * 70)
print("SENTIMENT ANALİZ ÖZETİ")
print("=" * 70)

print(
    f"Bu çalıştırmada analiz edilen: {total:,}"
)

print(
    f"Database'deki toplam sentiment kaydı: "
    f"{db_count:,}"
)

print("\nSentiment dağılımı:")
print("-" * 40)

for sentiment, count in distribution:

    print(
        f"{sentiment:<15} {count:,}"
    )

print(
    f"\nToplam süre: {elapsed / 60:.2f} dakika"
)

print("=" * 70)
print("SENTIMENT ANALİZİ TAMAMLANDI")
print("=" * 70)

cursor.close()
conn.close()