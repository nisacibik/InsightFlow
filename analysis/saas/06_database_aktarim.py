import json
from datetime import datetime
import psycopg2
import os 
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
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

cursor = conn.cursor()

file_path = "../data/processed/saas_final.jsonl"

with open(file_path, "r", encoding="utf-8") as f:

    count = 0

    for line in f:
        data = json.loads(line)

        data["review_date"] = datetime.fromtimestamp(
            data["review_date"] / 1000
        )

        cursor.execute(
            """
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
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            )
            """,
            (
                data["review_id"],
                data["dataset_id"],
                data["product_id"],
                data["review_text"],
                data["source"],
                data["rating"],
                data["language"],
                data["product_area"],
                data["review_date"],
                data["helpful_count"],
                data["verified_purchase"]
            )
        )

        count += 1

        if count % 1000 == 0:
            conn.commit()
            print(f"{count} kayıt aktarıldı...")

conn.commit()

print(f"\nToplam {count} kayıt PostgreSQL'e aktarıldı.")

cursor.close()
conn.close()