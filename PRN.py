import requests
import re
from concurrent.futures import ThreadPoolExecutor

# --- M3U8 çözme ---
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

# --- Porn+18 filtresi ---
def kategori_filtrele(kanallar):
    anahtarlar = ['porn', '18+']
    filtreli = []

    for k in kanallar:
        grup = k['grup'].lower()
        kanal_ad = k['kanal'].lower()
        for anahtar in anahtarlar:
            if anahtar in grup or anahtar in kanal_ad:
                filtreli.append(k)
                break

    return filtreli

# --- Multi-thread bağlantı kontrol ---
def baglanti_kontrol(kanal):
    try:
        response = requests.head(kanal['url'], timeout=5, allow_redirects=True)
        return response.status_code in [200, 301, 302]
    except:
        return False

def baglanti_kontrol_multi(kanallar, max_workers=20):
    aktif = []
    pasif = []
    print(f"[•] {len(kanallar)} kanal test ediliyor...\n")

    def kontrol(kanal):
        return kanal, baglanti_kontrol(kanal)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for kanal, durum in executor.map(kontrol, kanallar):
            print(f"{kanal['kanal']} ({kanal['grup']}): {'✅' if durum else '❌'}")
            if durum:
                aktif.append(kanal)
            else:
                pasif.append(kanal)

    return aktif, pasif

# --- M3U kaydetme ---
def m3u_kaydet(kanallar, dosya_adi):
    with open(dosya_adi, "w", encoding="utf-8", errors='replace') as f:
        f.write("#EXTM3U\n")
        for kanal in kanallar:
            f.write(f'#EXTINF:-1 group-title="{kanal["grup"]}",{kanal["kanal"]}\n')
            f.write(f'{kanal["url"]}\n')
    print(f"[💾] {dosya_adi} kaydedildi. ({len(kanallar)} kanal)")

# --- Ana program ---
def main():
    playlist_urls = [
        "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/DaddyLive.m3u8",
        "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/DrewAll.m3u8",
        "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/DrewLiveVOD.m3u8",
        # İhtiyacınıza göre ek M3U8 listeleri ekleyebilirsiniz
    ]

    print("[📡] Tüm IPTV listeleri indiriliyor...")
    kanallar = []

    for url in playlist_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.ok:
                yeni_kanallar = m3u8_coz(response.text)
                print(f"→ {url.split('/')[-1]}: {len(yeni_kanallar)} kanal bulundu.")
                kanallar.extend(yeni_kanallar)
            else:
                print(f"[!] {url} alınamadı: {response.status_code}")
        except Exception as e:
            print(f"[!] {url} hata verdi: {e}")

    print(f"\n🔢 Toplam {len(kanallar)} kanal toplandı.\n")

    # Sadece porn+18 filtrele
    filtreli = kategori_filtrele(kanallar)
    print(f"[🔍] 'porn+18' kategorisinde {len(filtreli)} kanal bulundu.\n")

    # Bağlantıları test et (multi-thread)
    aktif, pasif = baglanti_kontrol_multi(filtreli)

    # Dosyaları kaydet
    m3u_kaydet(aktif, "aktif_porn18_kanallar.m3u")
    m3u_kaydet(pasif, "calismayan_porn18_kanallar.m3u")

    print(f"\n✅ {len(aktif)} çalışıyor | ❌ {len(pasif)} çalışmıyor")

if __name__ == "__main__":
    main()

