import os
import time
import unicodedata

import pandas as pd
from dotenv import load_dotenv
from transformers import pipeline

TEST_LIMIT = 1000
BATCH_SIZE = 32

MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

CSV_PATH = (
    "../data/raw/"
    "The__Generative_AI_Ecosystem_50k_User_Reviews_2026.csv"
)

print("=" * 70)
print("INSIGHTFLOW - AI CONFIDENCE ANALİZİ")
print("=" * 70)

start_time = time.time()

print("\nAI veri seti okunuyor...")

df = pd.read_csv(CSV_PATH)

df = df.head(TEST_LIMIT).copy()

print(f"Test edilecek yorum sayısı: {len(df)}")

texts = [
    unicodedata.normalize("NFKC", str(text))
    for text in df["Review_Text"]
]

print("\nSentiment modeli yükleniyor...")
print("CPU üzerinde çalışacak.")

sentiment_model = pipeline(
    "sentiment-analysis",
    model=MODEL_NAME,
    top_k=None,
    device=-1
)

print("Model hazır.")

print("\nSentiment analizi başlıyor...")

results = []

for start in range(0, len(texts), BATCH_SIZE):

    batch = texts[start:start + BATCH_SIZE]

    batch_results = sentiment_model(
        batch,
        batch_size=BATCH_SIZE,
        truncation=True,
        max_length=512
    )

    for result in batch_results:

        best = max(
            result,
            key=lambda x: x["score"]
        )

        raw_label = best["label"]

        if raw_label in ["label_2", "positive"]:
            label = "positive"

        elif raw_label in ["label_1", "neutral"]:
            label = "neutral"

        elif raw_label in ["label_0", "negative"]:
            label = "negative"

        else:
            label = raw_label

        results.append({
            "sentiment": label,
            "confidence": best["score"]
        })

    completed = min(
        start + BATCH_SIZE,
        len(texts)
    )

    print(
        f"İşlenen: {completed}/{len(texts)}"
    )


df["model_sentiment"] = [
    result["sentiment"]
    for result in results
]

df["confidence"] = [
    result["confidence"]
    for result in results
]

print("\n")
print("=" * 70)
print("CONFIDENCE İSTATİSTİKLERİ")
print("=" * 70)

print(
    f"\nOrtalama confidence: "
    f"{df['confidence'].mean():.4f}"
)

print(
    f"Minimum confidence: "
    f"{df['confidence'].min():.4f}"
)

print(
    f"Maksimum confidence: "
    f"{df['confidence'].max():.4f}"
)

print(
    f"Medyan confidence: "
    f"{df['confidence'].median():.4f}"
)

print("\n")
print("=" * 70)
print("CONFIDENCE DAĞILIMI")
print("=" * 70)

bins = [
    0.0,
    0.50,
    0.60,
    0.70,
    0.80,
    0.90,
    1.00
]

labels = [
    "0.00 - 0.50",
    "0.50 - 0.60",
    "0.60 - 0.70",
    "0.70 - 0.80",
    "0.80 - 0.90",
    "0.90 - 1.00"
]

df["confidence_group"] = pd.cut(
    df["confidence"],
    bins=bins,
    labels=labels,
    include_lowest=True
)

distribution = (
    df["confidence_group"]
    .value_counts()
    .sort_index()
)

for group, count in distribution.items():

    percentage = (
        count / len(df)
    ) * 100

    print(
        f"{group}: "
        f"{count} yorum "
        f"(%{percentage:.2f})"
    )

print("\n")
print("=" * 70)
print("SENTIMENT BAZINDA CONFIDENCE")
print("=" * 70)

sentiment_summary = (
    df.groupby("model_sentiment")["confidence"]
    .agg(["count", "mean", "median", "min", "max"])
)

print(
    sentiment_summary.to_string(
        float_format=lambda x: f"{x:.4f}"
    )
)

print("\n")
print("=" * 70)
print("MODELİN EN KARARSIZ OLDUĞU 20 YORUM")
print("=" * 70)

low_confidence = (
    df.sort_values("confidence")
    .head(20)
)

for _, row in low_confidence.iterrows():

    print("\n" + "-" * 70)

    print(
        f"Review ID: {row['review_id']}"
        if "review_id" in row
        else "Review ID: CSV satırı"
    )

    print(
        f"Model sentiment: "
        f"{row['model_sentiment']}"
    )

    print(
        f"Confidence: "
        f"{row['confidence']:.4f}"
    )

    print(
        f"Rating: "
        f"{row['Star_Rating']}"
    )

    print(
        f"Yorum: "
        f"{row['Review_Text']}"
    )

print("\n")
print("=" * 70)
print("MODELİN EN YÜKSEK CONFIDENCE VERDİĞİ 10 YORUM")
print("=" * 70)

high_confidence = (
    df.sort_values(
        "confidence",
        ascending=False
    )
    .head(10)
)

for _, row in high_confidence.iterrows():

    print("\n" + "-" * 70)

    print(
        f"Model sentiment: "
        f"{row['model_sentiment']}"
    )

    print(
        f"Confidence: "
        f"{row['confidence']:.4f}"
    )

    print(
        f"Rating: "
        f"{row['Star_Rating']}"
    )

    print(
        f"Yorum: "
        f"{row['Review_Text']}"
    )


print("\n")
print("=" * 70)
print("SENTIMENT DAĞILIMI")
print("=" * 70)

sentiment_counts = (
    df["model_sentiment"]
    .value_counts()
)

for sentiment, count in sentiment_counts.items():

    percentage = (
        count / len(df)
    ) * 100

    print(
        f"{sentiment}: "
        f"{count} "
        f"(%{percentage:.2f})"
    )


elapsed = time.time() - start_time

print("\n")
print("=" * 70)
print("ANALİZ TAMAMLANDI")
print("=" * 70)

print(
    f"Toplam süre: "
    f"{elapsed / 60:.2f} dakika"
)

print(
    "\nVeritabanına herhangi bir veri yazılmadı."
)