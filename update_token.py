import re
import requests
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

SOURCE_URL = "https://cool-tv-online.com/ch/fashion-tv/"
OUTPUT_FILE = "fashiontv.m3u"

M3U_REGEX = re.compile(r"https?://[^\s'\"<>]+?\.(?:m3u8|m3u)(?:\?[^\s'\"<>]*)?", re.IGNORECASE)

def fetch_html(url):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; TokenUpdater/1.0)"}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        return r.text
    except Exception as e:
        logging.error("Sayfa indirilemedi: %s", e)
        return ""

def extract_m3u(html):
    matches = M3U_REGEX.findall(html)
    if not matches:
        return None
    # token içeren varsa onu seç
    for m in matches:
        if "token" in m.lower() or "auth" in m.lower() or "sig=" in m.lower():
            return m
    return matches[0]

def save_m3u(url):
    content = "#EXTM3U\n" + url + "\n"
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    logging.info("M3U dosyası güncellendi: %s", OUTPUT_FILE)

def main():
    html = fetch_html(SOURCE_URL)
    if not html:
        return
    url = extract_m3u(html)
    if not url:
        logging.warning("Sayfada tokenli M3U bulunamadı.")
        return
    save_m3u(url)

if __name__ == "__main__":
    main()
