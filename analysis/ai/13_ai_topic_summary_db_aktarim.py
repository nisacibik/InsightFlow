import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv


print("=" * 70)
print("INSIGHTFLOW - AI TOPIC SUMMARY DB AKTARIMI")
print("=" * 70)


BASE_DIR = r"C:\Users\asinc\OneDrive\Masaüstü\InsightFlow"

INPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "ai_sentiment_50000.csv"
)

ENV_FILE = os.path.join(
    BASE_DIR,
    ".env"
)


print("\nAI sentiment verisi okunuyor...")

if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(
        f"Dosya bulunamadı:\n{INPUT_FILE}"
    )

df = pd.read_csv(INPUT_FILE)

print(f"Toplam yorum: {len(df):,}")


required_columns = [
    "Review_Theme",
    "Star_Rating",
    "model_sentiment"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Eksik kolonlar: {missing_columns}"
    )

print("Gerekli kolonlar bulundu.")


df["Review_Theme"] = (
    df["Review_Theme"]
    .fillna("Unknown")
    .astype(str)
    .str.strip()
)

df["Star_Rating"] = pd.to_numeric(
    df["Star_Rating"],
    errors="coerce"
)

df["model_sentiment"] = (
    df["model_sentiment"]
    .fillna("unknown")
    .astype(str)
    .str.strip()
    .str.lower()
)


summary = (
    df.groupby("Review_Theme")
    .agg(
        review_count=("Review_Theme", "size"),

        positive_count=(
            "model_sentiment",
            lambda x: (x == "positive").sum()
        ),

        negative_count=(
            "model_sentiment",
            lambda x: (x == "negative").sum()
        ),

        neutral_count=(
            "model_sentiment",
            lambda x: (x == "neutral").sum()
        ),

        average_rating=(
            "Star_Rating",
            "mean"
        )
    )
    .reset_index()
)

summary["average_rating"] = (
    summary["average_rating"]
    .round(2)
)

print("\n" + "=" * 70)
print("AI TEMA ÖZETİ")
print("=" * 70)

print(
    summary.to_string(index=False)
)


print("\n" + "=" * 70)
print("KONTROL")
print("=" * 70)

print(
    f"Tema sayısı          : {len(summary)}"
)

print(
    f"Toplam yorum         : "
    f"{summary['review_count'].sum():,}"
)

print(
    f"Toplam pozitif       : "
    f"{summary['positive_count'].sum():,}"
)

print(
    f"Toplam negatif       : "
    f"{summary['negative_count'].sum():,}"
)

print(
    f"Toplam nötr          : "
    f"{summary['neutral_count'].sum():,}"
)


print("\nPostgreSQL bağlantısı hazırlanıyor...")

if not os.path.exists(ENV_FILE):
    raise FileNotFoundError(
        f".env dosyası bulunamadı:\n{ENV_FILE}"
    )

load_dotenv(ENV_FILE)

try:

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    print("PostgreSQL bağlantısı başarılı.")

except Exception as e:

    raise ConnectionError(
        f"PostgreSQL bağlantısı kurulamadı:\n{e}"
    )


try:

    cursor = conn.cursor()

    print("\nMevcut AI topic summary kayıtları kontrol ediliyor...")

    cursor.execute("""
        DELETE FROM topic_summary
        WHERE sector = 'Bilişim'
          AND product_area = 'AI';
    """)

    deleted_count = cursor.rowcount

    print(
        f"Mevcut AI kayıtları: {deleted_count}"
    )


    print("\nAI tema özetleri veritabanına aktarılıyor...")

    inserted_count = 0

    for _, row in summary.iterrows():

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
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            );
        """, (
            "Bilişim",
            "AI",
            row["Review_Theme"],
            int(row["review_count"]),
            int(row["positive_count"]),
            int(row["negative_count"]),
            int(row["neutral_count"]),
            float(row["average_rating"]),
            "2026"
        ))

        inserted_count += 1

    conn.commit()

    print(
        f"Eklenen AI tema kaydı: {inserted_count}"
    )

except Exception as e:

    conn.rollback()

    raise RuntimeError(
        f"Veritabanı aktarımı sırasında hata oluştu:\n{e}"
    )

finally:

    cursor.close()
    conn.close()

# ------------------------------------------------------------
# 11. SONUÇ
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("AKTARIM TAMAMLANDI")
print("=" * 70)

print(
    f"Silinen eski AI kayıtları : {deleted_count}"
)

print(
    f"Eklenen yeni AI kayıtları : {inserted_count}"
)

print(
    f"Toplam AI yorum           : "
    f"{summary['review_count'].sum():,}"
)

print("\nAI topic_summary aktarımı başarıyla tamamlandı.")