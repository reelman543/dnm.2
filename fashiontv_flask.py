import re
import requests
import logging
import sys
import threading
import time
from flask import Flask, jsonify

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

SOURCE_URL = "https://cool-tv-online.com/ch/fashion-tv/"
OUTPUT_FILE = "fashiontv.m3u"
UPDATE_INTERVAL = 300

M3U_REGEX = re.compile(r"https?://[^\s'"<>]+?\.(?:m3u8|m3u)(?:\?[^\s'"<>]*)?", re.IGNORECASE)
current_url = None

app = Flask(__name__)

def fetch_html(url):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; TokenUpdater/1.0)"}
    try:
        logging.info("🌐 Sayfa indiriliyor: %s", url)
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        return r.text
    except Exception as e:
        logging.error("❌ Sayfa indirilemedi: %s", e)
        return ""

def extract_m3u(html):
    matches = M3U_REGEX.findall(html)
    if not matches:
        logging.warning("⚠️ Sayfada hiç m3u linki bulunamadı!")
        return None
    for m in matches:
        if "token" in m.lower() or "auth" in m.lower() or "sig=" in m.lower():
            logging.info("✅ Tokenli URL bulundu: %s", m)
            return m
    logging.info("ℹ️ Token bulunmadı, ilk m3u seçildi: %s", matches[0])
    return matches[0]

def save_m3u(url):
    content = "#EXTM3U\n" + url + "\n"
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        logging.info("💾 Dosya yazıldı: %s", OUTPUT_FILE)
    except Exception as e:
        logging.error("❌ Dosya yazılamadı: %s", e)

def update_url():
    global current_url
    while True:
        html = fetch_html(SOURCE_URL)
        if html:
            url = extract_m3u(html)
            if url:
                current_url = url
                save_m3u(url)
        time.sleep(UPDATE_INTERVAL)

@app.route("/current", methods=["GET"])
def get_current():
    if current_url:
        return jsonify({"url": current_url})
    return jsonify({"error": "URL henüz alınamadı"}), 503

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Tek seferlik çalıştır")
    args = parser.parse_args()

    if args.once:
        html = fetch_html(SOURCE_URL)
        if html:
            url = extract_m3u(html)
            if url:
                save_m3u(url)
        sys.exit(0)
    else:
        thread = threading.Thread(target=update_url, daemon=True)
        thread.start()
        app.run(host="0.0.0.0", port=5000)
