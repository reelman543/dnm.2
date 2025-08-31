import requests
from bs4 import BeautifulSoup

# Kullanıcı bilgileri
USERNAME = "FORZA ESES"
PASSWORD = "aTv26E"

LOGIN_URL = "https://sat-forum.net/ucp.php?mode=login"
REFERER_TOPIC = "https://sat-forum.net/viewtopic.php?f=41&t=7857"
M3U_URLS = ["https://sat-forum.net/download/file.php?id=28161"]
OUTPUT_FILE = "RM26.m3u"

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
})

# 1. login formunu çek
resp = session.get(LOGIN_URL)
soup = BeautifulSoup(resp.text, "html.parser")

# 👇 Buradaki birden fazla hidden input olabilir:
creation_time = soup.find("input", {"name": "creation_time"})["value"]
form_token = soup.find("input", {"name": "form_token"})["value"]
# Eğer başka hidden input’lar varsa, onları da buraya ekle

payload = {
    "username": USERNAME,
    "password": PASSWORD,
    "login": "Login",           # butonun name ve value değerine göre
    "creation_time": creation_time,
    "form_token": form_token,
    "redirect": "./index.php",
}

login_resp = session.post(LOGIN_URL, data=payload)
if "Hatalı" in login_resp.text or "yanlış" in login_resp.text:
    raise SystemExit("❌ Giriş başarısız!")
print("✅ Giriş başarılı.")

merged = "#EXTM3U\n"
seen = set()

down_headers = {
    "User-Agent": session.headers["User-Agent"],
    "Referer": REFERER_TOPIC
}

for url in M3U_URLS:
    r = session.get(url, headers=down_headers)
    print("İndirme durum:", r.status_code)
    text = r.content.decode("utf-8", errors="ignore")
    print("İlk 200 karakter:", text[:200])

    for i, line in enumerate(text.splitlines()):
        line = line.strip().lstrip("\ufeff")
        if line.startswith("#EXTINF:"):
            name = line.split(",")[-1].strip().lower()
            if name not in seen:
                merged += line + "\n"
                seen.add(name)
                if i+1 < len(text.splitlines()):
                    merged += text.splitlines()[i+1].strip() + "\n"

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(merged)

print(f"✅ {OUTPUT_FILE} oluşturuldu ({len(seen)} kanal).")
