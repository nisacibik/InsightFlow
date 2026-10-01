import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from dotenv import load_dotenv
import os

print("=" * 70)
print("INSIGHTFLOW - MOBİL REVIEW ANALYSIS DB AKTARIMI")
print("=" * 70)


print("\n.env dosyası okunuyor...")

load_dotenv()

print("\nMobil sentiment verisi okunuyor...")

df = pd.read_csv("../data/processed/mobil_sentiment.csv")

print("Toplam CSV kayıt:", len(df))


print("\nPostgreSQL bağlantısı kuruluyor...")

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT")
)

cursor = conn.cursor()

print("PostgreSQL bağlantısı başarılı.")


cursor.execute("""
    SELECT COUNT(*)
    FROM review_analysis ra
    JOIN reviews r
        ON r.id = ra.review_id
    WHERE r.dataset_id = 3
""")

existing_count = cursor.fetchone()[0]

print("DB'deki mevcut mobil analysis kayıt:", existing_count)

print("\nMobil reviews kayıtları DB'den okunuyor...")

cursor.execute("""
    SELECT
        id,
        product_id,
        review_text
    FROM reviews
    WHERE dataset_id = 3
""")

review_rows = cursor.fetchall()

print("DB'den okunan mobil review:", len(review_rows))

print("\nEşleştirme tablosu hazırlanıyor...")

review_map = {}

for review_id, product_id, review_text in review_rows:

    key = (
        str(product_id),
        review_text
    )

    review_map[key] = review_id

print("Eşleştirme tablosu hazır.")

print("\nMevcut analysis kayıtları kontrol ediliyor...")

cursor.execute("""
    SELECT ra.review_id
    FROM review_analysis ra
    JOIN reviews r
        ON r.id = ra.review_id
    WHERE r.dataset_id = 3
""")

existing_review_ids = {
    row[0]
    for row in cursor.fetchall()
}

print(
    "DB'de zaten analysis kaydı bulunan review ID sayısı:",
    len(existing_review_ids)
)


print("\nCSV analizleri DB kayıtlarıyla eşleştiriliyor...")

insert_data = []
missing_count = 0
already_exists_count = 0

for _, row in df.iterrows():

    key = (
        str(row["app_id"]),
        row["review_text"]
    )

    review_id = review_map.get(key)

    if review_id is None:

        missing_count += 1
        continue

    if review_id in existing_review_ids:

        already_exists_count += 1
        continue

    insert_data.append(
        (
            review_id,
            row["sentiment"],
            float(row["sentiment_score"])
        )
    )

print("\nEşleşme sonucu:")
print("Yeni eklenecek:", len(insert_data))
print("Zaten mevcut:", already_exists_count)
print("Eşleşmeyen:", missing_count)


if len(insert_data) > 0:

    print("\nYeni analysis kayıtları PostgreSQL'e aktarılıyor...")

    insert_query = """
        INSERT INTO review_analysis (
            review_id,
            sentiment,
            sentiment_score
        )
        VALUES (
            %s,
            %s,
            %s
        )

        ON CONFLICT ON CONSTRAINT review_analysis_review_id_key DO NOTHING    """

    execute_batch(
        cursor,
        insert_query,
        insert_data,
        page_size=1000
    )

    conn.commit()

    print(
        len(insert_data),
        "analysis kaydı başarıyla eklendi."
    )

else:

    print("\nYeni eklenecek analysis kaydı yok.")


cursor.execute("""
    SELECT review_id
    FROM review_analysis
""")

final_count = cursor.fetchone()[0]

print("\n" + "=" * 70)
print("SON KONTROL")
print("=" * 70)

print(
    "DB'deki mobil review_analysis kayıt sayısı:",
    final_count
)

print(
    "Beklenen kayıt sayısı:",
    len(df)
)


cursor.close()
conn.close()

print("\nMobil review_analysis aktarımı tamamlandı.")