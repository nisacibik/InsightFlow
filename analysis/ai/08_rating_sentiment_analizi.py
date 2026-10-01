import pandas as pd
import os
import glob
from transformers import pipeline


print("=" * 70)
print("INSIGHTFLOW - RATING × SENTIMENT ANALİZİ")
print("=" * 70)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

print("\nAI dataset aranıyor...")
print(f"Aranan klasör: {RAW_DIR}")


patterns = [
    os.path.join(RAW_DIR, "*ai*.csv"),
    os.path.join(RAW_DIR, "*AI*.csv"),
    os.path.join(RAW_DIR, "*ai*.json"),
    os.path.join(RAW_DIR, "*AI*.json"),
    os.path.join(RAW_DIR, "*ai*.jsonl"),
    os.path.join(RAW_DIR, "*AI*.jsonl"),
]

dataset_files = []

for pattern in patterns:
    dataset_files.extend(glob.glob(pattern))


dataset_files = list(dict.fromkeys(dataset_files))

if not dataset_files:

    print("\nHATA: AI dataset bulunamadı.")
    print("\nKontrol edilen klasör:")
    print(RAW_DIR)

    print("\nMevcut dosyalar:")

    if os.path.exists(RAW_DIR):
        for file in os.listdir(RAW_DIR):
            print(" -", file)

    else:
        print("data/raw klasörü bulunamadı.")

    raise FileNotFoundError("AI dataset bulunamadı.")


print("\nBulunan AI dataset dosyaları:")

for i, file in enumerate(dataset_files, start=1):
    print(f"{i}. {os.path.basename(file)}")


DATA_PATH = dataset_files[0]

print("\nKullanılacak dataset:")
print(DATA_PATH)
print("\nDataset okunuyor...")

extension = os.path.splitext(DATA_PATH)[1].lower()


if extension == ".csv":

    df = pd.read_csv(DATA_PATH)

elif extension == ".json":

    df = pd.read_json(DATA_PATH)

elif extension == ".jsonl":

    df = pd.read_json(DATA_PATH, lines=True)

else:

    raise ValueError(
        f"Desteklenmeyen dosya formatı: {extension}"
    )


print("Dataset başarıyla okundu.")

print(f"Toplam yorum sayısı: {len(df):,}")

print("\nDataset sütunları:")

for column in df.columns:
    print(" -", column)


rating_column = None

possible_rating_columns = [
    "rating",
    "Rating",
    "stars",
    "score",
    "Star_Rating",
]

for column in possible_rating_columns:

    if column in df.columns:
        rating_column = column
        break


if rating_column is None:

    raise ValueError(
        "\nRating sütunu bulunamadı. "
        "Dataset içerisinde rating/stars/score sütunu olmalı."
    )


print(f"\nRating sütunu: {rating_column}")

text_column = None

possible_text_columns = [
    "review_text",
    "text",
    "review",
    "content",
    "body",
    "Review_Text",
]

for column in possible_text_columns:

    if column in df.columns:
        text_column = column
        break


if text_column is None:

    raise ValueError(
        "\nYorum metni sütunu bulunamadı."
    )


print(f"Yorum sütunu: {text_column}")
print("\n" + "=" * 70)
print("SENTIMENT MODELİ")
print("=" * 70)

print("\nSentiment modeli yükleniyor...")
print("CPU üzerinde çalışacak.")


MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

sentiment_model = pipeline(
    "sentiment-analysis",
    model=MODEL_NAME,
    device=-1,
    truncation=True,
    max_length=512
)

print("Sentiment modeli hazır.")

TEST_SIZE = min(1000, len(df))

analysis_df = df.head(TEST_SIZE).copy()

print(f"\nAnaliz edilecek yorum sayısı: {len(analysis_df)}")

analysis_df[text_column] = (
    analysis_df[text_column]
    .fillna("")
    .astype(str)
)


print("\nSentiment analizi başlıyor...")

sentiments = []
confidences = []

for index, text in enumerate(
    analysis_df[text_column],
    start=1
):

    result = sentiment_model(text[:5000])[0]

    label = result["label"]
    confidence = result["score"]

    if label.lower() == "positive":
        sentiment = "positive"

    elif label.lower() == "negative":
        sentiment = "negative"

    elif label.lower() == "neutral":
        sentiment = "neutral"

    else:
        sentiment = label.lower()


    sentiments.append(sentiment)
    confidences.append(confidence)


    if index % 100 == 0 or index == len(analysis_df):

        print(
            f"İşlenen yorum: "
            f"{index}/{len(analysis_df)}"
        )


