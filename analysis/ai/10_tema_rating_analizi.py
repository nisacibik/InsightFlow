import os
import pandas as pd

print("=" * 70)
print("INSIGHTFLOW - AI TEMA × RATING ANALİZİ")
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
    "Star_Rating"
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

print("\nVeri kontrolü yapılıyor...")

df["Review_Theme"] = (
    df["Review_Theme"]
    .fillna("Unknown")
    .astype(str)
    .str.strip()
)

df.loc[
    df["Review_Theme"] == "",
    "Review_Theme"
] = "Unknown"

df["Star_Rating"] = pd.to_numeric(
    df["Star_Rating"],
    errors="coerce"
)

missing_rating = df["Star_Rating"].isna().sum()

print(
    f"Eksik rating sayısı: {missing_rating:,}"
)

invalid_rating = (
    ~df["Star_Rating"].isin([1, 2, 3, 4, 5])
    & df["Star_Rating"].notna()
).sum()

print(
    f"Geçersiz rating sayısı: {invalid_rating:,}"
)

if missing_rating > 0 or invalid_rating > 0:
    print(
        "\nUyarı: Geçersiz veya eksik rating değerleri var."
    )


print("\n" + "=" * 70)
print("1. GENEL STAR RATING DAĞILIMI")
print("=" * 70)

rating_distribution = (
    df["Star_Rating"]
    .value_counts()
    .sort_index()
    .rename_axis("Star_Rating")
    .reset_index(name="yorum_sayisi")
)

rating_distribution["yuzde"] = (
    rating_distribution["yorum_sayisi"]
    / len(df)
    * 100
).round(2)

print(
    rating_distribution.to_string(index=False)
)


print("\n" + "=" * 70)
print("2. REVIEW_THEME × STAR_RATING")
print("=" * 70)

theme_rating_count = pd.crosstab(
    df["Review_Theme"],
    df["Star_Rating"]
)

for rating in [1, 2, 3, 4, 5]:

    if rating not in theme_rating_count.columns:
        theme_rating_count[rating] = 0

theme_rating_count = theme_rating_count[
    [1, 2, 3, 4, 5]
]

print(
    theme_rating_count.to_string()
)


print("\n" + "=" * 70)
print("3. TEMA BAZINDA RATING YÜZDELERİ")
print("=" * 70)

theme_rating_percentage = (
    pd.crosstab(
        df["Review_Theme"],
        df["Star_Rating"],
        normalize="index"
    )
    .mul(100)
    .round(2)
)

for rating in [1, 2, 3, 4, 5]:

    if rating not in theme_rating_percentage.columns:
        theme_rating_percentage[rating] = 0

theme_rating_percentage = (
    theme_rating_percentage[
        [1, 2, 3, 4, 5]
    ]
)

print(
    theme_rating_percentage.to_string()
)


print("\n" + "=" * 70)
print("4. TEMA BAZINDA ORTALAMA RATING")
print("=" * 70)

theme_average_rating = (
    df.groupby("Review_Theme")["Star_Rating"]
    .mean()
    .round(2)
    .reset_index()
)

theme_average_rating.columns = [
    "Review_Theme",
    "ortalama_rating"
]

print(
    theme_average_rating.to_string(index=False)
)


print("\n" + "=" * 70)
print("5. TEMA RATING ÖZET TABLOSU")
print("=" * 70)

theme_rating_summary = (
    theme_rating_percentage
    .reset_index()
    .merge(
        theme_average_rating,
        on="Review_Theme",
        how="left"
    )
)

theme_rating_summary.columns = [
    "tema",
    "bir_yildiz_yuzde",
    "iki_yildiz_yuzde",
    "uc_yildiz_yuzde",
    "dort_yildiz_yuzde",
    "bes_yildiz_yuzde",
    "ortalama_rating"
]

print(
    theme_rating_summary.to_string(index=False)
)


print("\n" + "=" * 70)
print("6. TEMA BAZINDA DÜŞÜK RATING ORANI")
print("=" * 70)

theme_rating_summary["dusuk_rating_yuzde"] = (
    theme_rating_summary["bir_yildiz_yuzde"]
    + theme_rating_summary["iki_yildiz_yuzde"]
)

print(
    theme_rating_summary[
        [
            "tema",
            "bir_yildiz_yuzde",
            "iki_yildiz_yuzde",
            "dusuk_rating_yuzde",
            "ortalama_rating"
        ]
    ]
    .sort_values(
        by="dusuk_rating_yuzde",
        ascending=False
    )
    .to_string(index=False)
)


print("\n" + "=" * 70)
print("7. TEMA BAZINDA YÜKSEK RATING ORANI")
print("=" * 70)

theme_rating_summary["yuksek_rating_yuzde"] = (
    theme_rating_summary["dort_yildiz_yuzde"]
    + theme_rating_summary["bes_yildiz_yuzde"]
)

print(
    theme_rating_summary[
        [
            "tema",
            "dort_yildiz_yuzde",
            "bes_yildiz_yuzde",
            "yuksek_rating_yuzde",
            "ortalama_rating"
        ]
    ]
    .sort_values(
        by="yuksek_rating_yuzde",
        ascending=False
    )
    .to_string(index=False)
)


rating_distribution_file = os.path.join(
    PROCESSED_DIR,
    "ai_rating_distribution.csv"
)

theme_rating_count_file = os.path.join(
    PROCESSED_DIR,
    "ai_theme_rating_count.csv"
)

theme_rating_percentage_file = os.path.join(
    PROCESSED_DIR,
    "ai_theme_rating_percentage.csv"
)

theme_rating_summary_file = os.path.join(
    PROCESSED_DIR,
    "ai_theme_rating_summary.csv"
)

rating_distribution.to_csv(
    rating_distribution_file,
    index=False,
    encoding="utf-8-sig"
)

theme_rating_count.to_csv(
    theme_rating_count_file,
    encoding="utf-8-sig"
)

theme_rating_percentage.to_csv(
    theme_rating_percentage_file,
    encoding="utf-8-sig"
)

theme_rating_summary.to_csv(
    theme_rating_summary_file,
    index=False,
    encoding="utf-8-sig"
)


print("\n" + "=" * 70)
print("DOSYALAR KAYDEDİLDİ")
print("=" * 70)

print(rating_distribution_file)
print(theme_rating_count_file)
print(theme_rating_percentage_file)
print(theme_rating_summary_file)

print("\n" + "=" * 70)
print("TEMA × RATING ANALİZİ TAMAMLANDI")
print("=" * 70)