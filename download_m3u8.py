#!/usr/bin/env python3
# download_m3u8.py
# Improved: handles raw m3u/m3u8 content and JSON->M3U conversion for daddy.json.
# SSL doğrulama hatası (CERTIFICATE_VERIFY_FAILED) nedeniyle verify=False kullanılır.

import os
import requests
import urllib3
import json
from datetime import datetime

# urllib3 insecure warnings kapat
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Çıktı dosyası temel adı
OUTPUT_BASENAME = "dlhd"

# Kaynak URL'ler (örnek sırayla)
URLS = [
    "https://dlhd.dad/schedule/schedule-generated.php",
    "https://dlhd.dad/daddy.json",
    "https://dlhd.dad/stream/stream-302.php",
]

# daddy.json URL index (URLS listesinde hangi index'te olduğunu belirtir)
JSON_INDEX = 1  # ikinci eleman

# Stream URL template (channel_id yerine {id} koyun)
STREAM_URL_TEMPLATE = os.environ.get("DLHD_STREAM_TEMPLATE", "https://dlhd.dad/stream/stream-{id}.php")

# Zaman aşımı
TIMEOUT = 15

def is_probably_m3u(text: str) -> bool:
    """Basit kontrol: EXTINF veya EXTM3U içeriyorsa m3u olarak kabul et."""
    if not text:
        return False
    t = text.strip().lower()
    return t.startswith('#extm3u') or '#extinf' in t or t.count('\nhttp')>0

def fetch_text(url: str) -> (str, bool):
    """İsteği yapar, metin döndürür. verify=False kullanır. Returns (text, success)."""
    try:
        resp = requests.get(url, timeout=TIMEOUT, verify=False)
        resp.raise_for_status()
        return resp.text, True
    except Exception as e:
        print(f"{datetime.now()}: {url} hatası -> {e}")
        return "", False

def save_file(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def generate_m3u_from_json_list(data_list, out_path, stream_template=STREAM_URL_TEMPLATE):
    lines = ["#EXTM3U\n"]
    count = 0
    for item in data_list:
        if not isinstance(item, dict):
            continue
        name = item.get('channel_name') or item.get('name') or item.get('title') or ''
        cid = item.get('channel_id') or item.get('id') or item.get('channel') or ''
        if not name or cid in (None, ''):
            continue
        cid = str(cid).strip()
        name = str(name).strip()
        extinf = f'#EXTINF:-1 tvg-id="{cid}" tvg-name="{name}" group-title="DLHD",{name}'
        stream_url = stream_template.format(id=cid)
        lines.append(extinf + '\n')
        lines.append(stream_url + '\n')
        count += 1
    save_file(out_path, ''.join(lines))
    print(f"{datetime.now()}: M3U oluşturuldu -> {out_path} (kanal sayısı: {count})")
    return count

def main():
    results = []
    json_text = None
    for idx, url in enumerate(URLS, start=1):
        text, ok = fetch_text(url)
        out_name = f"{OUTPUT_BASENAME}_{idx}.m3u8"
        # Eğer gelen metin muhtemelen m3u ise olduğu gibi kaydet
        if ok and is_probably_m3u(text):
            save_file(out_name, text)
            print(f"{datetime.now()}: {url} muhtemelen M3U, kaydedildi -> {out_name}")
        elif ok and idx-1 == JSON_INDEX:
            # daddy.json beklenen JSON listesi veya başka JSON olabilir
            json_text = text
            # Kaydet raw JSON olarak da isteğe bağlı
            save_file(out_name, text)
            print(f"{datetime.now()}: {url} JSON/diğer format olarak kaydedildi -> {out_name}")
        elif ok:
            # diğer durumlarda ham metni yine kaydet
            save_file(out_name, text)
            print(f"{datetime.now()}: {url} ham içerik olarak kaydedildi -> {out_name}")
        else:
            print(f"{datetime.now()}: {url} indirilemedi, atlandı -> {out_name}")
        results.append((url, out_name, ok))

    # Eğer daddy.json geldiyse M3U üret
    if json_text:
        try:
            parsed = json.loads(json_text)
            # Eğer JSON'da bir kök nesne içinde channels alanı varsa, onu kullan
            if isinstance(parsed, dict) and 'channels' in parsed and isinstance(parsed['channels'], list):
                count = generate_m3u_from_json_list(parsed['channels'], 'dlhd_channels.m3u')
            elif isinstance(parsed, list):
                count = generate_m3u_from_json_list(parsed, 'dlhd_channels.m3u')
            else:
                # Beklenmedik JSON, deneme: eğer içinde dizi bulursak ilk bulduğumuzu kullan
                found = None
                if isinstance(parsed, dict):
                    for v in parsed.values():
                        if isinstance(v, list):
                            found = v
                            break
                if found:
                    count = generate_m3u_from_json_list(found, 'dlhd_channels.m3u')
                else:
                    print(f"{datetime.now()}: JSON içinde uygun kanal listesi bulunamadı.")
        except Exception as e:
            print(f"{datetime.now()}: JSON parse hatası -> {e}")

    # Özet
    print("\n--- Özet ---")
    for url, out, ok in results:
        print(f"{out}: {'OK' if ok else 'FAILED'} ({url})")

if __name__ == '__main__':
    main()
