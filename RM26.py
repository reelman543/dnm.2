import requests

m3u_urls = [
    "https://sat-forum.net/download/file.php?id=28161",
]

output_file = "RM26.m3u"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/117.0.0.0 Safari/537.36"
}

merged_content = "#EXTM3U\n"
eklenen_kanallar = set()

for url in m3u_urls:
    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()

        # İlk deneme: text
        raw_text = r.text.strip()

        # Eğer çok kısa geldiyse (muhtemelen binary)
        if len(raw_text) < 20:
            raw_text = r.content.decode("utf-8", errors="ignore")

        lines = raw_text.splitlines()

        for i, line in enumerate(lines):
            line = line.strip().lstrip("\ufeff")
            if line.startswith("#EXTINF:"):
                kanal_adi = line.split(",")[-1].strip().lower()
                if kanal_adi not in eklenen_kanallar:
                    merged_content += line + "\n"
                    eklenen_kanallar.add(kanal_adi)
                    if i + 1 < len(lines):
                        merged_content += lines[i + 1].strip() + "\n"

    except Exception as e:
        print(f"Hata: {e} ({url})")

with open(output_file, "w", encoding="utf-8") as f:
    f.write(merged_content)

print(f"{output_file} dosyası oluşturuldu ({len(eklenen_kanallar)} kanal).")
