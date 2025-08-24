import requests

# M3U kaynak linkleri
m3u_urls = [
    "https://raw.githubusercontent.com/kadirsener1/CanliTvListe/main/yeni.m3u",
    
]

output_file = ".m3u"
merged_content = "#EXTM3U\n"
eklenen_kanallar = set()

for url in m3u_urls:
    try:
        print(f"İndiriliyor: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        content = response.text.strip()

        if content.startswith("#EXTM3U"):
            content = content.split("\n", 1)[1]

        lines = content.strip().splitlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("#EXTINF"):
                kanal_satiri = line
                i += 1
                if i < len(lines):
                    stream_url = lines[i].strip()
                    kanal_anahtar = kanal_satiri + stream_url
                    if kanal_anahtar not in eklenen_kanallar:
                        eklenen_kanallar.add(kanal_anahtar)
                        merged_content += kanal_satiri + "\n" + stream_url + "\n"
            i += 1

    except Exception as e:
        print(f"Hata oluştu: {url}\n{e}")

with open(output_file, "w", encoding="utf-8") as f:
    f.write(merged_content.strip() + "\n")

print(f"\nBirleştirme tamamlandı: {output_file}")
