import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

cursor = conn.cursor()

print("=" * 70)
print("INSIGHTFLOW - SAAS TOPIC SUMMARY DATABASE AKTARIMI")
print("=" * 70)

print("\nPostgreSQL bağlantısı başarılı.")

cursor.execute("""
    SELECT
        rt.topic,

        COUNT(*) AS review_count,

        COUNT(*) FILTER (
            WHERE ra.sentiment = 'positive'
        ) AS positive_count,

        COUNT(*) FILTER (
            WHERE ra.sentiment = 'negative'
        ) AS negative_count,

        COUNT(*) FILTER (
            WHERE ra.sentiment = 'neutral'
        ) AS neutral_count,

        ROUND(AVG(r.rating)::numeric, 2) AS average_rating

    FROM review_topics rt

    JOIN reviews r
        ON r.id = rt.review_id

    LEFT JOIN review_analysis ra
        ON ra.review_id = r.id

    WHERE r.dataset_id = 1

    GROUP BY rt.topic

    ORDER BY review_count DESC;
""")

results = cursor.fetchall()

print(f"Bulunan topic sayısı: {len(results)}")

cursor.execute("""
    DELETE FROM topic_summary
    WHERE sector = 'Bilişim'
      AND product_area = 'SaaS';
""")

deleted_count = cursor.rowcount

print(f"Eski SaaS topic_summary kayıtları silindi: {deleted_count}")


inserted_count = 0

for row in results:

    topic = row[0]
    review_count = row[1]
    positive_count = row[2]
    negative_count = row[3]
    neutral_count = row[4]
    average_rating = row[5]

    cursor.execute("""
        INSERT INTO topic_summary (
            sector,
            product_area,
            topic,
            review_count,
            positive_count,
            negative_count,
            neutral_count,
            average_rating,
            period
        )
        VALUES (
            'Bilişim',
            'SaaS',
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            '2026'
        );
    """, (
        topic,
        review_count,
        positive_count,
        negative_count,
        neutral_count,
        average_rating
    ))

    inserted_count += 1



conn.commit()

print(f"Topic summary kayıtları aktarıldı: {inserted_count}")



cursor.execute("""
    SELECT
        topic,
        review_count,
        positive_count,
        negative_count,
        neutral_count,
        average_rating,
        period
    FROM topic_summary
    WHERE sector = 'Bilişim'
      AND product_area = 'SaaS'
    ORDER BY review_count DESC;
""")

summary_results = cursor.fetchall()


print("\nSaaS Topic Summary:")
print("-" * 90)

for row in summary_results:

    print(
        f"{row[0]:25} | "
        f"reviews: {row[1]:5} | "
        f"positive: {row[2]:5} | "
        f"negative: {row[3]:5} | "
        f"neutral: {row[4]:5} | "
        f"rating: {row[5]} | "
        f"period: {row[6]}"
    )



cursor.execute("""
    SELECT
        COUNT(*),
        SUM(review_count)
    FROM topic_summary
    WHERE sector = 'Bilişim'
      AND product_area = 'SaaS';
""")

topic_count, total_review_count = cursor.fetchone()

print("\nKontrol:")
print(f"Topic summary kayıt sayısı: {topic_count}")
print(f"Topic-review toplamı: {total_review_count}")


cursor.close()
conn.close()

print("\n" + "=" * 70)
print("SAAS TOPIC SUMMARY AKTARIMI TAMAMLANDI")
print("=" * 70)