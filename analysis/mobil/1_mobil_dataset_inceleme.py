from datasets import load_dataset

print("=" * 70)
print("INSIGHTFLOW - MOBİL UYGULAMALAR DATASET İNCELEME")
print("=" * 70)

print("\nDataset yükleniyor...")

dataset = load_dataset(
    "dmytrobuhai/play_market_2025_1m_reviews_500_titles",
    data_files="apps_reviews.csv"
)

print("\nDataset başarıyla yüklendi.")

print("\nDataset yapısı:")
print(dataset)

print("\nKolonlar:")
print(dataset["train"].column_names)

print("\nToplam kayıt sayısı:")
print(len(dataset["train"]))

print("\nİlk kayıt:")
print(dataset["train"][0])


import pandas as pd

print("\n45.000 yorum rastgele seçiliyor...")

df = dataset["train"].to_pandas()

mobil_45000 = df.sample(
    n=45000,
    random_state=42
)

print("\nÖrnekleme tamamlandı.")
print("Seçilen kayıt sayısı:", len(mobil_45000))


print("\n45.000 yorum kaydediliyor...")

mobil_45000.to_csv(
    "../data/raw/mobil_45000.csv",
    index=False
)

print("Dosya kaydedildi:")
print("../data/raw/mobil_45000.csv")