analysis_df["model_sentiment"] = sentiments
analysis_df["confidence"] = confidences

analysis_df[rating_column] = pd.to_numeric(
    analysis_df[rating_column],
    errors="coerce"
)


analysis_df = analysis_df.dropna(
    subset=[rating_column]
)


analysis_df[rating_column] = (
    analysis_df[rating_column]
    .astype(int)
)

print("\n")
print("=" * 70)
print("SENTIMENT DAĞILIMI")
print("=" * 70)


sentiment_counts = (
    analysis_df["model_sentiment"]
    .value_counts()
)


total = len(analysis_df)


for sentiment, count in sentiment_counts.items():

    percentage = (count / total) * 100

    print(
        f"{sentiment:<10}: "
        f"{count:>4} "
        f"(%{percentage:.2f})"
    )

print("\n")
print("=" * 70)
print("RATING DAĞILIMI")
print("=" * 70)


rating_counts = (
    analysis_df[rating_column]
    .value_counts()
    .sort_index()
)


for rating, count in rating_counts.items():

    percentage = (count / total) * 100

    print(
        f"{rating} yıldız: "
        f"{count:>4} "
        f"(%{percentage:.2f})"
    )

print("\n")
print("=" * 70)
print("RATING × SENTIMENT ÇAPRAZ ANALİZİ")
print("=" * 70)


cross_table = pd.crosstab(
    analysis_df[rating_column],
    analysis_df["model_sentiment"]
)

for sentiment in [
    "positive",
    "neutral",
    "negative"
]:

    if sentiment not in cross_table.columns:

        cross_table[sentiment] = 0


cross_table = cross_table[
    [
        "positive",
        "neutral",
        "negative"
    ]
]


print("\n")
print(cross_table)
print("\n")
print("=" * 70)
print("RATING BAZINDA SENTIMENT YÜZDELERİ")
print("=" * 70)


cross_percentage = pd.crosstab(
    analysis_df[rating_column],
    analysis_df["model_sentiment"],
    normalize="index"
) * 100


for sentiment in [
    "positive",
    "neutral",
    "negative"
]:

    if sentiment not in cross_percentage.columns:

        cross_percentage[sentiment] = 0


cross_percentage = cross_percentage[
    [
        "positive",
        "neutral",
        "negative"
    ]
]


print("\n")


for rating in cross_percentage.index:

    print(f"{rating} YILDIZ")

    print(
        f"  Positive : "
        f"{cross_percentage.loc[rating, 'positive']:.2f}%"
    )

    print(
        f"  Neutral  : "
        f"{cross_percentage.loc[rating, 'neutral']:.2f}%"
    )

    print(
        f"  Negative : "
        f"{cross_percentage.loc[rating, 'negative']:.2f}%"
    )

    print()

print("=" * 70)
print("RATING × SENTIMENT UYUŞMAZLIKLARI")
print("=" * 70)


def expected_sentiment(rating):

    if rating <= 2:
        return "negative"

    elif rating == 3:
        return "neutral"

    else:
        return "positive"


analysis_df["expected_sentiment"] = (
    analysis_df[rating_column]
    .apply(expected_sentiment)
)


analysis_df["sentiment_match"] = (
    analysis_df["model_sentiment"]
    ==
    analysis_df["expected_sentiment"]
)


match_count = analysis_df["sentiment_match"].sum()

mismatch_count = (
    (~analysis_df["sentiment_match"])
    .sum()
)


match_percentage = (
    match_count / len(analysis_df)
) * 100


mismatch_percentage = (
    mismatch_count / len(analysis_df)
) * 100


print(
    f"\nUyuşan yorumlar   : "
    f"{match_count} "
    f"(%{match_percentage:.2f})"
)


print(
    f"Uyuşmayan yorumlar: "
    f"{mismatch_count} "
    f"(%{mismatch_percentage:.2f})"
)

print("\n")
print("=" * 70)
print("ÖNEMLİ RATING × SENTIMENT UYUŞMAZLIKLARI")
print("=" * 70)

case_1 = analysis_df[
    (analysis_df[rating_column] == 1)
    &
    (analysis_df["model_sentiment"] == "positive")
]

