import requests
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

playlist_urls = [
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/DaddyLive.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/DaddyLiveEvents.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/DrewAll.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/JapanTV.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/PlexTV.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/PlutoTV.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/TubiTV.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/DrewLiveVOD.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/TVPass.m3u",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/Radio.m3u8",
    "http://drewlive24.duckdns.org:8081/PPVLand.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/StreamEast.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/FSTV24.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/Roku.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/TheTVApp.m3u8",
    "http://drewlive24.duckdns.org:8081/Tims247.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/LGTV.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/AriaPlus.m3u8",
    "http://drewlive24.duckdns.org:8081/Zuzz.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/SamsungTVPlus.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/Xumo.m3u8"
]

EPG_URL = "http://drewlive24.duckdns.org:8081/merged2_epg.xml.gz"
OUTPUT_FILE = "NSFW.m3u8"

# -------------------- Fetch Playlist --------------------
def fetch_playlist(url):
    try:
        res = requests.get(url, timeout=15)
        res.raise_for_status()
        return res.content.decode('utf-8', errors='ignore').splitlines()
    except Exception as e:
        print(f"❌ Failed to fetch {url}: {e}")
        return []

# -------------------- Parse Playlist --------------------
def parse_playlist(lines):
    parsed_channels = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF:"):
            extinf_line = line
            headers = []
            i += 1
            while i < len(lines) and lines[i].strip().startswith("#") and not lines[i].strip().startswith("#EXTINF:"):
                headers.append(lines[i].strip())
                i += 1
            if i < len(lines):
                url_line = lines[i].strip()
                i += 1
                if not url_line or url_line.lower() in ["*", "none", "null"]:
                    continue
                # Kanal adı çıkarma (daha güvenli)
                name_match = re.split(r',', extinf_line, maxsplit=1)
                channel_name = name_match[-1].strip() if len(name_match) > 1 else "Unknown"
                # Kanal bazlı tvg-id ekle
                if not re.search(r'tvg-id="', extinf_line):
                    extinf_line = extinf_line.replace("#EXTINF:", f'#EXTINF:-1 tvg-id="{channel_name}" ', 1)
                parsed_channels.append((extinf_line, tuple(headers), url_line))
        else:
            i += 1
    return parsed_channels

# -------------------- Write Merged Playlist --------------------
def write_merged_playlist(channels):
    lines = ['#EXTM3U', '']

    # Grup bazlı organize et
    groups = {}
    for extinf, headers, url in channels:
        group_match = re.search(r'group-title="([^"]+)"', extinf)
        group_name = group_match.group(1) if group_match else "Other"
        groups.setdefault(group_name, []).append((extinf, headers, url))

    # Alfabetik olarak grupları ve kanalları sırala
    for group_name in sorted(groups.keys()):
        lines.append(f'#EXTGRP:{group_name}')
        for extinf, headers, url in sorted(groups[group_name], key=lambda x: re.split(r',', x[0], maxsplit=1)[-1].strip().lower()):
            lines.append(extinf)
            lines.extend(headers)
            lines.append(url)
        lines.append("")

    if lines and lines[-1] == "":
        lines.pop()

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines) + "\n")

    total_channels = sum(len(ch) for ch in groups.values())
    print(f"\n✅ Merged playlist written to {OUTPUT_FILE}. Total channels: {total_channels}")

# -------------------- Main --------------------
if __name__ == "__main__":
    print(f"Starting merge at {datetime.now()}...")

    all_channels = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        results = list(executor.map(fetch_playlist, playlist_urls))
        for lines in results:
            parsed = parse_playlist(lines)
            all_channels.extend(parsed)

    write_merged_playlist(all_channels)
    print(f"Merge complete at {datetime.now()}")
