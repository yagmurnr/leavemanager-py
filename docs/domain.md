# Domain

Bu dosya **bugünkü davranışı** belgeler (bootstrap, 2026-10-23; kaynak: `app.py`). Kodla
çelişen ya da kararı verilmemiş noktalar **açık karar (OD-n)** olarak işaretlidir. Bir OD'yi
kapatmak bir değişiklik talebidir (`/change`): kararı İK verir, spec ile uygulanır, burası
o spec'le birlikte güncellenir.

## Ubiquitous language

| Term | Meaning | Notes / not to be confused with |
|---|---|---|
| Personel (employee) | İzin hakkı olan çalışan. Ad, birim ve işe giriş tarihi taşır. | Kod: `employee`. Birim değerleri: IT, Muhasebe, IK, Satis. |
| İzin talebi (leave request) | Bir personelin başlangıç ve bitiş tarihleri dahil bir aralık için izin isteği. Neden ve durum taşır. | Kod: `request`. Flask'ın `request` nesnesiyle karıştırılmamalı. |
| Durum (status) | Talebin durumu: `Beklemede`, `Onaylandi` ya da `Reddedildi`. | Arayüzde ve veride bu yazımla, Türkçe karakter olmadan saklanır. |
| Kıdem (seniority) | Personelin şirketteki tam yılı. | Bugün yalnızca takvim yılı farkıyla hesaplanıyor (OD-2). |
| Hak (entitlement) | Kıdeme göre bir yılda kullanılabilecek izin günü. | Kod: `get_entitlement`. |
| Kullanılan (used) | `Onaylandi` durumundaki taleplerin gün toplamı. | Bekleyen talepler dahil değil (OD-5). |
| Kalan (remaining) | Hak − Kullanılan. | "Bakiye" ile aynı anlamda kullanılır. |
| Gün (talep günü) | Bir talebin kapsadığı gün sayısı. | Kodda "iş günü" deniyor ama takvim günü sayılıyor (OD-3). |

## Business rules
Bugünkü davranış. Her kural test edilebilir bir ifadedir; karakterizasyon testleri bunları sabitler.

- **BR-1 Hak tablosu:** kıdem < 1 yıl → 0 gün · 1-5 yıl → 14 gün · 6-15 yıl → 20 gün · 16 yıl ve üzeri → 26 gün. (OD-1)
- **BR-2 Kıdem:** `bugünün yılı − işe giriş yılı`. Ay ve gün dikkate alınmaz. (OD-2)
- **BR-3 Gün sayımı:** `bitiş − başlangıç + 1` takvim günü. Hafta sonu ve tatil düşülmez. (OD-3)
- **BR-4 Kullanılan:** yalnızca `Onaylandi` durumundaki taleplerin günleri toplanır. (OD-5)
- **BR-5 Kalan:** Hak − Kullanılan. Negatif olabilir; bir alt sınır yok.
- **BR-6 Bakiye kontrolü (form):** talep günü > Kalan ise talep reddedilir ve hata mesajı gösterilir. (OD-4)
- **BR-7 Bakiye kontrolü (servis):** talep günü ≥ Kalan ise talep **sessizce** kaydedilmez ve kullanıcı yine talep listesine yönlendirilir. (OD-4, OD-7)
- **BR-8 Yeni talep** `Beklemede` durumunda oluşturulur.
- **BR-9 Geçmiş tarihli talep** kabul edilir. İK geriye dönük giriş yapıyor; bilinçli bir karar.
- **BR-10 Tarih aralığı:** bitişin başlangıçtan önce olması bugün engellenmiyor. Gün sayısı ≤ 0 çıkar, bakiye kontrolünden geçer.

### Açık kararlar

| # | Konu | Bugün | Belirsizlik |
|---|---|---|---|
| OD-1 | 1-5 yıl hak | 14 gün | Koddaki yorum (İK el kitabı, 2014) **15 gün** diyor. |
| OD-2 | Kıdem hesabı | Yıl farkı | Aralık'ta giren biri Ocak'ta 1 yıllık sayılıyor; işe giriş yıl dönümü mü esas alınmalı? |
| OD-3 | Gün sayımı | Takvim günü | Yorum "iş günü" diyor; hafta sonu ve resmi tatiller düşülmeli mi? |
| OD-4 | Bakiye sınırı | Form `>`, servis `≥` | Kalan günün tamamı kullanılabilmeli mi? İki kontrol birbiriyle çelişiyor. |
| OD-5 | Bekleyen talepler | Bakiyeden düşülmüyor | 2018'de konuşulmuş, karar verilmemiş. |
| OD-6 | Ters tarih aralığı | Engellenmiyor | Bitiş < başlangıç olan talep doğrulama hatası mı olmalı? (BR-10) |
| OD-7 | Hata davranışı | Hatalar yutuluyor, kullanıcı "başarılı" gibi yönlendiriliyor | Hangi hatada kullanıcıya ne gösterilecek? (`docs/conventions.md`, Error handling) |
| OD-8 | Devreden izin | Yok (kod yorum satırında: en fazla 5 gün) | Yıl sonunda kalan gün devredecek mi? |

## Key domain invariants
- Bir talep her zaman var olan bir personele aittir.
- Durum yalnızca `Beklemede`, `Onaylandi` ya da `Reddedildi` olabilir.
- Kalan, her ekranda aynı kuralla hesaplanır. Bir hesaplamanın tek kaynağı `service` katmanıdır.
- İzin kuralları (BR-n) yalnızca bir spec ile değişir. "Kodda düzeltiverdim" kabul edilmez; mevcut davranış İK'nın alıştığı davranıştır.
