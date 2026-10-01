
import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv


print("=" * 70)
print("INSIGHTFLOW - AI SENTIMENT DATABASE AKTARIMI")
print("=" * 70)
load_dotenv()

CSV_FILE = r"C:\Users\asinc\OneDrive\Masaüstü\InsightFlow\data\processed\ai_sentiment_50000.csv"

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

BATCH_SIZE = 500


print("\nAI sentiment CSV dosyası okunuyor...")

df = pd.read_csv(CSV_FILE)

print(f"CSV kayıt sayısı: {len(df):,}")

required_columns = [
    "Review_Text",
    "Star_Rating",
    "model_sentiment",
    "confidence"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]


if missing_columns:

    print("\nEksik kolonlar bulundu:")

    for column in missing_columns:
        print(f"- {column}")

    raise SystemExit


print("Gerekli kolonların tamamı mevcut.")


print("\nDatabase bağlantısı kuruluyor...")

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

cursor = conn.cursor()

print("Database bağlantısı başarılı.")



print("\nAI datasetindeki analiz durumları kontrol ediliyor...")

cursor.execute("""
SELECT COUNT(*)
FROM reviews r
JOIN datasets d
    ON d.id = r.dataset_id
LEFT JOIN review_analysis ra
    ON ra.review_id = r.id
WHERE d.name = 'Generative AI Reviews 50K'
  AND ra.review_id IS NULL;
""")

missing_count = cursor.fetchone()[0]

print(
    f"Database'de analiz edilmemiş AI yorumu: "
    f"{missing_count:,}"
)


print("\nCSV ve Database kayıtları eşleştiriliyor...")

cursor.execute("""
SELECT
    r.id,
    r.review_id,
    r.review_text,
    r.rating
FROM reviews r
JOIN datasets d
    ON d.id = r.dataset_id
WHERE d.name = 'Generative AI Reviews 50K'
ORDER BY r.id;
""")

db_reviews = cursor.fetchall()

print(
    f"Database AI kayıt sayısı: "
    f"{len(db_reviews):,}"
)

if len(df) != len(db_reviews):

    print("\n⚠ CSV ve Database kayıt sayıları eşleşmiyor!")

    cursor.close()
    conn.close()

    raise SystemExit


print("CSV ve Database kayıt sayıları eşleşiyor.")


# ---------------------------------------------------------
# METİN + RATING EŞLEŞMESİ
# ---------------------------------------------------------

match_count = 0

for index, db_row in enumerate(db_reviews):

    csv_row = df.iloc[index]

    db_text = str(db_row[2]).strip()
    csv_text = str(csv_row["Review_Text"]).strip()

    db_rating = db_row[3]
    csv_rating = csv_row["Star_Rating"]

    if db_text == csv_text and db_rating == csv_rating:
        match_count += 1


print(
    f"Metin + rating eşleşmesi: "
    f"{match_count:,} / {len(df):,}"
)


# Eşleşme tam değilse aktarımı durdur
if match_count != len(df):

    print("\n⚠ Eşleşme tam olmadığı için aktarım durduruldu.")

    cursor.close()
    conn.close()

    raise SystemExit


print("\n" + "=" * 70)
print("AKTARIM ÖNCESİ KONTROL")
print("=" * 70)

print(f"CSV toplam kayıt       : {len(df):,}")
print(f"Database AI kayıtları  : {len(db_reviews):,}")
print(f"Database eksik kayıt   : {missing_count:,}")

print("\nEşleşme kontrolü başarılı.")
print("Aktarım başlatılıyor...")


cursor.execute("""
SELECT review_id
FROM review_analysis;
""")

existing_analysis_ids = {
    row[0]
    for row in cursor.fetchall()
}

print(
    f"\nMevcut review_analysis kayıtları: "
    f"{len(existing_analysis_ids):,}"
)



records_to_insert = []

for index, db_row in enumerate(db_reviews):

    db_id = db_row[0]

    if db_id in existing_analysis_ids:
        continue

    csv_row = df.iloc[index]

    sentiment = str(
        csv_row["model_sentiment"]
    ).lower()

    confidence = float(
        csv_row["confidence"]
    )



    if sentiment == "positive":

        sentiment_score = confidence

    elif sentiment == "negative":

        sentiment_score = -confidence

    elif sentiment == "neutral":

        sentiment_score = 0

    else:

        print(
            f"\n⚠ Beklenmeyen sentiment: "
            f"{sentiment}"
        )

        cursor.close()
        conn.close()

        raise SystemExit


    records_to_insert.append((
        db_id,
        sentiment,
        sentiment_score,
        confidence
    ))


