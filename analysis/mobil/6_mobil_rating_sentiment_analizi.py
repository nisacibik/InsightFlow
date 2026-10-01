import pandas as pd

print("=" * 70)
print("INSIGHTFLOW - MOBİL RATING × SENTIMENT ANALİZİ")
print("=" * 70)

print("\nSentiment verisi okunuyor...")

df = pd.read_csv("../data/processed/mobil_sentiment.csv")

print("Toplam yorum sayısı:", len(df))

print("\n" + "-" * 70)
print("RATING × SENTIMENT DAĞILIMI")
print("-" * 70)

rating_sentiment_counts = pd.crosstab(
    df["review_score"],
    df["sentiment"]
)

print("\nYorum sayıları:")
print(rating_sentiment_counts)

print("\n" + "-" * 70)
print("RATING × SENTIMENT ORANLARI")
print("-" * 70)

rating_sentiment_percent = pd.crosstab(
    df["review_score"],
    df["sentiment"],
    normalize="index"
) * 100

rating_sentiment_percent = rating_sentiment_percent.round(2)

print("\nYüzde dağılımı:")
print(rating_sentiment_percent)