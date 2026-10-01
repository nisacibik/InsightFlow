import pandas as pd

print("=" * 70)
print("INSIGHTFLOW - MOBİL VERİ KALİTE KONTROLÜ")
print("=" * 70)
print("\nVeri okunuyor...")

df = pd.read_csv("../data/raw/mobil_45000.csv")

print("Veri başarıyla okundu.")
print("Toplam kayıt:", len(df))

print("\nKolonlar:")
print(df.columns.tolist())

print("\nEksik değer kontrolü:")
print(df.isnull().sum())

print("\nDuplicate kontrolü:")

duplicate_count = df.duplicated().sum()

print("Tamamen duplicate kayıt sayısı:", duplicate_count)

print("\nRating dağılımı:")

print(df["review_score"].value_counts().sort_index())


print("\nTarih bilgileri:")

df["review_date"] = pd.to_datetime(df["review_date"], errors="coerce")

print("En eski yorum:", df["review_date"].min())
print("En yeni yorum:", df["review_date"].max())

print("Geçersiz tarih sayısı:", df["review_date"].isnull().sum())

print("\nYorum uzunluğu analizi:")

df["review_length"] = df["review_text"].astype(str).str.len()

print("Minimum:", df["review_length"].min())
print("Ortalama:", round(df["review_length"].mean(), 2))
print("Medyan:", df["review_length"].median())
print("Maksimum:", df["review_length"].max())


print("\nÇok kısa yorum kontrolü:")

short_reviews = (df["review_length"] < 10).sum()

print("10 karakterden kısa yorum:", short_reviews)


print("\nHelpful count analizi:")

print("Minimum:", df["helpful_count"].min())
print("Ortalama:", round(df["helpful_count"].mean(), 2))
print("Medyan:", df["helpful_count"].median())
print("Maksimum:", df["helpful_count"].max())

print("\n" + "=" * 70)
print("VERİ KALİTE KONTROLÜ TAMAMLANDI")
print("=" * 70)