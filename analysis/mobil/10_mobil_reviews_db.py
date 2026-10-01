import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from dotenv import load_dotenv
import os

print("=" * 70)
print("INSIGHTFLOW - MOBİL REVIEWS DB AKTARIMI")
print("=" * 70)

print("\n.env dosyası okunuyor...")

load_dotenv()

print("\nMobil veri okunuyor...")

df = pd.read_csv("../data/processed/mobil_cleaned.csv")

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
    FROM reviews
    WHERE dataset_id = 3
""")

existing_count = cursor.fetchone()[0]

print("DB'deki mevcut mobil kayıt:", existing_count)

if existing_count >= len(df):

    print("\nMobil kayıtların tamamı zaten DB'de.")
    print("Yeni kayıt eklenmedi.")

else:

    remaining_df = df.iloc[existing_count:].copy()

    print("Aktarılacak yeni kayıt:", len(remaining_df))

    cursor.execute("""
        SELECT COALESCE(MAX(review_id), 0)
        FROM reviews
    """)

    max_review_id = cursor.fetchone()[0]

    print("Mevcut maksimum review_id:", max_review_id)

    insert_data = []

    for index, row in remaining_df.iterrows():

        new_review_id = max_review_id + index - existing_count + 1

        insert_data.append(
            (
                new_review_id,
                3,
                str(row["app_id"]),
                row["review_text"],
                "Play Market",
                int(row["review_score"]),
                "en",
                "Mobil Uygulamalar",
                row["review_date"],
                int(row["helpful_count"])
            )
        )

    print("\nMobil yorumlar DB'ye aktarılıyor...")

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
        helpful_count
    )
    VALUES (
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s
    )
    """

    execute_batch(
        cursor,
        insert_query,
        insert_data,
        page_size=1000
    )

    conn.commit()

    print(f"{len(insert_data)} mobil yorum başarıyla eklendi.")

cursor.execute("""
    SELECT COUNT(*)
    FROM reviews
    WHERE dataset_id = 3
""")

final_count = cursor.fetchone()[0]

print("\nDB'deki mobil kayıt sayısı:", final_count)


cursor.close()
conn.close()

print("\nMobil reviews aktarımı tamamlandı.")