case_2 = analysis_df[
    (analysis_df[rating_column] == 5)
    &
    (analysis_df["model_sentiment"] == "negative")
]


case_3 = analysis_df[
    (analysis_df[rating_column] <= 2)
    &
    (analysis_df["model_sentiment"] == "positive")
]


case_4 = analysis_df[
    (analysis_df[rating_column] >= 4)
    &
    (analysis_df["model_sentiment"] == "negative")
]


print(
    f"\n1 yıldız + Positive : "
    f"{len(case_1)} yorum"
)


print(
    f"5 yıldız + Negative : "
    f"{len(case_2)} yorum"
)


print(
    f"1-2 yıldız + Positive: "
    f"{len(case_3)} yorum"
)


print(
    f"4-5 yıldız + Negative: "
    f"{len(case_4)} yorum"
)


print("\n")
print("=" * 70)
print("DÜŞÜK CONFIDENCE UYUŞMAZLIKLARI")
print("=" * 70)


low_confidence = analysis_df[
    (analysis_df["confidence"] < 0.50)
    &
    (~analysis_df["sentiment_match"])
].copy()


print(
    f"\nConfidence < 0.50 ve rating ile "
    f"sentiment uyuşmayan yorum sayısı: "
    f"{len(low_confidence)}"
)



print("\n")
print("=" * 70)
print("EN DİKKAT ÇEKİCİ 20 UYUŞMAZLIK")
print("=" * 70)


mismatches = analysis_df[
    ~analysis_df["sentiment_match"]
].copy()


mismatches = mismatches.sort_values(
    by="confidence"
)


for i, (_, row) in enumerate(
    mismatches.head(20).iterrows(),
    start=1
):

    print("\n" + "-" * 70)

    print(f"#{i}")

    print(
        f"Rating: "
        f"{row[rating_column]}"
    )

    print(
        f"Beklenen sentiment: "
        f"{row['expected_sentiment']}"
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
        f"Yorum: "
        f"{row[text_column]}"
    )

print("\n")
print("=" * 70)
print("RATING BAZINDA CONFIDENCE")
print("=" * 70)


rating_confidence = (
    analysis_df
    .groupby(rating_column)["confidence"]
    .agg(
        count="count",
        mean="mean",
        median="median",
        min="min",
        max="max"
    )
)


print("\n")

print(
    rating_confidence.to_string(
        float_format=lambda x: f"{x:.4f}"
    )
)


print("\n")
print("=" * 70)
print("SENTIMENT BAZINDA CONFIDENCE")
print("=" * 70)


sentiment_confidence = (
    analysis_df
    .groupby("model_sentiment")["confidence"]
    .agg(
        count="count",
        mean="mean",
        median="median",
        min="min",
        max="max"
    )
)


print("\n")

print(
    sentiment_confidence.to_string(
        float_format=lambda x: f"{x:.4f}"
    )
)


print("\n")
print("=" * 70)
print("ANALİZ ÖZETİ")
print("=" * 70)


print(
    f"\nToplam analiz edilen yorum : "
    f"{len(analysis_df)}"
)


print(
    f"Rating-Sentiment uyuşması : "
    f"{match_count} (%{match_percentage:.2f})"
)


print(
    f"Rating-Sentiment uyuşmazlığı: "
    f"{mismatch_count} (%{mismatch_percentage:.2f})"
)


print(
    f"1 yıldız + Positive        : "
    f"{len(case_1)}"
)


print(
    f"5 yıldız + Negative        : "
    f"{len(case_2)}"
)


print(
    f"Düşük confidence + uyuşmazlık: "
    f"{len(low_confidence)}"
)


OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "data",
    "processed"
)


os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


OUTPUT_PATH = os.path.join(
    OUTPUT_DIR,
    "ai_rating_sentiment_test.csv"
)


analysis_df.to_csv(
    OUTPUT_PATH,
    index=False,
    encoding="utf-8-sig"
)


print("\n")
print("=" * 70)
print("TEST SONUCU KAYDEDİLDİ")
print("=" * 70)


print(
    f"\nDosya: {OUTPUT_PATH}"
)


print("\nVeritabanına herhangi bir veri yazılmadı.")

print("\n")
print("=" * 70)
print("ANALİZ TAMAMLANDI")
print("=" * 70)