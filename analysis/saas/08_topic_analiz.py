import os
import json
import time
import psycopg2
import torch
from dotenv import load_dotenv
from transformers import pipeline

load_dotenv()

if not os.getenv("DB_PASSWORD"):
    raise ValueError(
        "DB_PASSWORD bulunamadı. "
        ".env dosyanı kontrol et."
    )


print("=" * 70)
print("INSIGHTFLOW - HIZLANDIRILMIŞ TOPIC ANALİZİ")
print("=" * 70)

if torch.cuda.is_available():
    device = 0
    print("\nGPU bulundu. GPU kullanılacak.")
else:
    device = -1
    print("\nGPU bulunamadı. CPU kullanılacak.")

print("NLP modeli yükleniyor...")

model = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli",
    device=device
)

print("Model hazır.")



conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

cursor = conn.cursor()

print("Database bağlantısı başarılı.")

category_map = {

    "Performance":
        "the software is slow, freezes, lags, crashes, takes too long "
        "to load, becomes unresponsive, or performs poorly",

    "Bugs / Errors":
        "a specific software function is broken, produces an error, "
        "fails unexpectedly, or does not work as intended",

    "Login / Account":
        "the user cannot log in, sign in, access the account, use a password, "
        "or has a specific account access problem",

    "Usability / Interface":
        "the product is difficult or confusing to use, navigate, or control, "
        "or has a problem with its interface, layout, or user experience",

    "Features":
        "the user requests or suggests more features, more levels, more games, "
        "more content, additional functionality, or a new capability",

    "Pricing":
        "the user complains about price, cost, payment, purchase, subscription, "
        "refund, expensive products, or poor value for money",

    "Customer Support":
        "the user complains about customer service, technical support, "
        "help desk, or asks the company for help",

    "Security / Privacy":
        "the user reports a security vulnerability, privacy violation, "
        "unauthorized access, password exposure, or personal data problem",

    "Installation / Update":
        "the user cannot install, download, update, launch, start, or run "
        "the software because of an installation, update, startup, "
        "or compatibility problem"
}


candidate_labels = list(category_map.values())

label_to_topic = {
    description: topic
    for topic, description in category_map.items()
}

actionability_labels = [
    "describes a specific problem, complaint, or feature request",
    "is mainly general praise, satisfaction, or opinion"
]

ACTIONABILITY_THRESHOLD = 0.60
TOPIC_THRESHOLD = 0.50
MAX_TOPICS = 2
TEST_LIMIT = 49918
BATCH_SIZE = 8

print("\nYorumlar database'den alınıyor...")

cursor.execute("""
    SELECT
        r.id,
        r.review_id,
        r.review_text,
        r.rating,
        ra.sentiment
    FROM reviews r
    LEFT JOIN review_analysis ra
        ON ra.review_id = r.id
    ORDER BY r.id
    LIMIT %s
""", (TEST_LIMIT,))

reviews = cursor.fetchall()

print(
    f"Analiz edilecek yorum sayısı: "
    f"{len(reviews):,}"
)

if len(reviews) != TEST_LIMIT:

    cursor.close()
    conn.close()

    raise ValueError(
        f"Beklenen {TEST_LIMIT} yorum yerine "
        f"{len(reviews)} yorum bulundu."
    )

print("Yorum sayısı kontrolü başarılı.")

analysis_results = []

topic_counts = {}

other_count = 0
actionable_count = 0
texts = [
    review[2].strip()[:512]
    for review in reviews
]
start_time = time.perf_counter()
print("\nActionability analizi başlıyor...")

actionability_results = []

for start in range(
    0,
    len(texts),
    BATCH_SIZE
):

    batch_texts = texts[
        start:start + BATCH_SIZE
    ]

    batch_results = model(
        batch_texts,
        candidate_labels=actionability_labels,
        multi_label=False,
        hypothesis_template="This review {}.",
        batch_size=BATCH_SIZE
    )

    actionability_results.extend(
        batch_results
    )

    processed = min(
        start + BATCH_SIZE,
        len(texts)
    )

    print(
        f"Actionability: "
        f"{processed:,} / {len(texts):,}",
        end="\r"
    )

print()

is_actionable_list = []
actionability_scores = []

for result in actionability_results:

    actionability_label = result["labels"][0]

    actionability_score = (
        result["scores"][0]
    )

    is_actionable = (
        actionability_label == actionability_labels[0]
        and
        actionability_score >= ACTIONABILITY_THRESHOLD
    )

    is_actionable_list.append(
        is_actionable
    )

    actionability_scores.append(
        float(actionability_score)
    )

actionable_indexes = [
    i
    for i, value in enumerate(is_actionable_list)
    if value
]

actionable_texts = [
    texts[i]
    for i in actionable_indexes
]

actionable_count = len(actionable_texts)

print(
    f"Actionable yorum sayısı: "
    f"{actionable_count:,}"
)

topic_results_by_index = {}

