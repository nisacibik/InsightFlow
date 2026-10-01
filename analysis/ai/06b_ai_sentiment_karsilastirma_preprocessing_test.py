import os
import time
import unicodedata

import pandas as pd
import psycopg2

from dotenv import load_dotenv
from transformers import pipeline

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

TEST_LIMIT = 1000
BATCH_SIZE = 32

MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

DATASET_ID = 2

CSV_PATH = (
    "../data/raw/"
    "The__Generative_AI_Ecosystem_50k_User_Reviews_2026.csv"
)


def polarity_to_label(polarity, threshold):

    if polarity > threshold:
        return "positive"

    elif polarity < -threshold:
        return "negative"

    else:
        return "neutral"


print("=" * 70)
print("INSIGHTFLOW - AI SENTIMENT KARŞILAŞTIRMA TESTİ")
print("=" * 70)

start_time = time.time()

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

try:

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    cursor = conn.cursor()

    print("\nDatabase bağlantısı başarılı.")

except Exception as e:

    print("\nDatabase bağlantı hatası:")
    print(e)

    raise SystemExit


query = """
SELECT
    review_id,
    product_id,
    review_text,
    rating,
    review_date
FROM reviews
WHERE dataset_id = %s
ORDER BY review_id
LIMIT %s;
"""

cursor.execute(
    query,
    (DATASET_ID, TEST_LIMIT)
)

rows = cursor.fetchall()

print(
    f"DB'den alınan yorum sayısı: "
    f"{len(rows):,}"
)


if len(rows) == 0:

    print("AI datasetine ait yorum bulunamadı.")

    cursor.close()
    conn.close()

    raise SystemExit

print("\nCSV okunuyor...")

try:

    df = pd.read_csv(CSV_PATH)

except Exception as e:

    print("\nCSV okuma hatası:")
    print(e)

    cursor.close()
    conn.close()

    raise SystemExit


print(
    f"CSV toplam kayıt sayısı: "
    f"{len(df):,}"
)

df.insert(
    0,
    "review_id",
    range(
        100001,
        100001 + len(df)
    )
)

db_review_ids = [
    row[0]
    for row in rows
]

df = df[
    df["review_id"].isin(db_review_ids)
].copy()


df = (
    df
    .set_index("review_id")
    .loc[db_review_ids]
    .reset_index()
)


print(
    f"CSV'den eşleştirilen yorum sayısı: "
    f"{len(df):,}"
)


if len(df) != len(rows):

    print(
        "\nUYARI: DB ve CSV kayıt sayıları eşleşmiyor!"
    )

    print(
        f"DB  : {len(rows)}"
    )

    print(
        f"CSV : {len(df)}"
    )

    cursor.close()
    conn.close()

    raise SystemExit


print(
    "DB ↔ CSV review_id eşleşmesi başarılı."
)

db_texts = {
    row[0]: row[2]
    for row in rows
}


text_mismatch = 0


for _, row in df.iterrows():

    review_id = row["review_id"]

    csv_text = str(
        row["Review_Text"]
    ).strip()

    db_text = str(
        db_texts[review_id]
    ).strip()

    if csv_text != db_text:

        text_mismatch += 1


print(
    f"Review text uyuşmazlığı: "
    f"{text_mismatch}"
)


if text_mismatch > 0:

    print(
        "UYARI: Bazı yorumlar DB ve CSV arasında farklı!"
    )

    cursor.close()
    conn.close()

    raise SystemExit


print(
    "DB ↔ CSV review_text eşleşmesi başarılı."
)

print("\nSentiment modeli yükleniyor...")


sentiment_model = pipeline(
    "sentiment-analysis",
    model=MODEL_NAME,
    top_k=None,
    device=-1
)


print("Sentiment modeli hazır.")
print("Analiz CPU üzerinde çalışacak.")

texts = [
    unicodedata.normalize(
        "NFKC",
        str(text)
    )
    for text in df["Review_Text"]
]

