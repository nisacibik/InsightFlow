import os
import pandas as pd

print("=" * 70)
print("INSIGHTFLOW - AI TEMA × SENTIMENT ANALİZİ")
print("=" * 70)

BASE_DIR = r"C:\Users\asinc\OneDrive\Masaüstü\InsightFlow"

PROCESSED_DIR = os.path.join(
    BASE_DIR,
    "data",
    "processed"
)

INPUT_FILE = os.path.join(
    PROCESSED_DIR,
    "ai_sentiment_50000.csv"
)

print("\nİşlenmiş AI verisi okunuyor...")

if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(
        f"Dosya bulunamadı:\n{INPUT_FILE}"
    )

df = pd.read_csv(INPUT_FILE)

print(f"Toplam yorum sayısı: {len(df):,}")

required_columns = [
    "Review_Theme",
    "model_sentiment"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    print("\nEksik kolonlar:")

    for column in missing_columns:
        print(f"- {column}")

    raise ValueError(
        "Gerekli kolonlardan bazıları bulunamadı."
    )

print("\nGerekli kolonlar bulundu.")


df["Review_Theme"] = (
    df["Review_Theme"]
    .fillna("Unknown")
    .astype(str)
    .str.strip()
)

empty_theme = (
    df["Review_Theme"] == ""
).sum()

print(
    f"Boş tema sayısı: {empty_theme:,}"
)

df.loc[
    df["Review_Theme"] == "",
    "Review_Theme"
] = "Unknown"


print("\n" + "=" * 70)
print("1. REVIEW_THEME DAĞILIMI")
print("=" * 70)

theme_distribution = (
    df["Review_Theme"]
    .value_counts()
    .rename_axis("Review_Theme")
    .reset_index(name="yorum_sayisi")
)

theme_distribution["yuzde"] = (
    theme_distribution["yorum_sayisi"]
    / len(df)
    * 100
).round(2)

print(
    theme_distribution.to_string(index=False)
)


print("\n" + "=" * 70)
print("2. REVIEW_THEME × MODEL_SENTIMENT")
print("=" * 70)

theme_sentiment_count = pd.crosstab(
    df["Review_Theme"],
    df["model_sentiment"]
)

for sentiment in [
    "positive",
    "neutral",
    "negative"
]:

    if sentiment not in theme_sentiment_count.columns:
        theme_sentiment_count[sentiment] = 0

theme_sentiment_count = (
    theme_sentiment_count[
        [
            "positive",
            "neutral",
            "negative"
        ]
    ]
)

print(
    theme_sentiment_count.to_string()
)


print("\n" + "=" * 70)
print("3. TEMA BAZINDA SENTIMENT YÜZDELERİ")
print("=" * 70)

theme_sentiment_percentage = (
    pd.crosstab(
        df["Review_Theme"],
        df["model_sentiment"],
        normalize="index"
    )
    .mul(100)
    .round(2)
)

for sentiment in [
    "positive",
    "neutral",
    "negative"
]:

    if sentiment not in theme_sentiment_percentage.columns:
        theme_sentiment_percentage[sentiment] = 0

theme_sentiment_percentage = (
    theme_sentiment_percentage[
        [
            "positive",
            "neutral",
            "negative"
        ]
    ]
)

print(
    theme_sentiment_percentage.to_string()
)


print("\n" + "=" * 70)
print("4. TEMA ÖZET TABLOSU")
print("=" * 70)

theme_summary = theme_distribution.copy()

theme_summary = theme_summary.merge(
    theme_sentiment_percentage.reset_index(),
    on="Review_Theme",
    how="left"
)

theme_summary.columns = [
    "tema",
    "yorum_sayisi",
    "genel_yuzde",
    "pozitif_yuzde",
    "notr_yuzde",
    "negatif_yuzde"
]

print(
    theme_summary.to_string(index=False)
)


print("\n" + "=" * 70)
print("5. NEGATİF ORANI EN YÜKSEK TEMALAR")
print("=" * 70)

most_negative = (
    theme_summary
    .sort_values(
        by="negatif_yuzde",
        ascending=False
    )
)

print(
    most_negative[
        [
            "tema",
            "yorum_sayisi",
            "negatif_yuzde",
            "pozitif_yuzde",
            "notr_yuzde"
        ]
    ].to_string(index=False)
)


print("\n" + "=" * 70)
print("6. POZİTİF ORANI EN YÜKSEK TEMALAR")
print("=" * 70)

most_positive = (
    theme_summary
    .sort_values(
        by="pozitif_yuzde",
        ascending=False
    )
)

print(
    most_positive[
        [
            "tema",
            "yorum_sayisi",
            "pozitif_yuzde",
            "negatif_yuzde",
            "notr_yuzde"
        ]
    ].to_string(index=False)
)


theme_file = os.path.join(
    PROCESSED_DIR,
    "ai_theme_distribution.csv"
)

sentiment_file = os.path.join(
    PROCESSED_DIR,
    "ai_theme_sentiment.csv"
)

summary_file = os.path.join(
    PROCESSED_DIR,
    "ai_theme_summary.csv"
)

theme_distribution.to_csv(
    theme_file,
    index=False,
    encoding="utf-8-sig"
)

theme_sentiment_percentage.to_csv(
    sentiment_file,
    encoding="utf-8-sig"
)

theme_summary.to_csv(
    summary_file,
    index=False,
    encoding="utf-8-sig"
)

print("\n" + "=" * 70)
print("DOSYALAR KAYDEDİLDİ")
print("=" * 70)

print(theme_file)
print(sentiment_file)
print(summary_file)

print("\n" + "=" * 70)
print("TEMA × SENTIMENT ANALİZİ TAMAMLANDI")
print("=" * 70)