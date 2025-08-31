import requests

# M3U kaynak linkleri
m3u_urls = [
    "https://sat-forum.net/download/file.php?id=28161",
    # Diğer M3U linklerini buraya ekleyebilirsin
]

# Üretilen dosya adı
output_file = "RM26.m3u"

merged_content = "#EXTM3U\n"
eklenen_kanallar = set()

for url in m3u_urls:
    try:
        r = requests.get(url)
        r.raise_for_status()
        lines = r.text.splitlines()
        for i, line in enumerate(lines):
            if line.startswith("#EXTINF:"):
                kanal = line.strip()
                if kanal not in eklenen_kanallar:
                    merged_content += kanal + "\n"
                    eklenen_kanallar.add(kanal)
                    # Sonraki satırda URL vardır
                    if i + 1 < len(lines):
                        merged_content += lines[i + 1].strip() + "\n"
    except Exception as e:
        print(f"Hata: {e} ({url})")

with open(output_file, "w", encoding="utf-8") as f:
    f.write(merged_content)

print(f"{output_file} dosyası oluşturuldu.")