print("\nModel sentiment analizi başlıyor...")
model_labels = []
model_scores = []

for i in range(
    0,
    len(texts),
    BATCH_SIZE
):

    batch = texts[
        i:i + BATCH_SIZE
    ]

    results = sentiment_model(
        batch,
        batch_size=BATCH_SIZE,
        truncation=True,
        max_length=512
    )

    for result in results:

        best = max(
            result,
            key=lambda x: x["score"]
        )

        raw_label = best["label"].lower()

        if raw_label in [
            "label_2",
            "positive"
        ]:

            label = "positive"

        elif raw_label in [
            "label_1",
            "neutral"
        ]:

            label = "neutral"

        elif raw_label in [
            "label_0",
            "negative"
        ]:

            label = "negative"

        else:

            print(
                f"UYARI: Bilinmeyen sentiment etiketi: "
                f"{raw_label}"
            )

            label = raw_label


        model_labels.append(label)

        model_scores.append(
            best["score"]
        )


    processed = min(
        i + BATCH_SIZE,
        len(texts)
    )

    print(
        f"İşlenen: {processed:,} / "
        f"{len(texts):,} "
        f"({processed / len(texts) * 100:.1f}%)"
    )

print("\n" + "=" * 70)
print("THRESHOLD OPTİMİZASYONU")
print("=" * 70)


thresholds = [
    0.05,
    0.10,
    0.15,
    0.20,
    0.25,
    0.30
]


threshold_results = []

for threshold in thresholds:

    reference_labels = [
        polarity_to_label(
            float(value),
            threshold
        )
        for value in df["Sentiment_Polarity"]
    ]


    accuracy = accuracy_score(
        reference_labels,
        model_labels
    )


    report = classification_report(
        reference_labels,
        model_labels,
        labels=[
            "positive",
            "negative",
            "neutral"
        ],
        output_dict=True,
        zero_division=0
    )


    macro_f1 = report["macro avg"]["f1-score"]

    weighted_f1 = report["weighted avg"]["f1-score"]


    threshold_results.append({
        "threshold": threshold,
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1
    })


    print(
        f"\nThreshold: ±{threshold:.2f}"
    )


    print(
        f"Accuracy    : {accuracy:.4f} "
        f"({accuracy * 100:.2f}%)"
    )


    print(
        f"Macro F1    : {macro_f1:.4f}"
    )


    print(
        f"Weighted F1 : {weighted_f1:.4f}"
    )

best_result = max(
    threshold_results,
    key=lambda x: x["macro_f1"]
)


print("\n" + "=" * 70)
print("THRESHOLD TEST SONUCU")
print("=" * 70)


print(
    f"En iyi threshold : "
    f"±{best_result['threshold']:.2f}"
)


print(
    f"Accuracy         : "
    f"{best_result['accuracy'] * 100:.2f}%"
)


print(
    f"Macro F1         : "
    f"{best_result['macro_f1']:.4f}"
)


print(
    f"Weighted F1      : "
    f"{best_result['weighted_f1']:.4f}"
)

if len(reference_labels) != len(model_labels):

    print(
        "\nUYARI: Referans ve model sonuç "
        "sayıları eşleşmiyor!"
    )

    cursor.close()
    conn.close()

    raise SystemExit

print("\n" + "=" * 70)
print("SENTIMENT KARŞILAŞTIRMA SONUCU")
print("=" * 70)


accuracy = accuracy_score(
    reference_labels,
    model_labels
)


print(
    f"\nToplam yorum       : "
    f"{len(df):,}"
)


print(
    f"Accuracy           : "
    f"{accuracy:.4f}"
)


print(
    f"Accuracy (%)       : "
    f"{accuracy * 100:.2f}%"
)

match_count = sum(
    1
    for ref, model
    in zip(
        reference_labels,
        model_labels
    )
    if ref == model
)


mismatch_count = (
    len(df) - match_count
)


