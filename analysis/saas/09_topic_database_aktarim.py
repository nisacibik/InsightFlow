import os
import json
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

input_path = "../data/processed/topic_results_49918.json"


if not os.path.exists(input_path):
    raise FileNotFoundError(
        f"Topic sonuç dosyası bulunamadı: {input_path}"
    )

with open(input_path, "r", encoding="utf-8") as f:
    analysis_results = json.load(f)


print("=" * 60)
print("INSIGHTFLOW - TOPIC DATABASE AKTARIMI")
print("=" * 60)

print(f"JSON'daki yorum sayısı: {len(analysis_results)}")


if not analysis_results:
    raise ValueError("JSON dosyası boş.")

required_fields = ["db_id", "review_id", "topics"]

for index, item in enumerate(analysis_results):

    for field in required_fields:

        if field not in item:
            raise ValueError(
                f"{index}. kayıtta '{field}' alanı bulunamadı."
            )



conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

cursor = conn.cursor()

print("PostgreSQL bağlantısı başarılı.")


cursor.execute("""
    CREATE TABLE IF NOT EXISTS review_topics (
        id SERIAL PRIMARY KEY,
        review_id INTEGER NOT NULL
            REFERENCES reviews(id)
            ON DELETE CASCADE,
        topic VARCHAR(100) NOT NULL,
        score NUMERIC(5,4),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (review_id, topic)
    );
""")

conn.commit()

print("review_topics tablosu hazır.")

db_ids = [
    item["db_id"]
    for item in analysis_results
]

print(f"Kontrol edilecek DB kayıt sayısı: {len(db_ids)}")

cursor.execute(
    """
    SELECT id
    FROM reviews
    WHERE id = ANY(%s);
    """,
    (db_ids,)
)

existing_ids = {row[0] for row in cursor.fetchall()}

missing_ids = set(db_ids) - existing_ids

if missing_ids:

    conn.rollback()
    cursor.close()
    conn.close()

    raise ValueError(
        f"reviews tablosunda bulunamayan DB ID'leri var: "
        f"{sorted(missing_ids)[:10]}"
    )

print("Tüm review DB ID'leri doğrulandı.")

cursor.execute(
  """ 
DELETE FROM review_topics rt
USING reviews r
WHERE rt.review_id = r.id
 AND r.dataset_id = 1;
"""
)

deleted_count = cursor.rowcount

print(f"Eski topic kayıtları silindi: {deleted_count}")

inserted_count = 0

for item in analysis_results:

    db_id = item["db_id"]
    topics = item["topics"]

    for topic_info in topics:

        topic = topic_info.get("topic")
        score = topic_info.get("score")

        if not topic:
            continue

        cursor.execute(
            """
            INSERT INTO review_topics
                (review_id, topic, score)
            VALUES
                (%s, %s, %s)
            ON CONFLICT (review_id, topic)
            DO UPDATE SET
                score = EXCLUDED.score;
            """,
            (
                db_id,
                topic,
                score
            )
        )

        inserted_count += 1


conn.commit()

print(f"Topic kayıtları aktarıldı: {inserted_count}")


cursor.execute(
    """
    SELECT COUNT(*)
    FROM review_topics
    WHERE review_id = ANY(%s);
    """,
    (db_ids,)
)

db_topic_count = cursor.fetchone()[0]

print(f"Database'deki topic kayıt sayısı: {db_topic_count}")


cursor.execute(
    """
    SELECT topic, COUNT(*) AS topic_count
    FROM review_topics
    WHERE review_id = ANY(%s)
    GROUP BY topic
    ORDER BY topic_count DESC;
    """,
    (db_ids,)
)

topic_distribution = cursor.fetchall()


print("\nTopic dağılımı:")
print("-" * 40)

for topic, count in topic_distribution:
    print(f"{topic:<25} {count}")



cursor.close()
conn.close()

print("\n" + "=" * 60)
print("AKTARIM TAMAMLANDI")
print("=" * 60)