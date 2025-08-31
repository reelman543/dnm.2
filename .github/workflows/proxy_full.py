import requests
from flask import Flask, Response, stream_with_context, request
from threading import Thread
import time
import re
import os
import logging

TOKEN_URL = os.getenv("TOKEN_URL")
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", 300))
LOCAL_M3U8 = None

if not os.path.exists("logs"):
    os.makedirs("logs")
logging.basicConfig(filename="logs/proxy.log",
                    level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")

app = Flask(__name__)

def fetch_token_m3u8():
    global LOCAL_M3U8
    while True:
        try:
            r = requests.get(TOKEN_URL, timeout=10)
            if r.status_code == 200:
                LOCAL_M3U8 = r.text
                logging.info("Tokenli M3U8 güncellendi.")
            else:
                logging.warning(f"Tokenli URL çekilemedi, status code: {r.status_code}")
        except Exception as e:
            logging.error(f"Token çekme hatası: {e}")
        time.sleep(UPDATE_INTERVAL)

@app.route("/stream.m3u8")
def stream_m3u8():
    global LOCAL_M3U8
    if not LOCAL_M3U8:
        return "Stream henüz yüklenmedi.", 503

    content = LOCAL_M3U8
    def replace_ts_url(match):
        url = match.group(1)
        return f"/segment?url={requests.utils.quote(url)}"

    content = re.sub(r"(https?://[^\s]+\.ts)[^\s]*", replace_ts_url, content)
    logging.info("M3U8 stream isteği alındı.")
    return Response(content, mimetype="application/vnd.apple.mpegurl")

@app.route("/segment")
def proxy_segment():
    ts_url = request.args.get("url")
    if not ts_url:
        return "URL parametresi eksik.", 400
    ts_url = requests.utils.unquote(ts_url)
    try:
        r = requests.get(ts_url, stream=True, timeout=10)
        logging.info(f"Segment proxy isteği: {ts_url}")
        return Response(stream_with_context(r.iter_content(chunk_size=1024)), content_type="video/MP2T")
    except Exception as e:
        logging.error(f"Segment çekilemedi: {ts_url} -> {e}")
        return f"Segment çekilemedi: {e}", 500

if __name__ == "__main__":
    t = Thread(target=fetch_token_m3u8, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=5000)