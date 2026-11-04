# Spec 0002 — Kayıtlı XSS ve kalıcı debug modunu kapatma (mini)

- Status: In progress
- Mode: lite
- Plan: `specs/plans/0002-plan.md`
- Source: `docs/security.md`, "Bilinen açıklar" 1 (kayıtlı XSS) ve 2 (`debug=True` kalıcı)
- Design: yok. Görünüm değişmez; özel karakterler yalnızca düz metin olarak görünür.
- Supersedes: —

## Intent
LeaveManager'da bir kullanıcının girdiği metin, örneğin izin talebinin "Neden" alanı, sayfaya HTML
olarak basılıyor. Talep listesini açan herkesin, İK dahil, tarayıcısında başkasının yazdığı kod
çalışabiliyor. Ayrıca uygulama her zaman debug modunda başlıyor ve bir hata olduğunda ağdan kod
çalıştırmaya izin veren hata ayıklayıcıyı açıyor. Bu iş iki açığı kapatır, böylece uygulama
gerçek kullanıma açılmaya bir adım yaklaşır. İzin kuralları ve sayfaların gösterdiği veri değişmez.

## Changed behavior
- [ ] CB-1 — "Neden" alanına `<script>alert(1)</script>` ya da `<img src=x onerror=alert(1)>` yazılıp kaydedilen bir talep, talep listesinde **aynen yazıldığı gibi düz metin** olarak görünür. Sayfada çalışabilir bir `<script>` ya da `<img>` öğesi oluşmaz.
- [ ] CB-2 — Personel adı ve birimi HTML karakterleri içerse bile (ör. `<b>Ali</b>`), ana sayfadaki bakiye tablosunda, talep listesinde ve yeni talep formunun personel listesinde düz metin olarak görünür. Bir öğe oluşmaz ve form seçeneğinin dışına taşmaz.
- [ ] CB-3 — `&`, `'`, `"`, `<`, `>` ve Türkçe karakterler (ör. `Çocuğun "okul" töreni & veli toplantısı`) kullanıcının yazdığı gibi, okunur şekilde görünür. Çift kaçışlama olmaz (ekranda `&amp;` görünmez).
- [ ] CB-4 — Uygulama doğrudan başlatıldığında, ayrıca bir ayar yapılmamışsa, debug modu **kapalıdır**. Beklenmeyen bir hata, örneğin talep listesinde var olmayan bir personele ait bir talep, kullanıcıya genel, Türkçe bir hata mesajı gösterir (ör. "Beklenmeyen bir hata oluştu."; tam metin sabitlenmez, OD-7 değiştirecek). Sayfada stack trace, dosya yolu, kod satırı ya da etkileşimli hata ayıklayıcı yer almaz.
- [ ] CB-5 — Debug modu yalnızca geliştiricinin bilerek verdiği bir ortam ayarıyla açılır. Kodun içinde debug modunu kalıcı olarak açan bir ayar kalmaz.

## Preserved behavior
- [ ] PB-1 — Spec 0001'in 31 karakterizasyon testi **hiç değiştirilmeden** yeşil kalır. BR-1…BR-10 ve OD-4/OD-6/OD-7 davranışı aynıdır.
- [ ] PB-2 — Ana sayfa (bekleyen, onaylanan, reddedilen sayıları ve personel bakiye tablosu), talep listesi (personel, başlangıç, bitiş, gün, neden, durum) ve yeni talep formu, seed verisiyle bugünkü verinin aynısını gösterir.
- [ ] PB-3 — Durum rozetleri bugünkü renklerini korur: `Onaylandi` yeşil, `Beklemede` turuncu, `Reddedildi` kırmızı.
- [ ] PB-4 — Bakiye yetersiz olduğunda form bugünkü hata mesajını gösterir. Mesajın metni değişmez, çünkü değişmesi OD-7'nin konusu.

## Out of scope
- OD-1…OD-8'den herhangi birini kapatmak. Özellikle hata mesajındaki iç kod ve dahili telefon numarası (`ERR-412 … dahili 4127`) bu işte değişmez; OD-7 ile değişir.
- Form girdisi doğrulama (personel var mı, bitiş ≥ başlangıç, "Neden" uzunluk sınırı). `docs/security.md` bunu istiyor, ama doğrulamanın ne zaman hata vereceği OD-6 ve OD-7'nin konusu.
- Kimlik doğrulama ve yetki (ayrı spec, 0003). Bu spec kapansa da uygulama `localhost` dışına açılmaz; açılabilmesi için 0003 gerekir.
- Kodu katmanlara bölmek (ayrı refactor spec'i). Bu işte HTML üretimi yalnızca güvenli hale getirilir.
- İçerik güvenlik politikası (CSP) gibi ek tarayıcı başlıkları ve görsel tasarım değişikliği.
- Split: proposed (a) XSS, (b) debug modu; kept as one — yagmur.cilek, 2026-11-04: ikisi de küçük, aynı güvenlik bölümünden ve tek PR'da incelenebilir.

## Definition of Done
- [ ] `scripts/check` green
- [ ] Independent review done; real findings fixed, noise rejected with written rationale
- [ ] Criterion ↔ evidence table complete for CB-* **and** PB-* (UI: before/after screenshots)
- [ ] Spec moved to `specs/done/` (immutable there)
