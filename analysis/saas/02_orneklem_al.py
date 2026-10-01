import json
import random

dosya_yolu = "../data/raw/Software.jsonl"
cikti_yolu = "../data/raw/saas_50000.jsonl"

hedef = 50000
ornekler = []

with open(dosya_yolu, "r", encoding="utf-8") as dosya:

    for i, satir in enumerate(dosya):
        veri = json.loads(satir)

        if i < hedef:
            ornekler.append(veri)
        else:
            j = random.randint(0, i)

            if j < hedef:
                ornekler[j] = veri

with open(cikti_yolu, "w", encoding="utf-8") as cikti:
    for veri in ornekler:
        cikti.write(json.dumps(veri, ensure_ascii=False) + "\n")

print(f"{len(ornekler)} kayıt seçildi.")
print(f"Dosya oluşturuldu: {cikti_yolu}")