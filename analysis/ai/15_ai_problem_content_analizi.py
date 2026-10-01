import os
import re
import pandas as pd
from collections import Counter


print("=" * 70)
print("INSIGHTFLOW - AI PROBLEM İÇERİK ANALİZİ")
print("=" * 70)

BASE_DIR = r"C:\Users\asinc\OneDrive\Masaüstü\InsightFlow"

INPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "ai_sentiment_50000.csv"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "data",
    "processed"
)


print("\nAI sentiment verisi okunuyor...")

if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(
        f"Dosya bulunamadı:\n{INPUT_FILE}"
    )

df = pd.read_csv(INPUT_FILE)

print(f"Toplam yorum: {len(df):,}")


required_columns = [
    "Review_Theme",
    "Star_Rating",
    "Review_Text",
    "model_sentiment"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Eksik kolonlar: {missing_columns}"
    )

print("Gerekli kolonlar bulundu.")


df["Review_Theme"] = (
    df["Review_Theme"]
    .fillna("Unknown")
    .astype(str)
    .str.strip()
)

df["Review_Text"] = (
    df["Review_Text"]
    .fillna("")
    .astype(str)
)

df["Star_Rating"] = pd.to_numeric(
    df["Star_Rating"],
    errors="coerce"
)

df["model_sentiment"] = (
    df["model_sentiment"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.lower()
)


problem_df = df[
    (df["model_sentiment"] == "negative")
    &
    (df["Star_Rating"].isin([1, 2]))
].copy()

print(
    f"\nProblem sinyali taşıyan yorum: "
    f"{len(problem_df):,}"
)


stopwords = {
    "the", "and", "a", "an", "is", "it", "to", "of",
    "in", "for", "on", "this", "that", "was", "with",
    "but", "i", "my", "me", "you", "your", "are",
    "be", "have", "has", "had", "not", "they", "we",
    "he", "she", "them", "its", "as", "at", "or",
    "so", "if", "can", "could", "would", "should",
    "very", "just", "from", "about", "there", "here",
    "when", "what", "which", "who", "how", "all",
    "more", "some", "too", "than", "also", "do",
    "does", "did", "dont", "didnt", "doesnt",
    "cant", "couldnt", "wouldnt", "shouldnt",
    "im", "ive", "id", "ill", "its"
}


def clean_text(text):
    text = text.lower()

    text = re.sub(
        r"http\S+|www\S+",
        " ",
        text
    )

    text = re.sub(
        r"[^a-z\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


def get_words(text):
    text = clean_text(text)

    words = [
        word
        for word in text.split()
        if word not in stopwords
        and len(word) >= 3
    ]

    return words


def get_bigrams(words):
    return [
        f"{words[i]} {words[i + 1]}"
        for i in range(len(words) - 1)
    ]


themes = problem_df["Review_Theme"].unique()

word_results = []
bigram_results = []

print("\nTema bazlı içerik analizi başlıyor...")

for theme in themes:

    theme_df = problem_df[
        problem_df["Review_Theme"] == theme
    ]

    all_words = []
    all_bigrams = []

    for text in theme_df["Review_Text"]:

        words = get_words(text)

        all_words.extend(words)

        bigrams = get_bigrams(words)

        all_bigrams.extend(bigrams)

    word_counter = Counter(all_words)
    bigram_counter = Counter(all_bigrams)

    for word, count in word_counter.most_common(20):

        word_results.append({
            "Review_Theme": theme,
            "type": "word",
            "term": word,
            "count": count
        })

    for bigram, count in bigram_counter.most_common(20):

        bigram_results.append({
            "Review_Theme": theme,
            "type": "bigram",
            "term": bigram,
            "count": count
        })


word_results_df = pd.DataFrame(
    word_results
)

bigram_results_df = pd.DataFrame(
    bigram_results
)


word_output = os.path.join(
    OUTPUT_DIR,
    "ai_problem_keywords.csv"
)

bigram_output = os.path.join(
    OUTPUT_DIR,
    "ai_problem_bigrams.csv"
)

word_results_df.to_csv(
    word_output,
    index=False,
    encoding="utf-8-sig"
)

bigram_results_df.to_csv(
    bigram_output,
    index=False,
    encoding="utf-8-sig"
)


print("\n" + "=" * 70)
print("EN SIK PROBLEM KELİMELERİ")
print("=" * 70)

for theme in themes:

    print(f"\n--- {theme} ---")

    theme_words = word_results_df[
        word_results_df["Review_Theme"] == theme
    ]

    print(
        theme_words[
            ["term", "count"]
        ].to_string(index=False)
    )

print("\n" + "=" * 70)
print("EN SIK PROBLEM İFADELERİ")
print("=" * 70)

for theme in themes:

    print(f"\n--- {theme} ---")

    theme_bigrams = bigram_results_df[
        bigram_results_df["Review_Theme"] == theme
    ]

    print(
        theme_bigrams[
            ["term", "count"]
        ].to_string(index=False)
    )


print("\n" + "=" * 70)
print("GENEL KONTROL")
print("=" * 70)

print(
    f"Toplam yorum              : {len(df):,}"
)

print(
    f"Problem sinyalli yorum    : {len(problem_df):,}"
)

print(
    f"Kelime sonucu             : "
    f"{len(word_results_df):,}"
)

print(
    f"Bigram sonucu             : "
    f"{len(bigram_results_df):,}"
)

print("\nSonuç dosyaları:")

print(word_output)
print(bigram_output)

print("\nAnaliz tamamlandı.")