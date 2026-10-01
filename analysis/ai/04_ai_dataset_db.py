import os
import psycopg2
from dotenv import load_dotenv


print("=" * 70)
print("INSIGHTFLOW - AI DATASET DATABASE KAYDI")
print("=" * 70)
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

print("\nDatabase bağlantısı başarılı.")

cursor.execute("""
INSERT INTO datasets (
    name,
    subsector,
    data_period,
    description,
    record_count,
    source,
    url,
    license
)
VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s
)
RETURNING id;
""", (
    "Generative AI Reviews 50K",
    "AI",
    "2025-2026",
    "ChatGPT, Microsoft Copilot, Google Gemini, Perplexity ve Claude uygulamalarına ait kullanıcı yorumlarından oluşan veri seti.",
    50000,
    "Generative AI Reviews 50K",
    "https://huggingface.co/datasets/jahnavik186/generative-ai-reviews-50k",
    "CC-BY-NC-4.0"
))

dataset_id = cursor.fetchone()[0]

conn.commit()
cursor.execute("""
SELECT
    id,
    name,
    subsector,
    data_period,
    record_count,
    source
FROM datasets
WHERE id = %s;
""", (dataset_id,))

result = cursor.fetchone()

print("\nEklenen dataset:")
print(result)

cursor.close()
conn.close()

print("\n" + "=" * 70)
print("AI DATASET DATABASE KAYDI TAMAMLANDI")
print("=" * 70)