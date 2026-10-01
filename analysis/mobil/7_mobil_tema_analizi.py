import pandas as pd

print("=" * 70)
print("INSIGHTFLOW - MOBİL TEMA ANALİZİ")
print("=" * 70)

print("\nSentiment verisi okunuyor...")

df = pd.read_csv("../data/processed/mobil_sentiment.csv")

print("Toplam yorum sayısı:", len(df))

print("\nGerekli kolonlar kontrol ediliyor...")

required_columns = [
    "review_text",
    "review_score",
    "sentiment"
]

for column in required_columns:
    if column in df.columns:
        print(f"- {column}: bulundu")
    else:
        print(f"- {column}: BULUNAMADI")

print("\nTema analizi için veri hazır.")


print("\n" + "-" * 70)
print("EN SIK GEÇEN KELİMELER")
print("-" * 70)

from collections import Counter
import re

all_text = " ".join(
    df["review_text"]
    .astype(str)
    .str.lower()
)

words = re.findall(r"\b[a-zA-Z]{3,}\b", all_text)

stopwords = {
    "the", "and", "for", "you", "this", "but", "that",
    "have", "not", "can", "with", "when", "was", "they",
    "just", "all", "get", "time", "like", "are", "your",
    "very", "there", "now", "from", "use", "has", "had",
    "been", "its", "what", "how", "too", "one", "out",
    "who", "why", "our", "his", "her", "their", "would",
    "could", "more", "some", "about", "which", "will",
    "also", "than", "then", "only", "really", "into",
    "my", "me", "were", "app"
}

words = [
    word
    for word in words
    if word not in stopwords
]

word_counts = Counter(words)

print("\nEn sık geçen 30 kelime:")

for word, count in word_counts.most_common(30):
    print(f"{word}: {count}")



    print("\n" + "-" * 70)
print("EN SIK GEÇEN KELİME ÇİFTLERİ")
print("-" * 70)

from collections import Counter

bigrams = zip(words, words[1:])

bigram_counts = Counter(bigrams)

print("\nEn sık geçen 30 kelime çifti:")

for pair, count in bigram_counts.most_common(30):
    print(f"{pair[0]} {pair[1]}: {count}")



    print("\n" + "-" * 70)
print("NEGATİF YORUMLARDA EN SIK GEÇEN KELİME ÇİFTLERİ")
print("-" * 70)

negative_text = " ".join(
    df.loc[df["sentiment"] == "negative", "review_text"]
    .astype(str)
    .str.lower()
)

negative_words = re.findall(
    r"\b[a-zA-Z]{3,}\b",
    negative_text
)

negative_words = [
    word
    for word in negative_words
    if word not in stopwords
]

negative_bigrams = zip(
    negative_words,
    negative_words[1:]
)

negative_bigram_counts = Counter(negative_bigrams)

print("\nNegatif yorumlarda en sık geçen 30 kelime çifti:")

for pair, count in negative_bigram_counts.most_common(30):
    print(f"{pair[0]} {pair[1]}: {count}")



    print("\n" + "-" * 70)
print("TEMA ANALİZİ - HATA / ÇALIŞMAMA")
print("-" * 70)

error_keywords = [
    "doesn't work",
    "does not work",
    "not working",
    "won't work",
    "wont work",
    "can't work",
    "cant work",
    "can't open",
    "cant open",
    "can't use",
    "cant use",
    "error message",
    "error code",
    "crash",
    "crashes",
    "crashed",
    "crashing",
    "bug",
    "bugs",
    "app froze",
    "app freezes",
    "app freezing",
    "not responding",
    "keeps crashing",
    "keeps freezing",
    "failed to"
]

df["tema_hata"] = df["review_text"].astype(str).str.lower().apply(
    lambda text: any(keyword in text for keyword in error_keywords)
)

error_count = df["tema_hata"].sum()
error_percentage = (error_count / len(df)) * 100

print("Hata / çalışmama teması bulunan yorum:", error_count)
print("Oran (%):", round(error_percentage, 2))



print("\n" + "-" * 70)
print("TEMA ANALİZİ - GÜNCELLEME")
print("-" * 70)

update_keywords = [
    "new update broke",
    "update broke",
    "update ruined",
    "update problem",
    "update issue",
    "update error",
    "update bug",
    "after update",
    "since update",
    "after the update",
    "since the update",
    "latest update broke",
    "latest update problem",
    "latest update issue",
    "last update broke",
    "last update problem",
    "last update issue"
]

df["tema_guncelleme"] = df["review_text"].astype(str).str.lower().apply(
    lambda text: any(keyword in text for keyword in update_keywords)
)

update_count = df["tema_guncelleme"].sum()
update_percentage = (update_count / len(df)) * 100

print("Güncelleme teması bulunan yorum:", update_count)
print("Oran (%):", round(update_percentage, 2))



print("\n" + "-" * 70)
print("TEMA ANALİZİ - MÜŞTERİ HİZMETLERİ / DESTEK")
print("-" * 70)

