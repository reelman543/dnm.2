addEventListener('fetch', event => {
  if (event.request.method === 'OPTIONS') {
    event.respondWith(handleOptions());
  } else {
    event.respondWith(handleRequest(event.request));
  }
});

function handleOptions() {
  return new Response(null, {
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, HEAD, OPTIONS',
      'Access-Control-Allow-Headers': 'Range, Accept-Encoding',
      'Access-Control-Max-Age': '86400',
    }
  });
}

const CHANNELS = {
  701: { name: 'beIN Sports 1', stream: 'bein1' },
  702: { name: 'beIN Sports 2', stream: 'bein2' },
  703: { name: 'beIN Sports 3', stream: 'bein3' },
  704: { name: 'beIN Sports 4', stream: 'bein4' },
  705: { name: 'S Sport 1', stream: 'ssport1' },
  730: { name: 'S Sport 2', stream: 'ssport2' },
  706: { name: 'Tivibu Spor 1', stream: 'tivibu1' },
  711: { name: 'Tivibu Spor 2', stream: 'tivibu2' },
  712: { name: 'Tivibu Spor 3', stream: 'tivibu3' },
  713: { name: 'Tivibu Spor 4', stream: 'tivibu4' }
};

async function handleRequest(request) {
  const url = new URL(request.url);

  if (url.pathname === '/playlist.m3u8') {
    return generatePlaylist(url);
  }

  const match = url.pathname.match(/\/(\d+)\.m3u8$/);
  if (!match) {
    return new Response('Geçersiz istek', { status: 400 });
  }

  const channel = CHANNELS[match[1]];
  if (!channel) {
    return new Response('Kanal tanımsız', { status: 404 });
  }

  try {
    const apiUrl = `https://7salamistv.online/ajax?method=channel_stream&stream=${channel.stream}`;
    const apiRes = await fetch(apiUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://7salamistv.online/',
        'X-Requested-With': 'XMLHttpRequest'
      }
    });

    const data = await apiRes.json();
    const streamRes = await fetch(data.stream);
    const m3u8 = await streamRes.text();

    return new Response(m3u8, {
      headers: {
        'Content-Type': 'application/vnd.apple.mpegurl',
        'Access-Control-Allow-Origin': '*'
      }
    });
  } catch (e) {
    return new Response('Hata', { status: 500 });
  }
}

function generatePlaylist(url) {
  let m3u = '#EXTM3U\n\n';
  for (const id in CHANNELS) {
    const ch = CHANNELS[id];
    m3u += `#EXTINF:-1 tvg-id="${id}" tvg-name="${ch.name}" group-title="Spor",${ch.name}\n`;
    m3u += `${url.origin}/${id}.m3u8\n\n`;
  }
  return new Response(m3u, {
    headers: {
      'Content-Type': 'application/vnd.apple.mpegurl',
      'Access-Control-Allow-Origin': '*'
    }
  });
}