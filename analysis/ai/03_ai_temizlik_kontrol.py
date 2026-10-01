import pandas as pd


input_path = "../data/raw/The__Generative_AI_Ecosystem_50k_User_Reviews_2026.csv"

df = pd.read_csv(input_path)

actual_length = (
    df["Review_Text"]
    .astype(str)
    .str.len()
)

dataset_length = df["Review_Length_Chars"]


different = df[
    dataset_length != actual_length
].copy()


different["Actual_Length"] = (
    different["Review_Text"]
    .astype(str)
    .str.len()
)

different["Length_Difference"] = (
    different["Review_Length_Chars"]
    - different["Actual_Length"]
)

print("=" * 70)
print("KARAKTER UZUNLUĞU FARKLI KAYITLAR")
print("=" * 70)

print(
    f"Toplam farklı kayıt: {len(different)}"
)


for _, row in different.iterrows():

    print("\n" + "-" * 70)

    print("App:", row["App"])

    print("Review Date:", row["Review_Date"])

    print("Rating:", row["Star_Rating"])

    print("Review Text:")
    print(row["Review_Text"])

    print(
        "Dataset Length:",
        row["Review_Length_Chars"]
    )

    print(
        "Gerçek Length:",
        row["Actual_Length"]
    )

    print(
        "Fark:",
        row["Length_Difference"]
    )


print("\n" + "=" * 70)
print("KONTROL TAMAMLANDI")
print("=" * 70)