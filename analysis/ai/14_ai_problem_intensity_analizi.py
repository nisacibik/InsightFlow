import os
import pandas as pd


print("=" * 70)
print("INSIGHTFLOW - AI PROBLEM YOĞUNLUĞU ANALİZİ")
print("=" * 70)

BASE_DIR = r"C:\Users\asinc\OneDrive\Masaüstü\InsightFlow"

INPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "ai_sentiment_50000.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "ai_problem_intensity.csv"
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


df["low_rating"] = df["Star_Rating"].isin([1, 2])

df["negative_sentiment"] = (
    df["model_sentiment"] == "negative"
)

df["problem_signal"] = (
    df["low_rating"]
    & df["negative_sentiment"]
)


summary = (
    df.groupby("Review_Theme")
    .agg(
        toplam_yorum=("Review_Theme", "size"),

        negatif_yorum=(
            "negative_sentiment",
            "sum"
        ),

        dusuk_rating=(
            "low_rating",
            "sum"
        ),

        negatif_1_2_yildiz=(
            "problem_signal",
            "sum"
        ),

        ortalama_rating=(
            "Star_Rating",
            "mean"
        )
    )
    .reset_index()
)


summary["negatif_orani"] = (
    summary["negatif_yorum"]
    / summary["toplam_yorum"]
    * 100
)

summary["dusuk_rating_orani"] = (
    summary["dusuk_rating"]
    / summary["toplam_yorum"]
    * 100
)


summary["problem_yogunlugu"] = (
    summary["negatif_1_2_yildiz"]
    / summary["toplam_yorum"]
    * 100
)


summary["ortalama_rating"] = (
    summary["ortalama_rating"]
    .round(2)
)

summary["negatif_orani"] = (
    summary["negatif_orani"]
    .round(2)
)

summary["dusuk_rating_orani"] = (
    summary["dusuk_rating_orani"]
    .round(2)
)

summary["problem_yogunlugu"] = (
    summary["problem_yogunlugu"]
    .round(2)
)


summary = summary[
    [
        "Review_Theme",
        "toplam_yorum",
        "negatif_yorum",
        "dusuk_rating",
        "negatif_1_2_yildiz",
        "problem_yogunlugu",
        "negatif_orani",
        "dusuk_rating_orani",
        "ortalama_rating"
    ]
]

# Problem yoğunluğuna göre sırala
summary = summary.sort_values(
    "problem_yogunlugu",
    ascending=False
)


print("\n" + "=" * 70)
print("TEMA BAZLI PROBLEM YOĞUNLUĞU")
print("=" * 70)

print(
    summary.to_string(index=False)
)


summary.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("\n" + "=" * 70)
print("SONUÇ DOSYASI KAYDEDİLDİ")
print("=" * 70)

print(OUTPUT_FILE)


print("\n" + "=" * 70)
print("GENEL KONTROL")
print("=" * 70)

print(
    f"Toplam yorum        : "
    f"{summary['toplam_yorum'].sum():,}"
)

print(
    f"Negatif yorum       : "
    f"{summary['negatif_yorum'].sum():,}"
)

print(
    f"1-2 yıldız          : "
    f"{summary['dusuk_rating'].sum():,}"
)

print(
    f"Negatif + 1-2 yıldız: "
    f"{summary['negatif_1_2_yildiz'].sum():,}"
)

print("\nAnaliz tamamlandı.")