print(
    f"\nAktarılacak yeni kayıt sayısı: "
    f"{len(records_to_insert):,}"
)



print("\n" + "=" * 70)
print("AI SENTIMENT AKTARIMI BAŞLIYOR")
print("=" * 70)

total_inserted = 0


for start in range(
    0,
    len(records_to_insert),
    BATCH_SIZE
):

    batch = records_to_insert[
        start:start + BATCH_SIZE
    ]


    cursor.executemany("""
        INSERT INTO review_analysis
        (
            review_id,
            sentiment,
            sentiment_score,
            confidence_score
        )
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (review_id) DO NOTHING;
    """, batch)


    conn.commit()


    total_inserted += len(batch)


    processed = min(
        start + BATCH_SIZE,
        len(records_to_insert)
    )


    print(
        f"Aktarılan: "
        f"{processed:,} / "
        f"{len(records_to_insert):,} "
        f"({processed / len(records_to_insert) * 100:.1f}%)"
    )



print("\n" + "=" * 70)
print("AKTARIM TAMAMLANDI")
print("=" * 70)

print(
    f"İşleme alınan yeni kayıt: "
    f"{total_inserted:,}"
)


print("\n" + "=" * 70)
print("AI DATABASE SON KONTROLÜ")
print("=" * 70)


cursor.execute("""
SELECT COUNT(*)
FROM reviews r
JOIN datasets d
    ON d.id = r.dataset_id
WHERE d.name = 'Generative AI Reviews 50K';
""")

ai_review_count = cursor.fetchone()[0]


cursor.execute("""
SELECT COUNT(*)
FROM reviews r
JOIN datasets d
    ON d.id = r.dataset_id
JOIN review_analysis ra
    ON ra.review_id = r.id
WHERE d.name = 'Generative AI Reviews 50K';
""")

ai_analysis_count = cursor.fetchone()[0]


cursor.execute("""
SELECT COUNT(*)
FROM reviews r
JOIN datasets d
    ON d.id = r.dataset_id
LEFT JOIN review_analysis ra
    ON ra.review_id = r.id
WHERE d.name = 'Generative AI Reviews 50K'
  AND ra.review_id IS NULL;
""")

ai_missing_count = cursor.fetchone()[0]


print(
    f"AI toplam review       : "
    f"{ai_review_count:,}"
)

print(
    f"AI toplam analysis     : "
    f"{ai_analysis_count:,}"
)

print(
    f"AI analizsiz review    : "
    f"{ai_missing_count:,}"
)



print("\n" + "=" * 70)
print("AI SENTIMENT DAĞILIMI")
print("=" * 70)

cursor.execute("""
SELECT
    ra.sentiment,
    COUNT(*)
FROM reviews r
JOIN datasets d
    ON d.id = r.dataset_id
JOIN review_analysis ra
    ON ra.review_id = r.id
WHERE d.name = 'Generative AI Reviews 50K'
GROUP BY ra.sentiment
ORDER BY ra.sentiment;
""")

sentiment_distribution = cursor.fetchall()


for sentiment, count in sentiment_distribution:

    print(
        f"{sentiment:<10} : "
        f"{count:,}"
    )


print("\n" + "=" * 70)
print("SONUÇ")
print("=" * 70)


if (
    ai_review_count == 50000
    and ai_analysis_count == 50000
    and ai_missing_count == 0
):

    print("✓ 50.000 AI yorumunun tamamı analiz edildi.")
    print("✓ 50.000 AI sentiment sonucu database'e aktarıldı.")
    print("✓ Analizsiz AI yorumu kalmadı.")

else:

    print("⚠ Aktarım sonrası beklenmeyen bir durum oluştu.")
    print("⚠ Yukarıdaki sayıları kontrol et.")



cursor.close()
conn.close()

print("\nDatabase bağlantısı kapatıldı.")
print("İşlem tamamlandı.")

