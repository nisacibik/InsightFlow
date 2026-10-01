import pandas as pd
import psycopg2
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

print("=" * 70)
print("INSIGHTFLOW - MOBİL REVIEW TOPICS DB AKTARIMI")
print("=" * 70)


print("\nMobil tema verisi okunuyor...")

df = pd.read_csv("../data/processed/mobil_tema.csv")

print(f"Toplam review: {len(df):,}")

print("\nPostgreSQL bağlantısı kuruluyor...")

conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    port=DB_PORT
)

cursor = conn.cursor()

print("Veritabanı bağlantısı başarılı.")


print("\nMobil review ID'leri alınıyor...")

cursor.execute("""
    SELECT
        id,
        product_id,
        review_text,
        rating,
        review_date,
        helpful_count
    FROM reviews
    WHERE dataset_id = 3
""")

reviews = cursor.fetchall()

print(f"Veritabanındaki mobil review sayısı: {len(reviews):,}")


review_map = {}

for row in reviews:
    review_id, product_id, review_text, rating, review_date, helpful_count = row

    key = (
        str(product_id),
        str(review_text),
        int(rating),
        pd.to_datetime(review_date).date(),
        int(helpful_count)
    )

    review_map[key] = review_id

print(f"Eşleştirme sözlüğü hazır: {len(review_map):,}")


theme_columns = {
    "tema_hata": "Bugs / Errors",
    "tema_guncelleme": "Updates",
    "tema_destek": "Support",
    "tema_odeme": "Payments",
    "tema_hesap": "Account / Login",
    "tema_arayuz": "Usability / Interface",
    "tema_performans": "Performance"
}


inserted = 0
unmatched = 0

for _, row in df.iterrows():

    key = (
        str(row["app_id"]),
        str(row["review_text"]),
        int(row["review_score"]),
        pd.to_datetime(row["review_date"]).date(),
        int(row["helpful_count"])
    )

    review_id = review_map.get(key)

    if review_id is None:
        unmatched += 1
        continue

    for column, topic_name in theme_columns.items():

        if bool(row[column]):

            cursor.execute("""
                INSERT INTO review_topics
                (
                    review_id,
                    topic,
                    score,
                    created_at
                )
                VALUES (%s, %s, %s, %s)
            """, (
                review_id,
                topic_name,
                None,
                datetime.now()
            ))

            inserted += 1


conn.commit()

print("\n" + "=" * 70)
print("AKTARIM TAMAMLANDI")
print("=" * 70)

print(f"CSV review sayısı       : {len(df):,}")
print(f"Eşleşmeyen review       : {unmatched:,}")
print(f"Eklenen topic kaydı     : {inserted:,}")

cursor.close()
conn.close()

print("\nVeritabanı bağlantısı kapatıldı.")
