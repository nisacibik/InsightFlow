import os
import pandas as pd
from transformers import pipeline
from tqdm import tqdm


print("=" * 70)
print("INSIGHTFLOW - AI SENTIMENT FULL ANALİZİ")
print("=" * 70)


BASE_DIR = r"C:\Users\asinc\OneDrive\Masaüstü\InsightFlow"

RAW_DIR = os.path.join(
    BASE_DIR,
    "data",
    "raw"
)

PROCESSED_DIR = os.path.join(
    BASE_DIR,
    "data",
    "processed"
)

os.makedirs(PROCESSED_DIR, exist_ok=True)

INPUT_FILE = os.path.join(
    RAW_DIR,
    "The__Generative_AI_Ecosystem_50k_User_Reviews_2026.csv"
)

OUTPUT_FILE = os.path.join(
    PROCESSED_DIR,
    "ai_sentiment_50000.csv"
)

print("\nAI veri seti okunuyor...")

if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(
        f"AI veri seti bulunamadı:\n{INPUT_FILE}"
    )

df = pd.read_csv(INPUT_FILE)

print(f"Toplam kayıt: {len(df):,}")

required_columns = [
    "Review_Text",
    "Star_Rating",
    "Review_Theme",
    "Review_Date",
    "App",
    "App_Version"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    print("\nEksik kolonlar:")

    for column in missing_columns:
        print(f"- {column}")

    raise ValueError(
        "Gerekli kolonlardan bazıları bulunamadı."
    )

print("\nGerekli kolonlar bulundu.")

df["Review_Text"] = (
    df["Review_Text"]
    .fillna("")
    .astype(str)
    .str.strip()
)

empty_reviews = (
    df["Review_Text"] == ""
).sum()

print(f"Boş yorum sayısı: {empty_reviews:,}")
print("\nSentiment modeli yükleniyor...")

print(
    "Model: "
    "cardiffnlp/twitter-roberta-base-sentiment-latest"
)

print("Çalışma ortamı: CPU")

sentiment_model = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
    device=-1
)

print("Model hazır.")

BATCH_SIZE = 32

texts = df["Review_Text"].tolist()

sentiments = []
confidences = []

total_records = len(texts)

print("\n" + "=" * 70)
print("50.000 YORUM İŞLENİYOR")
print("=" * 70)

print(f"Toplam yorum : {total_records:,}")
print(f"Batch boyutu : {BATCH_SIZE:,}")

for start in tqdm(
    range(0, total_records, BATCH_SIZE),
    desc="Sentiment analizi",
    unit="batch"
):

    batch = texts[
        start:start + BATCH_SIZE
    ]

    results = sentiment_model(
        batch,
        truncation=True,
        max_length=512
    )

    for result in results:

        sentiments.append(
            result["label"].lower()
        )

        confidences.append(
            float(result["score"])
        )

print("\nSentiment sonuçları tabloya ekleniyor...")

df["model_sentiment"] = sentiments

df["confidence"] = confidences

print("\n" + "=" * 70)
print("SONUÇ KONTROLÜ")
print("=" * 70)

print(
    f"Toplam veri            : {len(df):,}"
)

print(
    f"Sentiment sonucu sayısı : "
    f"{len(df['model_sentiment']):,}"
)

print(
    f"Confidence sonucu sayısı: "
    f"{len(df['confidence']):,}"
)

if len(df) != len(sentiments):

    raise ValueError(
        "Sentiment sonuçlarının sayısı "
        "veri sayısıyla eşleşmiyor."
    )

print("\n" + "=" * 70)
print("SENTIMENT DAĞILIMI")
print("=" * 70)

sentiment_counts = (
    df["model_sentiment"]
    .value_counts()
)

sentiment_percentages = (
    df["model_sentiment"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)

for sentiment in [
    "positive",
    "neutral",
    "negative"
]:

    count = sentiment_counts.get(
        sentiment,
        0
    )

    percentage = sentiment_percentages.get(
        sentiment,
        0
    )

    print(
        f"{sentiment:<10} "
        f"{count:>8,} "
        f"({percentage:>6.2f}%)"
    )

print("\n" + "=" * 70)
print("CONFIDENCE İSTATİSTİKLERİ")
print("=" * 70)

print(
    f"Ortalama : "
    f"{df['confidence'].mean():.4f}"
)

print(
    f"Medyan   : "
    f"{df['confidence'].median():.4f}"
)

print(
    f"Minimum  : "
    f"{df['confidence'].min():.4f}"
)

print(
    f"Maksimum : "
    f"{df['confidence'].max():.4f}"
)

print("\n" + "=" * 70)
print("CONFIDENCE DAĞILIMI")
print("=" * 70)

confidence_bins = pd.cut(
    df["confidence"],
    bins=[
        0.0,
        0.50,
        0.60,
        0.70,
        0.80,
        0.90,
        1.00
    ],
    include_lowest=True
)

confidence_distribution = (
    confidence_bins
    .value_counts()
    .sort_index()
)

for interval, count in confidence_distribution.items():

    percentage = (
        count / len(df) * 100
    )

    print(
        f"{str(interval):<20} "
        f"{count:>8,} "
        f"({percentage:>6.2f}%)"
    )

print("\n" + "=" * 70)
print("SONUÇLAR KAYDEDİLİYOR")
print("=" * 70)

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("\nDosya başarıyla kaydedildi:")

print(
    OUTPUT_FILE
)

if os.path.exists(OUTPUT_FILE):

    file_size_mb = (
        os.path.getsize(OUTPUT_FILE)
        / (1024 * 1024)
    )

    print(
        f"\nDosya boyutu: "
        f"{file_size_mb:.2f} MB"
    )

else:

    raise FileNotFoundError(
        "Çıktı dosyası oluşturulamadı."
    )

print("\n" + "=" * 70)
print("50.000 YORUM SENTIMENT ANALİZİ TAMAMLANDI")
print("=" * 70)