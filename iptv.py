import requests
import re
from concurrent.futures import ThreadPoolExecutor

def m3u8_coz(icerik):
    kanallar = []
    bloklar = icerik.split('#EXTINF')

    for blok in bloklar[1:]:
        satirlar = blok.strip().split('\n')
        if len(satirlar) < 2:
            continue

        bilgi = satirlar[0]
        url = satirlar[1]

        ad = re.search(r',(.+)', bilgi)
        grup = re.search(r'group-title="([^"]+)"', bilgi)

        kanallar.append({
            'kanal': ad.group(1).strip() if ad else "Bilinmiyor",
            'grup': grup.group(1).strip() if grup else "Genel",
            'url': url
        })

    return kanallar

def baglanti_kontrol(kanal, deneme=2):
    for _ in range(deneme):
        try:
            response = requests.head(kanal['url'], timeout=5, allow_redirects=True)
            if response.status_code in [200, 301, 302]:
                return True
            response = requests.get(kanal['url'], stream=True, timeout=5)
            if response.status_code == 200:
                return True
        except:
            continue
    return False

def sadece_spor_aktif(kanallar):
    anahtar_kelimeler = {
        'spor','futbol','basket','voleybol','hentbol','tenis','motorspor','Bein Sport','Beinsport','BEIN SPORT','BEINSPORT',
        'sport','sports','football','basketball','volleyball','handball','tennis',
        'motorsport','racing','nfl','nba','nhl','mlb','fifa','uefa','champions',
        'premier league','la liga','serie a','bundesliga','mls','ncaa','cricket',
        'rugby','golf','boxing','mma',
        'fußball','deporte','fútbol','baloncesto','moto'
    }

    spor_kanallar = [
        k for k in kanallar
        if any(kw in k['grup'].lower() or kw in k['kanal'].lower() for kw in anahtar_kelimeler)
    ]

    with ThreadPoolExecutor(max_workers=20) as executor:
        sonuc = list(executor.map(lambda k: k if baglanti_kontrol(k) else None, spor_kanallar))

    return [k for k in sonuc if k]

def m3u_kaydet(kanallar, dosya_adi):
    with open(dosya_adi, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for kanal in kanallar:
            f.write(f'#EXTINF:-1 group-title="{kanal["grup"]}",{kanal["kanal"]}\n')
            f.write(f'{kanal["url"]}\n')
    print(f"[💾] {dosya_adi} kaydedildi. ({len(kanallar)} aktif spor kanalı)")

def main():
    playlist_urls = [
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/DaddyLive.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/DaddyLiveEvents.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/DrewAll.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/JapanTV.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/PlexTV.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/DrewLiveVOD.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/Radio.m3u8",
    "http://drewlive24.duckdns.org:8081/PPVLand.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/StreamEast.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/FSTV24.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/TheTVApp.m3u8",
    "http://drewlive24.duckdns.org:8081/Tims247.m3u8",
    "http://drewlive24.duckdns.org:8081/Zuzz.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/SamsungTVPlus.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/Xumo.m3u8"
]
    print("[📡] IPTV listeleri indiriliyor...")
    tum_kanallar = []

    for url in playlist_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.ok:
                yeni = m3u8_coz(response.text)
                print(f"→ {url.split('/')[-1]}: {len(yeni)} kanal")
                tum_kanallar.extend(yeni)
        except Exception as e:
            print(f"[!] {url} hata verdi: {e}")

    print(f"\n🔍 Spor kategorisi filtreleniyor ve bağlantılar test ediliyor...\n")
    aktif_spor_kanallar = sadece_spor_aktif(tum_kanallar)

    print(f"Toplam: {len(tum_kanallar)} kanal")
    print(f"Spor bulunan: {len(aktif_spor_kanallar)} aktif spor kanalı\n")

    m3u_kaydet(aktif_spor_kanallar, "spor.m3u8")

if __name__ == "__main__":
    main()
