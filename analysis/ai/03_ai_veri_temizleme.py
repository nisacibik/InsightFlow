import os
import pandas as pd

print("=" * 70)
print("INSIGHTFLOW - AI VERİ TEMİZLEME")
print("=" * 70)

input_path = (
    "../data/raw/"
    "The__Generative_AI_Ecosystem_50k_User_Reviews_2026.csv"
)

output_dir = "../data/processed/ai"

output_path = (
    f"{output_dir}/ai_final.csv"
)


if not os.path.exists(input_path):

    raise FileNotFoundError(
        f"Dataset bulunamadı:\n{input_path}"
    )

os.makedirs(
    output_dir,
    exist_ok=True
)

print("\nDataset okunuyor...")

df = pd.read_csv(
    input_path
)

print(
    f"İlk kayıt sayısı: {len(df):,}"
)


required_columns = [
    "App",
    "Review_Date",
    "Star_Rating",
    "Review_Text",
    "Thumbs_Up_Count"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    raise ValueError(
        "Eksik kolonlar: "
        + ", ".join(missing_columns)
    )

df = df[
    [
        "App",
        "Review_Date",
        "Star_Rating",
        "Review_Text",
        "Thumbs_Up_Count"
    ]
].copy()


df["Review_Text"] = (
    df["Review_Text"]
    .astype(str)
    .str.strip()
)

before = len(df)

df = df[
    df["Review_Text"].notna()
    & (df["Review_Text"] != "")
].copy()

removed_empty = before - len(df)

print(
    f"Boş yorum nedeniyle çıkarılan: "
    f"{removed_empty:,}"
)


before = len(df)

df = df[
    df["Star_Rating"].between(1, 5)
].copy()

removed_rating = before - len(df)

print(
    f"Geçersiz rating nedeniyle çıkarılan: "
    f"{removed_rating:,}"
)

df["Review_Date"] = pd.to_datetime(
    df["Review_Date"],
    errors="coerce"
)


invalid_dates = df["Review_Date"].isna().sum()

print(
    f"Geçersiz tarih: {invalid_dates:,}"
)


df = df[
    df["Review_Date"].notna()
].copy()

valid_apps = [
    "ChatGPT",
    "Microsoft_Copilot",
    "Google_Gemini",
    "Perplexity",
    "Claude"
]

before = len(df)

df = df[
    df["App"].isin(valid_apps)
].copy()

removed_apps = before - len(df)

print(
    f"Geçersiz uygulama nedeniyle çıkarılan: "
    f"{removed_apps:,}"
)


duplicate_count = df.duplicated().sum()

print(
    f"Tam duplicate kayıt: "
    f"{duplicate_count:,}"
)

if duplicate_count > 0:

    df = df.drop_duplicates().copy()


df.insert( 
    0, 
    "review_id", 
    range( 
        100001, 
        100001 + len(df) 
    ) 
)

df["product_id"] = (
    df["App"]
    .str.lower()
    .str.replace("_", "-", regex=False)
    .str.replace(" ", "-", regex=False)
)

df["dataset_id"] = 2

df["source"] = "Generative AI Reviews 50K"

df["language"] = "English"

df["product_area"] = "AI"


df = df[
    [
        "review_id",
        "product_id",
        "Review_Text",
        "Star_Rating",
        "Review_Date",
        "Thumbs_Up_Count",
        "dataset_id",
        "source",
        "language",
        "product_area"
    ]
].copy()


df.rename(
    columns={
        "Review_Text": "review_text",
        "Star_Rating": "rating",
        "Review_Date": "review_date",
        "Thumbs_Up_Count": "helpful_count"
    },
    inplace=True
)


df.to_csv(
    output_path,
    index=False,
    encoding="utf-8-sig"
)


print("\n" + "=" * 70)
print("TEMİZLEME SONUCU")
print("=" * 70)

print(
    f"Son kayıt sayısı: "
    f"{len(df):,}"
)

print(
    f"Sütun sayısı: "
    f"{len(df.columns)}"
)

print("\nKolonlar:")

for column in df.columns:

    print(
        f"- {column}"
    )


print("\nEksik değerler:")

print(
    df.isnull().sum()
)


print("\nDuplicate review_id:")

print(
    df["review_id"].duplicated().sum()
)


print("\nUygulama dağılımı:")

print(
    df["product_id"].value_counts()
)


print("\nRating dağılımı:")

print(
    df["rating"].value_counts().sort_index()
)


print("\n" + "=" * 70)
print("AI VERİ TEMİZLEME TAMAMLANDI")
print("=" * 70)

print(
    f"Çıktı dosyası: {output_path}"
)