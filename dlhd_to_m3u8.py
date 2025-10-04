
import requests
from datetime import datetime

OUTPUT_FILE = "dlhd.m3u8"

def fetch_json(url):
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"HATA: {url} alınamadı -> {e}")
        return None

def parse_channels(data):
    channels = []
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict) and 'url' in v:
                channels.append({
                    "name": v.get("name", k),
                    "url": v["url"],
                    "group": v.get("group", "Uncategorized")
                })
    elif isinstance(data, list):
        for v in data:
            if isinstance(v, dict) and 'url' in v:
                channels.append({
                    "name": v.get("name", v.get("title", "Unknown")),
                    "url": v["url"],
                    "group": v.get("group", "Uncategorized")
                })
    return channels

def save_m3u8(channels, filename=OUTPUT_FILE):
    header = "#EXTM3U\n"
    body = ""
    for ch in channels:
        body += f'#EXTINF:-1 group-title="{ch["group"]}",{ch["name"]}\n{ch["url"]}\n'
    with open(filename, "w", encoding="utf-8") as f:
        f.write(header + body)
    print(f"{len(channels)} kanal kaydedildi -> {filename}")

def main():
    urls = [
        "https://dlhd.dad/schedule/schedule-generated.php",
        "https://dlhd.dad/daddy.json"
    ]
    all_channels = []
    for u in urls:
        data = fetch_json(u)
        if data:
            all_channels.extend(parse_channels(data))
    if all_channels:
        save_m3u8(all_channels)
    else:
        print("Kanal bulunamadı!")

if __name__ == "__main__":
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Güncelleme başlatılıyor...")
    main()
