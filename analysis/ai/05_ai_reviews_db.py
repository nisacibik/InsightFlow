import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv


print("=" * 70)
print("INSIGHTFLOW - AI REVIEWS DATABASE AKTARIMI")
print("=" * 70)
load_dotenv()

INPUT_PATH = "../data/processed/ai/ai_final.csv"

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

print("\nAI final dataset okunuyor...")

df = pd.read_csv(INPUT_PATH)

print(f"CSV kayıt sayısı: {len(df):,}")

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
SELECT id, name, record_count
FROM datasets
WHERE id = 2;
""")

dataset = cursor.fetchone()

if dataset is None:
    raise Exception("Dataset ID=2 bulunamadı.")

print(f"\nDataset bulundu: {dataset}")

cursor.execute("""
SELECT COUNT(*)
FROM reviews
WHERE dataset_id = 2;
""")

existing_count = cursor.fetchone()[0]

print(f"Database'de mevcut AI yorum sayısı: {existing_count:,}")


if existing_count > 0:
    print("\nAI yorumları zaten database'de mevcut.")
    print("Yeni aktarım yapılmayacak.")

    cursor.close()
    conn.close()
    exit()

print("\n50.000 AI yorumu aktarılıyor...")

insert_query = """
INSERT INTO reviews (
    review_id,
    dataset_id,
    product_id,
    review_text,
    source,
    rating,
    language,
    product_area,
    review_date,
    helpful_count,
    verified_purchase
)
VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
)
"""

batch_size = 1000
inserted = 0

for start in range(0, len(df), batch_size):

    batch = df.iloc[start:start + batch_size]

    records = []

    for _, row in batch.iterrows():

        records.append((
            int(row["review_id"]),
            int(row["dataset_id"]),
            row["product_id"],
            row["review_text"],
            row["source"],
            int(row["rating"]),
            row["language"],
            row["product_area"],
            pd.to_datetime(row["review_date"]).to_pydatetime(),
            int(row["helpful_count"]),
            None
        ))

    cursor.executemany(insert_query, records)

    conn.commit()

    inserted += len(records)

    print(f"Aktarıldı: {inserted:,} / {len(df):,}")


cursor.execute("""
SELECT COUNT(*)
FROM reviews
WHERE dataset_id = 2;
""")

db_count = cursor.fetchone()[0]

print("\n" + "=" * 70)
print("AKTARIM SONUCU")
print("=" * 70)

print(f"CSV kayıt sayısı     : {len(df):,}")
print(f"Database kayıt sayısı: {db_count:,}")


if db_count == len(df):
    print("\n✓ 50.000 yorum başarıyla aktarıldı.")
else:
    print("\n⚠ Kayıt sayılarında fark var!")


cursor.execute("""
SELECT product_id, COUNT(*)
FROM reviews
WHERE dataset_id = 2
GROUP BY product_id
ORDER BY product_id;
""")

print("\nUygulama dağılımı:")

for product, count in cursor.fetchall():
    print(f"- {product}: {count:,}")


cursor.close()
conn.close()

print("\n" + "=" * 70)
print("AI REVIEWS DATABASE AKTARIMI TAMAMLANDI")
print("=" * 70)