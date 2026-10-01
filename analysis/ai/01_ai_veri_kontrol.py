import os
import pandas as pd


print("=" * 70)
print("INSIGHTFLOW - AI DATASET KONTROLÜ")
print("=" * 70)

input_path = "../data/raw/The__Generative_AI_Ecosystem_50k_User_Reviews_2026.csv"

if not os.path.exists(input_path):
    raise FileNotFoundError(
        f"Dataset bulunamadı:\n{input_path}"
    )

print("\nDataset bulundu.")
print(f"Dosya: {input_path}")


df = pd.read_csv(input_path)

print("\n" + "=" * 70)
print("GENEL BİLGİ")
print("=" * 70)

print(f"Satır sayısı : {len(df):,}")
print(f"Sütun sayısı : {len(df.columns)}")
print("\n" + "=" * 70)
print("SÜTUNLAR")
print("=" * 70)

for i, column in enumerate(df.columns, start=1):
    print(f"{i}. {column}")

print("\n" + "=" * 70)
print("VERİ TİPLERİ")
print("=" * 70)

print(df.dtypes)
print("\n" + "=" * 70)
print("EKSİK VERİ KONTROLÜ")
print("=" * 70)

missing = df.isnull().sum()

print(missing)
print("\n" + "=" * 70)
print("DUPLICATE KONTROLÜ")
print("=" * 70)

print(
    f"Tamamen aynı kayıt sayısı: "
    f"{df.duplicated().sum():,}"
)

print("\n" + "=" * 70)
print("İLK 5 KAYIT")
print("=" * 70)

print(df.head().to_string())
print("\n" + "=" * 70)
print("KATEGORİK ALANLAR")
print("=" * 70)

for column in df.columns:

    if df[column].dtype == "object":

        unique_count = df[column].nunique()

        print(
            f"\n{column}: "
            f"{unique_count:,} unique değer"
        )

        if unique_count <= 20:
            print(df[column].unique())


print("\n" + "=" * 70)
print("KONTROL TAMAMLANDI")
print("=" * 70)