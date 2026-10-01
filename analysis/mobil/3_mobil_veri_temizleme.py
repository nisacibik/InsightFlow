import pandas as pd

print("=" * 70)
print("INSIGHTFLOW - MOBİL VERİ TEMİZLEME")
print("=" * 70)


print("\nHam veri okunuyor...")

df = pd.read_csv("../data/raw/mobil_45000.csv")

print("Başlangıç kayıt sayısı:", len(df))


print("\nYorum metinleri kontrol ediliyor...")

df["review_text"] = df["review_text"].astype(str).str.strip()

before = len(df)

df = df[df["review_text"] != ""]

after = len(df)

print("Boş yorum nedeniyle silinen kayıt:", before - after)

print("\nDuplicate kontrolü yapılıyor...")

before = len(df)

df = df.drop_duplicates()

after = len(df)

print("Duplicate nedeniyle silinen kayıt:", before - after)

print("\nTarih formatı düzenleniyor...")

df["review_date"] = pd.to_datetime(
    df["review_date"],
    errors="coerce"
)

before = len(df)

df = df.dropna(subset=["review_date"])

after = len(df)

print("Geçersiz tarih nedeniyle silinen kayıt:", before - after)

print("\nTemizleme sonrası kontroller:")

print("Toplam kayıt:", len(df))
print("Eksik değer:")
print(df.isnull().sum())

output_path = "../data/processed/mobil_cleaned.csv"

print("\nTemiz veri kaydediliyor...")

df.to_csv(
    output_path,
    index=False
)

print("Dosya kaydedildi:")
print(output_path)

print("\n" + "=" * 70)
print("MOBİL VERİ TEMİZLEME TAMAMLANDI")
print("=" * 70)