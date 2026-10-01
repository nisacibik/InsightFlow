import os
import sys
import pandas as pd
import psycopg2
from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CSV_FILE = os.path.join(
    BASE_DIR,
    "..",
    "data",
    "processed",
    "ai_sentiment_50000.csv"
)

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

DATASET_ID = 2


print("=" * 70)
print("INSIGHTFLOW - AI REVIEW TOPICS DB AKTARIMI")
print("=" * 70)

print("\nAI tema verisi okunuyor...")

if not os.path.exists(CSV_FILE):
    print(f"Dosya bulunamadı: {CSV_FILE}")
    sys.exit()

df = pd.read_csv(CSV_FILE)

print(f"Toplam CSV kaydı: {len(df):,}")

required_columns = ["Review_Theme"]

for column in required_columns:
    if column not in df.columns:
        print(f"Eksik kolon: {column}")
        sys.exit()

print("Gerekli kolonlar bulundu.")


print("\nPostgreSQL bağlantısı kuruluyor...")

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

print("Bağlantı başarılı.")


print("\nAI review ID'leri veritabanından okunuyor...")

cur.execute("""
    SELECT id, review_id
    FROM reviews
    WHERE dataset_id = %s
    ORDER BY id
""", (DATASET_ID,))

db_reviews = cur.fetchall()

print(f"DB'deki AI review sayısı: {len(db_reviews):,}")


print("\nCSV ve DB kayıtları eşleştiriliyor...")

db_mapping = {
    review_id: db_id
    for db_id, review_id in db_reviews
}

matched = 0
unmatched = 0
insert_data = []

for _, row in df.iterrows():

    csv_index = int(_)

    review_id = 100001 + csv_index

    if review_id not in db_mapping:
        unmatched += 1
        continue

    db_review_id = db_mapping[review_id]

    theme = str(row["Review_Theme"]).strip()

    if not theme:
        theme = "Unknown"

    insert_data.append(
        (
            db_review_id,
            theme,
            None
        )
    )

    matched += 1


print(f"Eşleşen kayıt: {matched:,}")
print(f"Eşleşmeyen kayıt: {unmatched:,}")



if unmatched > 0:
    print("\nUYARI: Eşleşmeyen kayıtlar var.")
    print("Aktarım iptal edildi.")
    conn.rollback()
    cur.close()
    conn.close()
    sys.exit()

if matched != len(df):
    print("\nUYARI: CSV kayıtlarının tamamı hazırlanamadı.")
    print("Aktarım iptal edildi.")
    conn.rollback()
    cur.close()
    conn.close()
    sys.exit()



print("\nAI tema kayıtları PostgreSQL'e aktarılıyor...")

insert_query = """
    INSERT INTO review_topics
        (review_id, topic, score)
    VALUES
        (%s, %s, %s)
"""

cur.executemany(insert_query, insert_data)

conn.commit()

print(f"Eklenen topic kaydı: {len(insert_data):,}")



cur.execute("""
    SELECT COUNT(*)
    FROM review_topics rt
    JOIN reviews r ON r.id = rt.review_id
    WHERE r.dataset_id = %s
""", (DATASET_ID,))

total = cur.fetchone()[0]

print("\nDB KONTROLÜ")
print("-" * 40)
print(f"AI review_topics toplamı: {total:,}")


print("\nTema dağılımı:")

cur.execute("""
    SELECT
        rt.topic,
        COUNT(*) AS adet
    FROM review_topics rt
    JOIN reviews r ON r.id = rt.review_id
    WHERE r.dataset_id = %s
    GROUP BY rt.topic
    ORDER BY adet DESC
""", (DATASET_ID,))

for topic, count in cur.fetchall():
    print(f"{topic:<25} {count:,}")



cur.close()
conn.close()

print("\n" + "=" * 70)
print("AI REVIEW TOPICS AKTARIMI TAMAMLANDI.")
print("=" * 70)