support_keywords = [
    "customer service",
    "customer support",
    "support team",
    "technical support",
    "contact support",
    "contact customer service",
    "help desk",
    "support agent",
    "customer care",
    "couldn't get help",
    "could not get help"
]

df["tema_destek"] = df["review_text"].astype(str).str.lower().apply(
    lambda text: any(keyword in text for keyword in support_keywords)
)

support_count = df["tema_destek"].sum()
support_percentage = (support_count / len(df)) * 100

print("Müşteri hizmetleri / destek teması bulunan yorum:", support_count)
print("Oran (%):", round(support_percentage, 2))


print("\n" + "-" * 70)
print("TEMA ANALİZİ - ÖDEME")
print("-" * 70)

payment_keywords = [
    "google pay",
    "credit card",
    "debit card",
    "payment failed",
    "payment error",
    "failed payment",
    "card declined",
    "credit card declined",
    "charged twice",
    "wrong charge",
    "refund",
    "billing problem",
    "billing issue"
]

df["tema_odeme"] = df["review_text"].astype(str).str.lower().apply(
    lambda text: any(keyword in text for keyword in payment_keywords)
)

payment_count = df["tema_odeme"].sum()
payment_percentage = (payment_count / len(df)) * 100

print("Ödeme teması bulunan yorum:", payment_count)
print("Oran (%):", round(payment_percentage, 2))




print("\n" + "-" * 70)
print("TEMA ANALİZİ - HESAP / GİRİŞ")
print("-" * 70)

account_keywords = [
    "can't login",
    "cant login",
    "cannot login",
    "can't log in",
    "cant log in",
    "cannot log in",
    "can't sign in",
    "cant sign in",
    "cannot sign in",
    "login failed",
    "login error",
    "sign in failed",
    "sign in error",
    "forgot password",
    "password doesn't work",
    "password does not work",
    "verification code",
    "verification problem",
    "verification failed",
    "can't access account",
    "cant access account",
    "cannot access account",
    "locked out",
    "account locked"
]

df["tema_hesap"] = df["review_text"].astype(str).str.lower().apply(
    lambda text: any(keyword in text for keyword in account_keywords)
)

account_count = df["tema_hesap"].sum()
account_percentage = (account_count / len(df)) * 100

print("Hesap / giriş teması bulunan yorum:", account_count)
print("Oran (%):", round(account_percentage, 2))



print("\n" + "-" * 70)
print("TEMA ANALİZİ - KULLANIM / ARAYÜZ")
print("-" * 70)

ux_keywords = [
    "hard to use",
    "difficult to use",
    "hard to navigate",
    "difficult to navigate",
    "can't navigate",
    "cant navigate",
    "navigation is confusing",
    "confusing navigation",
    "confusing interface",
    "bad interface",
    "poor interface",
    "bad design",
    "poor design",
    "button doesn't work",
    "button does not work",
    "menu doesn't work",
    "menu does not work"
]

df["tema_arayuz"] = df["review_text"].astype(str).str.lower().apply(
    lambda text: any(keyword in text for keyword in ux_keywords)
)

ux_count = df["tema_arayuz"].sum()
ux_percentage = (ux_count / len(df)) * 100

print("Kullanım / arayüz teması bulunan yorum:", ux_count)
print("Oran (%):", round(ux_percentage, 2))



print("\n" + "-" * 70)
print("TEMA ANALİZİ - PERFORMANS / YAVAŞLIK")
print("-" * 70)

performance_keywords = [
    "very slow",
    "too slow",
    "so slow",
    "app is slow",
    "app was slow",
    "loading forever",
    "takes forever to load",
    "takes too long to load",
    "loading issue",
    "loading problem",
    "lagging",
    "keeps freezing",
    "app freezes",
    "app freezing",
    "not responding",
    "slow to load"
]

df["tema_performans"] = df["review_text"].astype(str).str.lower().apply(
    lambda text: any(keyword in text for keyword in performance_keywords)
)

performance_count = df["tema_performans"].sum()
performance_percentage = (performance_count / len(df)) * 100

print("Performans / yavaşlık teması bulunan yorum:", performance_count)
print("Oran (%):", round(performance_percentage, 2))




print("\n" + "=" * 70)
print("TEMA KOLONLARI HAZIR")
print("=" * 70)

theme_columns = [
    "tema_hata",
    "tema_guncelleme",
    "tema_destek",
    "tema_odeme",
    "tema_hesap",
    "tema_arayuz",
    "tema_performans"
]

for column in theme_columns:
    print(f"{column}: {df[column].sum()} yorum")


    print("\nTema sonuçları kaydediliyor...")

output_path = "../data/processed/mobil_tema.csv"

df.to_csv(
    output_path,
    index=False,
    encoding="utf-8-sig"
)

print("Tema verisi kaydedildi:", output_path)
print("Toplam kayıt:", len(df))