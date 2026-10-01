import os
import pandas as pd

print("=" * 70)
print("INSIGHTFLOW - AI DATASET DETAYLI KONTROL")
print("=" * 70)

input_path = "../data/raw/The__Generative_AI_Ecosystem_50k_User_Reviews_2026.csv"

if not os.path.exists(input_path):
    raise FileNotFoundError(
        f"Dataset bulunamadı:\n{input_path}"
    )

df = pd.read_csv(input_path)

print(f"\nDataset yüklendi: {len(df):,} kayıt")
print("\n" + "=" * 70)
print("1. RATING KONTROLÜ")
print("=" * 70)

print("Rating değerleri:")
print(df["Star_Rating"].value_counts().sort_index())

invalid_ratings = df[
    ~df["Star_Rating"].between(1, 5)
]

print(
    f"\n1-5 dışında rating sayısı: "
    f"{len(invalid_ratings):,}"
)


print("\n" + "=" * 70)
print("2. REVIEW TEXT KONTROLÜ")
print("=" * 70)

empty_text = df["Review_Text"].isna().sum()

blank_text = (
    df["Review_Text"]
    .astype(str)
    .str.strip()
    .eq("")
    .sum()
)

print(f"Boş / NaN yorum      : {empty_text:,}")
print(f"Boş string yorum     : {blank_text:,}")


actual_char_length = (
    df["Review_Text"]
    .astype(str)
    .str.len()
)

print("\nGerçek yorum uzunluğu:")
print(
    actual_char_length.describe()
)


very_short = df[
    actual_char_length < 5
]

print(
    f"\n5 karakterden kısa yorum: "
    f"{len(very_short):,}"
)


print("\n" + "=" * 70)
print("3. WORD COUNT KONTROLÜ")
print("=" * 70)

actual_word_count = (
    df["Review_Text"]
    .astype(str)
    .str.split()
    .str.len()
)

word_count_difference = (
    df["Word_Count"] - actual_word_count
)

print(
    "Word_Count fark istatistikleri:"
)

print(
    word_count_difference.describe()
)

print(
    f"\nWord_Count ile gerçek kelime sayısı "
    f"farklı olan kayıt: "
    f"{(word_count_difference != 0).sum():,}"
)

print("\n" + "=" * 70)
print("4. REVIEW LENGTH KONTROLÜ")
print("=" * 70)

length_difference = (
    df["Review_Length_Chars"]
    - actual_char_length
)

print(
    f"Karakter uzunluğu farklı olan kayıt: "
    f"{(length_difference != 0).sum():,}"
)

print(
    "\nLength fark istatistikleri:"
)

print(
    length_difference.describe()
)

print("\n" + "=" * 70)
print("5. THUMBS UP KONTROLÜ")
print("=" * 70)

print(
    df["Thumbs_Up_Count"].describe()
)

negative_thumbs = df[
    df["Thumbs_Up_Count"] < 0
]

print(
    f"\nNegatif Thumbs_Up_Count: "
    f"{len(negative_thumbs):,}"
)

print("\n" + "=" * 70)
print("6. SENTIMENT POLARITY KONTROLÜ")
print("=" * 70)

print(
    df["Sentiment_Polarity"].describe()
)

invalid_polarity = df[
    ~df["Sentiment_Polarity"].between(-1, 1)
]

print(
    f"\n-1 ile 1 dışında değer: "
    f"{len(invalid_polarity):,}"
)

print("\n" + "=" * 70)
print("7. REVIEW DATE KONTROLÜ")
print("=" * 70)

parsed_dates = pd.to_datetime(
    df["Review_Date"],
    errors="coerce"
)

invalid_dates = parsed_dates.isna()

print(
    f"Geçersiz tarih: "
    f"{invalid_dates.sum():,}"
)

print(
    f"En eski tarih: "
    f"{parsed_dates.min()}"
)

print(
    f"En yeni tarih: "
    f"{parsed_dates.max()}"
)


print("\n" + "=" * 70)
print("8. UYGULAMA DAĞILIMI")
print("=" * 70)

app_distribution = (
    df["App"]
    .value_counts()
)

print(app_distribution)

print("\n" + "=" * 70)
print("9. UYGULAMA BAZINDA RATING")
print("=" * 70)

app_rating = pd.crosstab(
    df["App"],
    df["Star_Rating"]
)

print(app_rating)
print("\n" + "=" * 70)
print("10. REVIEW THEME DAĞILIMI")
print("=" * 70)

print(
    df["Review_Theme"]
    .value_counts()
)

print("\n" + "=" * 70)
print("11. APP VERSION")
print("=" * 70)

print(
    f"Eksik App_Version: "
    f"{df['App_Version'].isna().sum():,}"
)

print(
    f"Unique App_Version: "
    f"{df['App_Version'].nunique():,}"
)

print("\n" + "=" * 70)
print("12. TEKRAR EDEN REVIEW TEXT")
print("=" * 70)

duplicate_text_count = (
    df["Review_Text"]
    .duplicated(keep=False)
    .sum()
)

duplicate_text_groups = (
    df["Review_Text"]
    .duplicated()
    .sum()
)

print(
    f"Tekrar eden metin içeren kayıt: "
    f"{duplicate_text_count:,}"
)

print(
    f"İlk kayıt hariç tekrar sayısı: "
    f"{duplicate_text_groups:,}"
)

print("\n" + "=" * 70)
print("13. URL KONTROLÜ")
print("=" * 70)

url_count = (
    df["Review_Text"]
    .astype(str)
    .str.contains(
        r"http://|https://|www\.",
        case=False,
        regex=True
    )
    .sum()
)

print(
    f"URL içeren yorum: "
    f"{url_count:,}"
)


print("\n" + "=" * 70)
print("14. ÖZEL KARAKTER KONTROLÜ")
print("=" * 70)

special_character_count = (
    df["Review_Text"]
    .astype(str)
    .str.contains(
        r"[^\x00-\x7F]",
        regex=True
    )
    .sum()
)

print(
    f"ASCII dışı karakter içeren yorum: "
    f"{special_character_count:,}"
)

print("\n" + "=" * 70)
print("DETAYLI KONTROL TAMAMLANDI")
print("=" * 70)

print(
    f"Toplam kayıt: {len(df):,}"
)

print(
    "Bu aşamada dataset üzerinde herhangi "
    "bir değişiklik yapılmadı."
)

print("=" * 70)