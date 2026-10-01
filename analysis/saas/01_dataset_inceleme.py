import json

dosya_yolu = "../data/raw/Software.jsonl"

with open(dosya_yolu, "r", encoding="utf-8") as dosya:
    ilk_satir = dosya.readline()
    veri = json.loads(ilk_satir)

print("Kolonlar:")
print(veri.keys())

print("\nİlk kayıt:")
print(veri)