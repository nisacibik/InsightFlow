import pandas as pd

df = pd.read_json(
    "../data/processed/saas_final.jsonl",
    lines=True
)

print("Kayıt sayısı:", len(df))

print("\nEksik değerler:")
print(df.isnull().sum())

print("\nDuplicate review_id:")
print(df["review_id"].duplicated().sum())

df["text_length"] = df["review_text"].str.len()

print("\nYorum uzunlukları:")
print(df["text_length"].describe())

print("\nURL içeren yorum sayısı:")
print(
    df["review_text"]
    .str.contains(r"http|www\.", case=False, regex=True)
    .sum()
)

print("\nBoş yorum sayısı:")
print(
    (df["review_text"].str.strip() == "").sum()
)

print("\nRating dağılımı:")
print(df["rating"].value_counts().sort_index())