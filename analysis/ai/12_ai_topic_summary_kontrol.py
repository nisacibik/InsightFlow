import os
import pandas as pd


print("=" * 70)
print("INSIGHTFLOW - AI TEMA ÖZET KONTROLÜ")
print("=" * 70)

BASE_DIR = r"C:\Users\asinc\OneDrive\Masaüstü\InsightFlow"

INPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "ai_sentiment_50000.csv"
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


summary = (
    df.groupby("Review_Theme")
    .agg(
        review_count=("Review_Theme", "size"),
        average_rating=("Star_Rating", "mean")
    )
    .reset_index()
)


sentiment_counts = (
    pd.crosstab(
        df["Review_Theme"],
        df["model_sentiment"]
    )
    .reset_index()
)

for sentiment in ["positive", "negative", "neutral"]:
    if sentiment not in sentiment_counts.columns:
        sentiment_counts[sentiment] = 0

summary = summary.merge(
    sentiment_counts[
        [
            "Review_Theme",
            "positive",
            "negative",
            "neutral"
        ]
    ],
    on="Review_Theme",
    how="left"
)

summary["average_rating"] = (
    summary["average_rating"]
    .round(2)
)

summary = summary[
    [
        "Review_Theme",
        "review_count",
        "positive",
        "negative",
        "neutral",
        "average_rating"
    ]
]


print("\n" + "=" * 70)
print("TEMA BAZLI ÖZET")
print("=" * 70)

print(
    summary.to_string(index=False)
)


print("\n" + "=" * 70)
print("KONTROL")
print("=" * 70)

print(
    f"Toplam tema yorum sayısı: "
    f"{summary['review_count'].sum():,}"
)

print(
    f"Toplam positive: "
    f"{summary['positive'].sum():,}"
)

print(
    f"Toplam negative: "
    f"{summary['negative'].sum():,}"
)

print(
    f"Toplam neutral: "
    f"{summary['neutral'].sum():,}"
)

print("\nKontrol tamamlandı.")