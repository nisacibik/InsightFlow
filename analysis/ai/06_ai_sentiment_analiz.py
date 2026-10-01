import os
import time
import psycopg2
import unicodedata
from dotenv import load_dotenv
from transformers import pipeline


print("=" * 70)
print("INSIGHTFLOW - AI SENTIMENT TEST")
print("=" * 70)

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

TEST_LIMIT = 1000
BATCH_SIZE = 32


print("\nSentiment modeli yükleniyor...")

sentiment_model = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
    top_k=None,
    device=-1
)

print("Sentiment modeli hazır.")
print("Analiz CPU üzerinde çalışacak.")


conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

cursor = conn.cursor()

print("\nDatabase bağlantısı başarılı.")


cursor.execute("""
SELECT
    r.id,
    r.review_id,
    r.product_id,
    r.review_text,
    r.rating
FROM reviews r
WHERE r.dataset_id = 2
ORDER BY r.id
LIMIT %s;
""", (TEST_LIMIT,))

reviews = cursor.fetchall()

total = len(reviews)

print(f"Test edilecek yorum sayısı: {total:,}")


if total == 0:
    print("\nTest edilecek AI yorumu bulunamadı.")

    cursor.close()
    conn.close()
    exit()


print("\nSentiment analizi başlıyor...")

start_time = time.time()

all_results = []

for start in range(0, total, BATCH_SIZE):

    batch = reviews[start:start + BATCH_SIZE]

    texts = [
    unicodedata.normalize("NFKC", row[3])
    for row in batch
]

    results = sentiment_model(
        texts,
        batch_size=BATCH_SIZE,
        truncation=True,
        max_length=512
    )

    for row, result in zip(batch, results):
        result = sorted(
            result,
            key=lambda x: x["score"],
            reverse=True
        )

        top_result = result[0]

        label = top_result["label"].lower()
        confidence = float(top_result["score"])


        if label == "label_2":
            sentiment = "positive"

        elif label == "label_1":
            sentiment = "neutral"

        elif label == "label_0":
            sentiment = "negative"

        else:
            sentiment = label


        if sentiment == "positive":
            sentiment_score = confidence

        elif sentiment == "negative":
            sentiment_score = -confidence

        else:
            sentiment_score = 0


        all_results.append({
            "db_id": row[0],
            "review_id": row[1],
            "product_id": row[2],
            "review_text": row[3],
            "rating": row[4],
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "confidence": confidence
        })


    processed = min(start + BATCH_SIZE, total)

    print(
        f"İşlenen: {processed:,} / {total:,} "
        f"({processed / total * 100:.1f}%)"
    )


elapsed = time.time() - start_time

positive_count = sum(
    1 for x in all_results
    if x["sentiment"] == "positive"
)

negative_count = sum(
    1 for x in all_results
    if x["sentiment"] == "negative"
)

neutral_count = sum(
    1 for x in all_results
    if x["sentiment"] == "neutral"
)

print("\n" + "=" * 70)
print("SENTIMENT TEST SONUCU")
print("=" * 70)

print(f"Toplam test yorumu : {total:,}")
print(f"Positive           : {positive_count:,}")
print(f"Negative           : {negative_count:,}")
print(f"Neutral            : {neutral_count:,}")

print(
    f"\nPositive oranı: "
    f"{positive_count / total * 100:.2f}%"
)

print(
    f"Negative oranı: "
    f"{negative_count / total * 100:.2f}%"
)

print(
    f"Neutral oranı: "
    f"{neutral_count / total * 100:.2f}%"
)

print(
    f"\nToplam analiz süresi: "
    f"{elapsed / 60:.2f} dakika"
)


print("\n" + "=" * 70)
print("RATING - SENTIMENT KONTROLÜ")
print("=" * 70)

for rating in range(1, 6):

    rating_results = [
        x for x in all_results
        if x["rating"] == rating
    ]

    if len(rating_results) == 0:
        continue

    pos = sum(
        1 for x in rating_results
        if x["sentiment"] == "positive"
    )

    neg = sum(
        1 for x in rating_results
        if x["sentiment"] == "negative"
    )

    neu = sum(
        1 for x in rating_results
        if x["sentiment"] == "neutral"
    )

    print(
        f"\n{rating} yıldız ({len(rating_results):,} yorum):"
    )

    print(f"  Positive: {pos:,}")
    print(f"  Negative: {neg:,}")
    print(f"  Neutral : {neu:,}")


print("\n" + "=" * 70)
print("ÖRNEK SENTIMENT SONUÇLARI")
print("=" * 70)


for i, result in enumerate(all_results[:10], start=1):

    print("\n" + "-" * 70)

    print(f"Örnek #{i}")
    print(f"Uygulama : {result['product_id']}")
    print(f"Rating   : {result['rating']}")

    print("\nYorum:")
    print(result["review_text"][:500])

    print(
        f"\nModel sonucu      : {result['sentiment']}"
    )

    print(
        f"Sentiment score   : "
        f"{result['sentiment_score']:.4f}"
    )

    print(
        f"Confidence        : "
        f"{result['confidence']:.4f}"
    )


print("\n" + "=" * 70)
print("YÜKSEK CONFIDENCE ÖRNEKLERİ")
print("=" * 70)

high_confidence = sorted(
    all_results,
    key=lambda x: x["confidence"],
    reverse=True
)[:5]


for i, result in enumerate(high_confidence, start=1):

    print("\n" + "-" * 70)

    print(f"Örnek #{i}")
    print(f"Uygulama   : {result['product_id']}")
    print(f"Rating     : {result['rating']}")
    print(f"Sentiment  : {result['sentiment']}")
    print(f"Confidence : {result['confidence']:.4f}")

    print("\nYorum:")
    print(result["review_text"][:500])



print("\n" + "=" * 70)
print("DÜŞÜK CONFIDENCE ÖRNEKLERİ")
print("=" * 70)

low_confidence = sorted(
    all_results,
    key=lambda x: x["confidence"]
)[:5]


for i, result in enumerate(low_confidence, start=1):

    print("\n" + "-" * 70)

    print(f"Örnek #{i}")
    print(f"Uygulama   : {result['product_id']}")
    print(f"Rating     : {result['rating']}")
    print(f"Sentiment  : {result['sentiment']}")
    print(f"Confidence : {result['confidence']:.4f}")

    print("\nYorum:")
    print(result["review_text"][:500])


print("\n" + "=" * 70)
print("TEST TAMAMLANDI")
print("=" * 70)

print("\n⚠ Bu test sonuçları database'e kaydedilmedi.")
print("⚠ review_analysis tablosunda değişiklik yapılmadı.")

cursor.close()
conn.close()