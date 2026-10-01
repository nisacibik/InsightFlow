import pandas as pd
import torch
from transformers import pipeline

print("=" * 70)
print("INSIGHTFLOW - MOBİL UYGULAMALAR SENTIMENT ANALİZİ")
print("=" * 70)
print("\nTemizlenmiş mobil verisi okunuyor...")

df = pd.read_csv("../data/processed/mobil_cleaned.csv")

print("Toplam yorum sayısı:", len(df))
print("\nSentiment modeli yükleniyor...")
print("Model: cardiffnlp/twitter-roberta-base-sentiment-latest")

device = 0 if torch.cuda.is_available() else -1

if device == 0:
    print("GPU üzerinde çalışacak.")
else:
    print("CPU üzerinde çalışacak.")

sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
    device=device
)


print("\nSentiment analizi başlıyor...")

results = []

texts = df["review_text"].tolist()

for i in range(0, len(texts), 32):

    batch = texts[i:i + 32]

    batch_results = sentiment_pipeline(
        batch,
        truncation=True,
        max_length=512
    )

    results.extend(batch_results)

    if (i + len(batch)) % 1000 == 0 or i + len(batch) == len(texts):
        print(
            f"İşlenen yorum: {i + len(batch):,} / {len(texts):,}"
        )


df["sentiment"] = [
    result["label"].lower()
    for result in results
]

df["sentiment_score"] = [
    result["score"]
    for result in results
]


print("\n" + "-" * 70)
print("SENTIMENT DAĞILIMI")
print("-" * 70)

sentiment_counts = df["sentiment"].value_counts()

sentiment_percentages = (
    df["sentiment"].value_counts(normalize=True) * 100
)

sentiment_table = pd.DataFrame({
    "Yorum Sayısı": sentiment_counts,
    "Oran (%)": sentiment_percentages.round(2)
})

print(sentiment_table)

output_path = "../data/processed/mobil_sentiment.csv"

df.to_csv(
    output_path,
    index=False
)

print("\nSentiment sonuçları kaydedildi:")
print(output_path)

print("\n" + "=" * 70)
print("MOBİL SENTIMENT ANALİZİ TAMAMLANDI")
print("=" * 70)