import os
import requests
from datetime import datetime

# Çıktı dosyası
OUTPUT_FILE = "dlhd.m3u8"

# URL listesi
URLS = [
    "https://dlhd.dad/schedule/schedule-generated.php",
    "https://dlhd.dad/daddy.json",
    "https://dlhd.dad/stream/stream-302.php"
]

def fetch_and_save(url, output_file):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        content = response.text

        if content.strip() == "":
            print(f"{datetime.now()}: {url} boş geldi, atlandı.")
            return False

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"{datetime.now()}: {url} başarıyla kaydedildi -> {output_file}")
        return True
    except Exception as e:
        print(f"{datetime.now()}: {url} hatası -> {e}")
        return False

def main():
    for i, url in enumerate(URLS):
        output_file = f"{OUTPUT_FILE.replace('.m3u8','')}_{i+1}.m3u8"
        fetch_and_save(url, output_file)

if __name__ == "__main__":
    main()
