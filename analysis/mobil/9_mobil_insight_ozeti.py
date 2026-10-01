import pandas as pd

print("=" * 70)
print("INSIGHTFLOW - MOBİL İÇGÖRÜ ÖZETİ")
print("=" * 70)

print("\nTema verisi okunuyor...")

df = pd.read_csv("../data/processed/mobil_tema.csv")

print("Toplam yorum sayısı:", len(df))

print("\nTema sonuçları hazırlanıyor...")

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

    count = df[column].sum()
    percentage = (count / len(df)) * 100

    print(
        f"{theme_name}: "
        f"{count} yorum "
        f"(%{percentage:.2f})"
    )


    print("\n" + "=" * 70)
    print("TEMA BAZLI NEGATİF İÇGÖRÜLER")
    print("=" * 70)

for theme_name, column in themes.items():

    theme_df = df[df[column] == True]

    total = len(theme_df)

    one_star_count = (theme_df["review_score"] == 1).sum()
    negative_count = (theme_df["sentiment"] == "negative").sum()

    one_star_percentage = (one_star_count / total) * 100
    negative_percentage = (negative_count / total) * 100

    print("\n" + "-" * 70)
    print(theme_name)
    print("-" * 70)

    print(f"Toplam yorum: {total}")
    print(f"1 yıldız oranı: %{one_star_percentage:.2f}")
    print(f"Negative sentiment oranı: %{negative_percentage:.2f}")




    print("\n" + "=" * 70)
    print("İÇGÖRÜLER KAYDEDİLİYOR")
    print("=" * 70)

insight_rows = []

for theme_name, column in themes.items():

    theme_df = df[df[column] == True]

    total = len(theme_df)

    one_star_count = (theme_df["review_score"] == 1).sum()
    negative_count = (theme_df["sentiment"] == "negative").sum()

    one_star_percentage = (one_star_count / total) * 100
    negative_percentage = (negative_count / total) * 100

    insight_rows.append({
        "theme": theme_name,
        "comment_count": total,
        "comment_percentage": round((total / len(df)) * 100, 2),
        "one_star_percentage": round(one_star_percentage, 2),
        "negative_percentage": round(negative_percentage, 2)
    })

insight_df = pd.DataFrame(insight_rows)

output_path = "../data/processed/mobil_insights.csv"

insight_df.to_csv(
    output_path,
    index=False,
    encoding="utf-8-sig"
)

print("\nİçgörü dosyası kaydedildi:")
print(output_path)

print("\nToplam tema:", len(insight_df))