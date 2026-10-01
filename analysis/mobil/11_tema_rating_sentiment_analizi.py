
import os

import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from dotenv import load_dotenv


print("=" * 70)
print("INSIGHTFLOW - MOBİL REVIEW ANALYSIS DB AKTARIMI")
print("=" * 70)
print("\n.env dosyası okunuyor...")

load_dotenv()

print("\nMobil sentiment verisi okunuyor...")

df = pd.read_csv(
    "../data/processed/mobil_sentiment.csv"
)

df["review_date"] = pd.to_datetime(
    df["review_date"],
    errors="coerce"
)

print("Toplam CSV kayıt:", len(df))


required_columns = [
    "app_id",
    "review_text",
    "review_score",
    "review_date",
    "helpful_count",
    "sentiment",
    "sentiment_score"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    print("\nEksik kolonlar bulundu:")

    for column in missing_columns:
        print("-", column)

    raise SystemExit(
        "\nGerekli kolonlar eksik olduğu için işlem durduruldu."
    )

print("Gerekli kolonların tamamı bulundu.")

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


try:

    cursor.execute("""
        SELECT COUNT(*)
        FROM review_analysis ra
        JOIN reviews r
            ON r.id = ra.review_id
        WHERE r.dataset_id = 3
    """)

    existing_count = cursor.fetchone()[0]

    print(
        "DB'deki mevcut mobil analysis kayıt:",
        existing_count
    )


    if existing_count >= len(df):

        print(
            "\nMobil sentiment analizlerinin tamamı "
            "zaten DB'de."
        )

        print("Yeni kayıt eklenmedi.")


    else:
        print(
            "\nMobil reviews kayıtları DB'den okunuyor..."
        )

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

        review_rows = cursor.fetchall()

        print(
            "DB'den okunan mobil review:",
            len(review_rows)
        )


        print(
            "\nReview ID eşleştirme tablosu hazırlanıyor..."
        )

        review_map = {}

        duplicate_key_count = 0

        for (
            review_id,
            product_id,
            review_text,
            rating,
            review_date,
            helpful_count
        ) in review_rows:

            if review_date is not None:

                review_date = (
                    pd.Timestamp(review_date)
                    .normalize()
                )

            key = (
                str(product_id),
                str(review_text),
                int(rating) if rating is not None else None,
                review_date,
                int(helpful_count)
                if helpful_count is not None
                else None
            )

            if key in review_map:
                duplicate_key_count += 1

            review_map[key] = review_id

        print("Eşleştirme tablosu hazır.")

        print(
            "Tekrarlanan eşleştirme anahtarı:",
            duplicate_key_count
        )


        print(
            "\nMevcut analysis kayıtları kontrol ediliyor..."
        )

        cursor.execute("""
            SELECT review_id
            FROM review_analysis
        """)

        existing_review_ids = {
            row[0]
            for row in cursor.fetchall()
        }

        print(
            "DB'de zaten analysis kaydı bulunan "
            "review ID sayısı:",
            len(existing_review_ids)
        )


        print(
            "\nCSV analizleri DB kayıtlarıyla eşleştiriliyor..."
        )

        insert_data = []

        missing_count = 0
        already_exists_count = 0

        pending_review_ids = set()


        for _, row in df.iterrows():

            review_date = pd.Timestamp(
                row["review_date"]
            ).normalize()

            key = (
                str(row["app_id"]),
                str(row["review_text"]),
                int(row["review_score"]),
                review_date,
                int(row["helpful_count"])
                if pd.notna(row["helpful_count"])
                else None
            )



            review_id = review_map.get(key)

            if review_id is None:

                missing_count += 1

                continue



            if review_id in existing_review_ids:

                already_exists_count += 1

                continue


            if review_id in pending_review_ids:

                already_exists_count += 1

                continue

            insert_data.append(
                (
                    review_id,
                    row["sentiment"],
                    float(row["sentiment_score"])
                )
            )

            pending_review_ids.add(review_id)


        print("\nEşleşme sonucu:")

        print(
            "Yeni eklenecek:",
            len(insert_data)
        )

        print(
            "Zaten mevcut:",
            already_exists_count
        )

        print(
            "Eşleşmeyen:",
            missing_count
        )


        if len(insert_data) > 0:

            print(
                "\nYeni analysis kayıtları "
                "PostgreSQL'e aktarılıyor..."
            )

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
                ON CONFLICT ON CONSTRAINT
                    review_analysis_review_id_key
                DO NOTHING
            """


            execute_batch(
                cursor,
                insert_query,
                insert_data,
                page_size=1000
            )


            conn.commit()


            print(
                "\nAnalysis kayıtları "
                "PostgreSQL'e aktarıldı."
            )


        else:

            print(
                "\nYeni eklenecek analysis kaydı yok."
            )


    cursor.execute("""
        SELECT COUNT(*)
        FROM review_analysis ra
        JOIN reviews r
            ON r.id = ra.review_id
        WHERE r.dataset_id = 3
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

    if final_count == len(df):

        print(
            "\nBAŞARILI:"
            "\nMobil review_analysis aktarımı "
            "tamamlandı."
        )

    else:

        print(
            "\nDİKKAT:"
            "\nDB'deki kayıt sayısı ile CSV kayıt sayısı "
            "henüz eşit değil."
        )


except Exception as e:

    conn.rollback()

    print("\nHATA OLUŞTU:")
    print(type(e).__name__)
    print(e)

    print(
        "\nİşlem geri alındı. "
        "Mevcut veriler korunuyor."
    )

    raise


finally:

    cursor.close()
    conn.close()

    print("\nPostgreSQL bağlantısı kapatıldı.")