if actionable_texts:

    print("\nTopic analizi başlıyor...")

    for start in range(
        0,
        len(actionable_texts),
        BATCH_SIZE
    ):

        batch_texts = actionable_texts[
            start:start + BATCH_SIZE
        ]

        batch_results = model(
            batch_texts,
            candidate_labels=candidate_labels,
            multi_label=True,
            hypothesis_template=(
                "This review indicates that {}."
            ),
            batch_size=BATCH_SIZE
        )

        for local_index, result in enumerate(
            batch_results
        ):

            original_index = actionable_indexes[
                start + local_index
            ]

            topic_results_by_index[
                original_index
            ] = result

        processed = min(
            start + BATCH_SIZE,
            len(actionable_texts)
        )

        print(
            f"Topic: "
            f"{processed:,} / "
            f"{len(actionable_texts):,}",
            end="\r"
        )

    print()

for index, review in enumerate(reviews):

    (
        db_id,
        review_id,
        review_text,
        rating,
        sentiment
    ) = review

    is_actionable = is_actionable_list[index]

    actionability_score = (
        actionability_scores[index]
    )

    selected_topics = []

    if is_actionable:

        topic_result = topic_results_by_index[index]

        topic_candidates = []

        for label, score in zip(
            topic_result["labels"],
            topic_result["scores"]
        ):

            if score >= TOPIC_THRESHOLD:

                topic_candidates.append(
                    {
                        "topic": label_to_topic[label],
                        "score": round(
                            float(score),
                            4
                        )
                    }
                )


        topic_candidates.sort(
            key=lambda x: x["score"],
            reverse=True
        )


        selected_topics = (
            topic_candidates[:MAX_TOPICS]
        )


        if not selected_topics:

            selected_topics = [
                {
                    "topic": "Other",
                    "score": 0.0
                }
            ]

            other_count += 1

        else:

            for item in selected_topics:

                topic = item["topic"]

                topic_counts[topic] = (
                    topic_counts.get(topic, 0) + 1
                )

    else:

        selected_topics = [
            {
                "topic": "Other",
                "score": round(
                    float(actionability_score),
                    4
                )
            }
        ]

        other_count += 1

    result_item = {

        "db_id": db_id,

        "review_id": review_id,

        "rating": rating,

        "sentiment": sentiment,

        "actionable": is_actionable,

        "actionability_score": round(
            float(actionability_score),
            4
        ),

        "topics": selected_topics
    }

    analysis_results.append(
        result_item
    )

elapsed_time = (
    time.perf_counter() - start_time
)

print(
    f"\nToplam analiz süresi: "
    f"{elapsed_time / 60:.2f} dakika"
)

print("\n" + "=" * 70)
print("TOPIC ANALİZ ÖZETİ")
print("=" * 70)

print(
    f"Toplam yorum: "
    f"{len(reviews):,}"
)

print(
    f"Problem/talep içeren yorum: "
    f"{actionable_count:,}"
)

print(
    f"Other: "
    f"{other_count:,}"
)

print("\nTopic dağılımı:")
print("-" * 40)

for topic, count in sorted(
    topic_counts.items(),
    key=lambda x: x[1],
    reverse=True
):

    print(
        f"{topic:<30} {count:,}"
    )


total_topics = sum(
    len(item["topics"])
    for item in analysis_results
)

average_topics = (
    total_topics / len(analysis_results)
    if analysis_results
    else 0
)

print(
    f"\nToplam topic kaydı: "
    f"{total_topics:,}"
)

print(
    f"Ortalama topic sayısı: "
    f"{average_topics:.2f}"
)

output_path = (
    "data/processed/"
    "topic_results_49918.json"
)

os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(
    output_path,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        analysis_results,
        f,
        ensure_ascii=False,
        indent=4
    )

print("\nJSON kontrolü yapılıyor...")

if not os.path.exists(output_path):

    cursor.close()
    conn.close()

    raise FileNotFoundError(
        "JSON dosyası oluşturulamadı."
    )


if len(analysis_results) != len(reviews):

    cursor.close()
    conn.close()

    raise ValueError(
        "Analiz sonucu sayısı ile "
        "yorum sayısı eşleşmiyor."
    )


print(
    f"JSON kayıt sayısı: "
    f"{len(analysis_results):,}"
)

print("JSON kontrolü başarılı.")

json_db_ids = [
    item["db_id"]
    for item in analysis_results
]

db_ids = [
    row[0]
    for row in reviews
]

if json_db_ids != db_ids:

    cursor.close()
    conn.close()

    raise ValueError(
        "JSON db_id sıralaması "
        "database ile eşleşmiyor."
    )

print("DB ID kontrolü başarılı.")

cursor.close()
conn.close()

print("\n" + "=" * 70)
print("TOPIC ANALİZİ TAMAMLANDI")
print("=" * 70)

print(
    f"Toplam yorum: "
    f"{len(reviews):,}"
)

print(
    f"Toplam topic kaydı: "
    f"{total_topics:,}"
)

print(
    f"Ortalama topic sayısı: "
    f"{average_topics:.2f}"
)

print(
    f"Toplam süre: "
    f"{elapsed_time / 60:.2f} dakika"
)

print(
    f"Sonuç dosyası: "
    f"{output_path}"
)

print("=" * 70)