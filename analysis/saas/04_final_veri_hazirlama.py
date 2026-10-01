import pandas as pd

df = pd.read_json(
    "../data/processed/saas_cleaned.jsonl",
    lines=True
)

df["review_id"] = range(1, len(df) + 1)

df["review_text"] = (
    df["title"].str.strip()
    + ". "
    + df["text"].str.strip()
)

df_final = df[
    [
        "review_id",
        "asin",
        "review_text",
        "rating",
        "timestamp",
        "helpful_vote",
        "verified_purchase"
    ]
].copy()

df_final = df_final.rename(columns={
    "asin": "product_id",
    "timestamp": "review_date",
    "helpful_vote": "helpful_count"
})

df_final["dataset_id"] = 1
df_final["source"] = "Amazon Reviews 2023"
df_final["language"] = "English"
df_final["product_area"] = "Software"

df_final.to_json(
    "../data/processed/saas_final.jsonl",
    orient="records",
    lines=True,
    force_ascii=False
)

print("Final veri seti oluşturuldu.")
print("Kayıt sayısı:", len(df_final))
print("\nKolonlar:")
print(df_final.columns.tolist())
print("\nİlk kayıt:")
print(df_final.iloc[0])