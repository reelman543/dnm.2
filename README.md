# m3u8-github-updater (SSL bypass)

Bu proje, `dlhd.dad` üzerindeki belirttiğiniz URL'lerden her saat başı `.m3u8` dosyalarını çeker ve repo'ya commit/push eder. `dlhd.dad` sitesi için SSL doğrulaması atlandı (`verify=False`) çünkü sunucu sertifikası yerel ortamda doğrulanamıyor.

## Kullanım

1. Depoyu GitHub'a push edin.
2. Actions sekmesinden workflow'un çalıştığını kontrol edin.
3. Manuel tetikleme için Actions -> seçili workflow -> "Run workflow" kullanın.

## Güvenlik uyarısı
Sertifika doğrulamasını devre dışı bırakmak (verify=False) güvenlik riskleri taşır. Eğer mümkünse:

- Sunucunun doğru CA sertifikasını temin edin ve `requests.get(..., verify='/path/to/ca.pem')` kullanın, veya
- Sunucu sertifikasını düzeltin (Let's Encrypt/Doğru ara-CA zinciri).
