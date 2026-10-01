import pandas as pd

print("=" * 70)
print("INSIGHTFLOW - MOBİL UYGULAMALAR EDA")
print("=" * 70)
print("\nTemiz veri okunuyor...")

df = pd.read_csv("../data/processed/mobil_cleaned.csv")

print("Toplam kayıt:", len(df))
print("\n" + "-" * 70)
print("RATING DAĞILIMI")
print("-" * 70)

rating_counts = df["review_score"].value_counts().sort_index()
rating_percentages = df["review_score"].value_counts(
    normalize=True
).sort_index() * 100

rating_table = pd.DataFrame({
    "Yorum Sayısı": rating_counts,
    "Oran (%)": rating_percentages.round(2)
})

print(rating_table)

print("\n" + "-" * 70)
print("TARİH ANALİZİ")
print("-" * 70)

df["review_date"] = pd.to_datetime(df["review_date"])

print("En eski yorum:", df["review_date"].min().date())
print("En yeni yorum:", df["review_date"].max().date())

print("\nYıllara göre yorum sayısı:")

yearly_counts = df["review_date"].dt.year.value_counts().sort_index()

yearly_percentages = (
    df["review_date"].dt.year.value_counts(normalize=True).sort_index() * 100
)

yearly_table = pd.DataFrame({
    "Yorum Sayısı": yearly_counts,
    "Oran (%)": yearly_percentages.round(2)
})

print(yearly_table)
print("\n" + "-" * 70)
print("YORUM UZUNLUĞU ANALİZİ")
print("-" * 70)

df["review_length"] = df["review_text"].astype(str).str.len()

print("Minimum:", df["review_length"].min())
print("Ortalama:", round(df["review_length"].mean(), 2))
print("Medyan:", df["review_length"].median())
print("Maksimum:", df["review_length"].max())

print("\nYorum uzunluğu grupları:")

length_groups = pd.cut(
    df["review_length"],
    bins=[0, 10, 50, 100, 250, 500, float("inf")],
    labels=[
        "1-10",
        "11-50",
        "51-100",
        "101-250",
        "251-500",
        "500+"
    ],
    include_lowest=True
)

length_counts = length_groups.value_counts().sort_index()
length_percentages = (
    length_groups.value_counts(normalize=True).sort_index() * 100
)

length_table = pd.DataFrame({
    "Yorum Sayısı": length_counts,
    "Oran (%)": length_percentages.round(2)
})

print(length_table)
print("\n" + "-" * 70)
print("HELPFUL COUNT ANALİZİ")
print("-" * 70)

print("Minimum:", df["helpful_count"].min())
print("Ortalama:", round(df["helpful_count"].mean(), 2))
print("Medyan:", df["helpful_count"].median())
print("Maksimum:", df["helpful_count"].max())

helpful_zero = (df["helpful_count"] == 0).sum()
helpful_zero_percentage = (helpful_zero / len(df)) * 100

print(
    "Helpful count = 0 olan yorumlar:",
    helpful_zero,
    f"({helpful_zero_percentage:.2f}%)"
)

print("\n" + "-" * 70)
print("GENEL VERİ KONTROLÜ")
print("-" * 70)

print("Toplam yorum:", len(df))
print("Toplam uygulama:", df["app_id"].nunique())
print("Eksik değer:", df.isnull().sum().sum())

print("\n" + "=" * 70)
print("MOBİL EDA TAMAMLANDI")
print("=" * 70)