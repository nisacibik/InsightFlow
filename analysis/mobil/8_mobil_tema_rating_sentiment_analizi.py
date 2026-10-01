import pandas as pd

print("=" * 70)
print("INSIGHTFLOW - MOBİL TEMA × RATING × SENTIMENT ANALİZİ")
print("=" * 70)

print("\nTema verisi okunuyor...")

df = pd.read_csv("../data/processed/mobil_tema.csv")

print("Toplam yorum sayısı:", len(df))

print("\nGerekli kolonlar kontrol ediliyor...")

required_columns = [
    "review_text",
    "review_score",
    "sentiment",
    "tema_hata",
    "tema_guncelleme",
    "tema_destek",
    "tema_odeme",
    "tema_hesap",
    "tema_arayuz",
    "tema_performans"
]

for column in required_columns:
    if column in df.columns:
        print(f"- {column}: bulundu")
    else:
        print(f"- {column}: BULUNAMADI")



        print("\n" + "-" * 70)
print("HATA / ÇALIŞMAMA TEMASI × RATING")
print("-" * 70)

hata_df = df[df["tema_hata"] == True]

print("\nHata / çalışmama temalı toplam yorum:", len(hata_df))

rating_counts = hata_df["review_score"].value_counts().sort_index()

print("\nRating dağılımı:")

for rating, count in rating_counts.items():
    percentage = (count / len(hata_df)) * 100
    print(
        f"{rating} yıldız: {count} yorum "
        f"(%{percentage:.2f})"
    )





    print("\n" + "-" * 70)
print("HATA / ÇALIŞMAMA TEMASI × SENTIMENT")
print("-" * 70)

sentiment_counts = hata_df["sentiment"].value_counts()

print("\nSentiment dağılımı:")

for sentiment, count in sentiment_counts.items():
    percentage = (count / len(hata_df)) * 100
    print(
        f"{sentiment}: {count} yorum "
        f"(%{percentage:.2f})"
    )




    print("\n" + "=" * 70)
print("TÜM TEMALAR - RATING × SENTIMENT")
print("=" * 70)

themes = {
    "Hata / Çalışmama": "tema_hata",
    "Güncelleme": "tema_guncelleme",
    "Müşteri Hizmetleri / Destek": "tema_destek",
    "Ödeme": "tema_odeme",
    "Hesap / Giriş": "tema_hesap",
    "Kullanım / Arayüz": "tema_arayuz",
    "Performans / Yavaşlık": "tema_performans"
}

for theme_name, column in themes.items():

    theme_df = df[df[column] == True]

    print("\n" + "-" * 70)
    print(theme_name)
    print("-" * 70)

    print("Toplam yorum:", len(theme_df))

    print("\nRating:")
    rating_counts = theme_df["review_score"].value_counts().sort_index()

    for rating, count in rating_counts.items():
        percentage = (count / len(theme_df)) * 100
        print(
            f"{rating} yıldız: {count} "
            f"(%{percentage:.2f})"
        )

    print("\nSentiment:")
    sentiment_counts = theme_df["sentiment"].value_counts()

    for sentiment, count in sentiment_counts.items():
        percentage = (count / len(theme_df)) * 100
        print(
            f"{sentiment}: {count} "
            f"(%{percentage:.2f})"
        )