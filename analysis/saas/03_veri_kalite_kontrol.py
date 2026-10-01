import pandas as pd

dosya_yolu = "../data/raw/saas_50000.jsonl"

df = pd.read_json(
    dosya_yolu,
    lines=True
)

print("Veri boyutu:")
print(df.shape)

print("\nKolonlar:")
print(df.columns.tolist())

print("\nVeri tipleri:")
print(df.dtypes)

print("\nEksik değer sayıları:")
print(df.isnull().sum())


print("\nTekrarlanan yorum sayısı:")
print(df["text"].duplicated().sum())


print("\nTekrarlanan yorum örnekleri:")
print(
    df[df["text"].duplicated(keep=False)]
    [["text", "rating", "user_id"]]
    .sort_values("text")
    .head(10)
)


print("\nGerçek duplicate kayıt sayısı:")

gercek_duplicate = df.duplicated(
    subset=["user_id", "text", "rating", "asin"]
).sum()

print(gercek_duplicate)


print("\nPuan dağılımı:")
print(df["rating"].value_counts().sort_index())
print("\nTarih aralığı:")
print("En eski yorum:", df["timestamp"].min())
print("En yeni yorum:", df["timestamp"].max())

print("\nEn kısa yorumlar:")
print(
    df[["text", "rating"]]
    .assign(uzunluk=df["text"].str.len())
    .sort_values("uzunluk")
    .head(20)
)

print("\nÇok kısa yorum sayısı:")

kisa_yorum = df["text"].str.strip().str.len() <= 1

print(kisa_yorum.sum())


kisa_yorum = df["text"].str.strip().str.len() <= 1

df_clean = df[~kisa_yorum].copy()

print("\nTemizleme sonrası kayıt sayısı:")
print(len(df_clean))

cikti_yolu = "../data/processed/saas_cleaned.jsonl"

df_clean.to_json(
    cikti_yolu,
    orient="records",
    lines=True,
    force_ascii=False
)

print(f"Temizlenmiş veri kaydedildi: {cikti_yolu}")
df_clean = df_clean.drop_duplicates(
    subset=["user_id", "text", "rating", "asin"]
)

print("\nDuplicate temizleme sonrası kayıt sayısı:")
print(len(df_clean))
print("\nÖrnek yorumlar:")
print(df_clean["text"].sample(20, random_state=42).to_string(index=False))

import re

def temizle_metin(metin):
    metin = str(metin)

    metin = re.sub(r"<[^>]+>", " ", metin)

    metin = re.sub(r"\s+", " ", metin)

    metin = metin.strip()

    return metin


df_clean["text"] = df_clean["text"].apply(temizle_metin)

print("\nTemizlenmiş örnek yorum:")
print(df_clean["text"].sample(10, random_state=42).to_string(index=False))


df_clean.to_json(
    "../data/processed/saas_cleaned.jsonl",
    orient="records",
    lines=True,
    force_ascii=False
)

print("\nGüncel temizlenmiş veri kaydedildi.")
print("Kayıt sayısı:", len(df_clean))

print("\nURL içeren yorum sayısı:")

url_sayisi = df_clean["text"].str.contains(
    r"https?://|www\.",
    case=False,
    regex=True,
    na=False
).sum()

print(url_sayisi)

print("\nURL içeren yorumlar:")

url_maskesi = df_clean["text"].str.contains(
    r"https?://|www\.",
    case=False,
    regex=True,
    na=False
)

print(df_clean.loc[url_maskesi, "text"].to_string(index=False))
print("\nYorum uzunluk istatistikleri:")
print(df_clean["text"].str.len().describe())

df_clean["review_text"] = (
    df_clean["title"].str.strip()
    + ". "
    + df_clean["text"].str.strip()
)

print("\nOluşturulan review_text örnekleri:")
print(df_clean[["title", "text", "review_text"]].head(5).to_string(index=False))