import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from dotenv import load_dotenv

print("=" * 70)
print("INSIGHTFLOW - EKSİK MOBİL REVIEW ANALYSIS AKTARIMI")
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
).dt.normalize()

df["helpful_count"] = pd.to_numeric(
    df["helpful_count"],
    errors="coerce"
)

print("CSV kayıt sayısı:", len(df))


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


    print("\nAnalysis olmayan mobil review'lar bulunuyor...")

    cursor.execute("""
        SELECT
            r.id,
            r.product_id,
            r.review_text,
            r.rating,
            r.review_date,
            r.helpful_count
        FROM reviews r
        WHERE r.dataset_id = 3
          AND NOT EXISTS (
              SELECT 1
              FROM review_analysis ra
              WHERE ra.review_id = r.id
          )
        ORDER BY r.id
    """)

    missing_rows = cursor.fetchall()

    print(
        "Analysis olmayan mobil review sayısı:",
        len(missing_rows)
    )

    if len(missing_rows) == 0:

        print("\nEksik analysis kaydı bulunamadı.")

    else:


        print("\nEksik kayıtlar CSV ile eşleştiriliyor...")

        insert_data = []
        unmatched = []
        ambiguous = []

        for (
            review_id,
            product_id,
            review_text,
            rating,
            review_date,
            helpful_count
        ) in missing_rows:


            db_product_id = str(product_id)

            db_review_text = str(review_text)

            db_rating = int(rating)

            db_review_date = pd.Timestamp(
                review_date
            ).normalize()

            if helpful_count is not None:
                db_helpful_count = int(helpful_count)
            else:
                db_helpful_count = None


            matches = df[
                (df["app_id"].astype(str) == db_product_id)
                &
                (df["review_text"].astype(str) == db_review_text)
                &
                (df["review_score"] == db_rating)
                &
                (df["review_date"] == db_review_date)
                &
                (
                    df["helpful_count"].fillna(-1).astype(int)
                    == (
                        db_helpful_count
                        if db_helpful_count is not None
                        else -1
                    )
                )
            ]


            if len(matches) == 0:

                unmatched.append(review_id)

                continue


            if len(matches) > 1:

                ambiguous.append(
                    (
                        review_id,
                        len(matches)
                    )
                )

            match = matches.iloc[0]

            insert_data.append(
                (
                    review_id,
                    match["sentiment"],
                    float(match["sentiment_score"])
                )
            )


        print("\n" + "=" * 70)
        print("EŞLEŞME SONUCU")
        print("=" * 70)

        print(
            "Eksik review sayısı:",
            len(missing_rows)
        )

        print(
            "Eşleşen:",
            len(insert_data)
        )

        print(
            "Eşleşmeyen:",
            len(unmatched)
        )

        print(
            "Birden fazla eşleşen:",
            len(ambiguous)
        )

        if len(unmatched) > 0:

            print("\nEşleşmeyen review ID'leri:")

            for review_id in unmatched:
                print("-", review_id)

        if len(ambiguous) > 0:

            print(
                "\nBirden fazla eşleşen review'lar:"
            )

            for review_id, count in ambiguous:
                print(
                    "- review_id:",
                    review_id,
                    "| eşleşme:",
                    count
                )


        if len(insert_data) > 0:

            print(
                "\nEksik analysis kayıtları "
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
                page_size=100
            )

            conn.commit()

            print(
                "\nEksik analysis kayıtları aktarıldı."
            )

        else:

            print(
                "\nEklenecek analysis kaydı bulunamadı."
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
        "Mobil review_analysis kayıt sayısı:",
        final_count
    )

    print(
        "Beklenen kayıt sayısı:",
        len(df)
    )

    if final_count == len(df):

        print("\nBAŞARILI!")
        print(
            "Tüm 45.000 mobil review için "
            "analysis kaydı mevcut."
        )

    else:

        print(
            "\nHenüz tamamlanmadı."
        )

        print(
            "Eksik kayıt:",
            len(df) - final_count
        )

except Exception as e:

    conn.rollback()

    print("\nHATA:")
    print(type(e).__name__)
    print(e)

    raise

finally:

    cursor.close()
    conn.close()

    print("\nPostgreSQL bağlantısı kapatıldı.")