print(
    f"\nUyumlu yorum       : "
    f"{match_count:,}"
)


print(
    f"Uyuşmayan yorum    : "
    f"{mismatch_count:,}"
)


print(
    f"Uyum oranı         : "
    f"{match_count / len(df) * 100:.2f}%"
)


print(
    f"Uyuşmazlık oranı   : "
    f"{mismatch_count / len(df) * 100:.2f}%"
)

print("\n" + "=" * 70)
print("REFERANS SENTIMENT DAĞILIMI")
print("=" * 70)


for label in [
    "positive",
    "negative",
    "neutral"
]:

    count = reference_labels.count(
        label
    )

    percentage = (
        count /
        len(reference_labels)
        * 100
    )


    print(
        f"{label.capitalize():10} : "
        f"{count:4d} "
        f"({percentage:.2f}%)"
    )

print("\n" + "=" * 70)
print("MODEL SENTIMENT DAĞILIMI")
print("=" * 70)


for label in [
    "positive",
    "negative",
    "neutral"
]:

    count = model_labels.count(
        label
    )

    percentage = (
        count /
        len(model_labels)
        * 100
    )


    print(
        f"{label.capitalize():10} : "
        f"{count:4d} "
        f"({percentage:.2f}%)"
    )

print("\n" + "=" * 70)
print("CLASSIFICATION REPORT")
print("=" * 70)


report = classification_report(
    reference_labels,
    model_labels,
    labels=[
        "positive",
        "negative",
        "neutral"
    ],
    zero_division=0
)


print(report)
print("=" * 70)
print("CONFUSION MATRIX")
print("=" * 70)


labels = [
    "positive",
    "negative",
    "neutral"
]


cm = confusion_matrix(
    reference_labels,
    model_labels,
    labels=labels
)


print(
    "\n                         MODEL"
)


print(
    "                 Positive  Negative  Neutral"
)


print(
    f"Reference Positive"
    f"     {cm[0][0]:4d}"
    f"       {cm[0][1]:4d}"
    f"      {cm[0][2]:4d}"
)


print(
    f"Reference Negative"
    f"     {cm[1][0]:4d}"
    f"       {cm[1][1]:4d}"
    f"      {cm[1][2]:4d}"
)


print(
    f"Reference Neutral "
    f"     {cm[2][0]:4d}"
    f"       {cm[2][1]:4d}"
    f"      {cm[2][2]:4d}"
)

print("\n" + "=" * 70)
print("UYUŞMAYAN ÖRNEKLER - İLK 20")
print("=" * 70)


mismatch_index = 0


for i in range(
    len(df)
):

    if reference_labels[i] != model_labels[i]:

        mismatch_index += 1


        if mismatch_index <= 20:

            print("\n" + "-" * 70)


            print(
                f"Uyuşmazlık #{mismatch_index}"
            )


            print(
                f"Review ID          : "
                f"{df.iloc[i]['review_id']}"
            )


            print(
                f"Rating             : "
                f"{df.iloc[i]['Star_Rating']}"
            )


            print(
                f"Reference polarity : "
                f"{df.iloc[i]['Sentiment_Polarity']}"
            )


            print(
                f"Reference label    : "
                f"{reference_labels[i]}"
            )


            print(
                f"Model label        : "
                f"{model_labels[i]}"
            )


            print(
                f"Model confidence   : "
                f"{model_scores[i]:.4f}"
            )


            print("\nYorum:")


            print(
                df.iloc[i]["Review_Text"]
            )


elapsed = time.time() - start_time


print("\n" + "=" * 70)


print(
    f"Toplam analiz süresi: "
    f"{elapsed / 60:.2f} dakika"
)


print(
    "\nDatabase'de değişiklik yapılmadı."
)


print(
    "review_analysis tablosuna kayıt yapılmadı."
)

cursor.close()
conn.close()


print("=" * 70)
print("KARŞILAŞTIRMA TESTİ TAMAMLANDI")
print("=" * 70)