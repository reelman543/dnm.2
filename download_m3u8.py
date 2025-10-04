#!/usr/bin/env python3
# download_m3u8.py
# SSL doğrulama hatası (CERTIFICATE_VERIFY_FAILED) nedeniyle verify=False kullanılır.

import os
import requests
import urllib3
from datetime import datetime

# urllib3 insecure warnings kapat
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Çıktı dosyası temel adı
OUTPUT_BASENAME = "dlhd"

# Kaynak URL'ler
URLS = [
    "https://dlhd.dad/schedule/schedule-generated.php",
    "https://dlhd.dad/daddy.json",
    "https://dlhd.dad/stream/stream-302.php",
]

# Zaman aşımı
TIMEOUT = 15

# İndirme fonksiyonu (verify=False)
def fetch_and_save(url: str, output_file: str) -> bool:
    try:
        resp = requests.get(url, timeout=TIMEOUT, verify=False)
        resp.raise_for_status()
        content = resp.text

        if not content or content.strip() == "":
            print(f"{datetime.now()}: {url} boş geldi, atlandı.")
            return False

        # Dizini oluştur
        os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"{datetime.now()}: {url} başarıyla kaydedildi -> {output_file}")
        return True

    except Exception as e:
        print(f"{datetime.now()}: {url} hatası -> {e}")
        return False

def main():
    results = []
    for idx, url in enumerate(URLS, start=1):
        out_name = f"{OUTPUT_BASENAME}_{idx}.m3u8"
        ok = fetch_and_save(url, out_name)
        results.append((url, out_name, ok))

    # Özet
    print("\n--- Özet ---")
    for url, out, ok in results:
        print(f"{out}: {'OK' if ok else 'FAILED'} ({url})")

if __name__ == "__main__":
    main()
