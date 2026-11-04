# Spec 0003 — Giriş ve oturum

- Status: In progress
- Mode: lite
- Plan: `specs/plans/0003-plan.md`

## Intent
Bugün LeaveManager'a ulaşabilen herkes bütün personelin izin bilgilerini görebiliyor ve herhangi biri
adına talep girebiliyor. Bu veriler arasında sağlık nedeni gibi hassas kişisel veriler (KVKK) de var.
Bu iş, uygulamayı yalnızca giriş yapmış kullanıcıların kullanabileceği hale getirir. Her kullanıcı
hesabı bir personel kaydına bağlıdır. Giriş yapan kişi, sayfada kim olarak giriş yaptığını görür ve
istediğinde çıkış yapabilir. Başarı: giriş yapmamış birinin hiçbir sayfada veri görememesi.

Bilerek yapılmayanlar:
- Kimin neyi göreceği (rol bazlı yetki). Bu iş tamamlanınca giriş yapan herkes bugünkü gibi her şeyi görür; ayrımı spec 0004 getirir.
- Onay ve red ekranı (spec 0005).
- Hesap yönetimi ekranı.

## Requirements
- R-1: Giriş yapmamış bir kullanıcı uygulamanın hiçbir sayfasında personel ya da izin verisi göremez ve hiçbir işlem yapamaz; giriş ekranına yönlendirilir.
- R-2: Kullanıcı, kendisine tanımlanmış kullanıcı adı ve şifreyle giriş yapar.
- R-3: Hatalı giriş, hangi bilginin hatalı olduğunu söylemez (kullanıcı adının var olup olmadığı anlaşılmaz).
- R-4: Her kullanıcı hesabı tam olarak bir personel kaydına bağlıdır. Giriş yapan kullanıcı sayfada kendi adını görür.
- R-5: Kullanıcı çıkış yapabilir; çıkıştan sonra yeniden giriş yapmadan veri göremez.
- R-6: Şifreler hiçbir yerde (veri, log, sayfa) açık metin olarak tutulmaz ya da gösterilmez.
- R-7: Hesaplar, uygulamanın dışında bir yönetici tarafından tanımlanır. Hesap bilgileri ve şifreler depoya (repo) girmez.
- R-8: Oturum, uygulamanın gizli anahtarıyla korunur. Gizli anahtar tanımlı değilse uygulama başlamaz ve nedenini açıkça söyler.

## User experience
- Flow: Kullanıcı herhangi bir sayfayı açar → giriş ekranı → kullanıcı adı ve şifreyi girer → **istediği sayfaya** döner. Menüde adı ve "Çıkış" bağlantısı görünür. Çıkış → giriş ekranı.
- States (giriş ekranı):
  - **Boş:** kullanıcı adı ve şifre alanları ve "Giriş" düğmesi.
  - **Hatalı giriş:** "Kullanıcı adı veya şifre hatalı." mesajı; kullanıcı adı alanı doldurulmuş kalır, şifre alanı boşalır.
  - **Eksik alan:** alanlardan biri boşsa "Kullanıcı adı ve şifre gerekli." mesajı.
  - **Başarılı:** istenen sayfa açılır; menüde kullanıcının adı görünür.
  - **Çıkış yapıldı:** giriş ekranı, "Çıkış yapıldı." bilgisiyle.
- Design reference: none — the flow above is the design. Görünüm bugünkü sayfalarla aynı sade stil.
- Accessibility: alanların görünür etiketleri var (`Kullanıcı adı`, `Şifre`); form klavyeyle doldurulup Enter ile gönderilebilir; şifre alanı karakterleri gizler.

## Constraints & out of scope
- Kararlar (yagmur.cilek, 2026-11-04, analistin önerileriyle):
  - Giriş, uygulamaya özel kullanıcı adı ve şifreyle yapılır. **Varsayım:** şirketin ortak bir giriş sistemi (Active Directory, Microsoft 365 vb.) kullanılmıyor. BT böyle bir sistem bildirirse bu spec R-08 ile revize edilir.
  - Her hesap bir personele bağlıdır; İK rolü bu hesabın üstüne eklenen bir yetki olacaktır (spec 0004).
  - Veri bugünkü gibi bellekte kalır. Uygulama yeniden başladığında açık oturumlar düşer. Kalıcı veritabanı ayrı bir ADR'nin konusudur.
- Spec 0001'in karakterizasyon testleri **assert'leri değişmeden** yeşil kalır; testlerin giriş yapmış bir kullanıcı olarak çalıştırılması kabul edilir (`docs/testing.md`, korumalı testler).
- Spec 0002'nin davranışı (kaçışlama, debug kapalı) korunur. Giriş ekranındaki kullanıcı adı da düz metin olarak basılır.
- Kapsam dışı: rol bazlı görünürlük ve talep girme yetkisi (0004), onay ve red ekranı (0005), hesap yönetimi ekranı, şifre sıfırlama ve "beni hatırla", çok faktörlü giriş, hatalı denemelerde hesap kilitleme, oturum zaman aşımı süresinin ayarlanması.
- Split: proposed (a) 0003 giriş ve oturum, (b) 0004 rol bazlı görünürlük ve talep yetkisi, (c) 0005 onay ve red ekranı; split applied — yagmur.cilek, 2026-11-04: tek spec 25+ kriter olurdu; giriş, yetki ve onay ayrı yetenekler.

## Acceptance criteria
- [ ] AC-1 — Giriş yapmamış bir kullanıcı ana sayfayı, talep listesini ya da yeni talep formunu açtığında giriş ekranına yönlendirilir; yanıtta hiçbir personel adı ya da izin verisi yer almaz.
- [ ] AC-2 — Giriş yapmamış bir kullanıcının gönderdiği yeni talep formu talep oluşturmaz ve giriş ekranına yönlendirilir.
- [ ] AC-3 — Doğru kullanıcı adı ve şifreyle giriş yapan kullanıcı, girişten önce açmak istediği sayfaya (yoksa ana sayfaya) yönlendirilir ve menüde bağlı olduğu personelin adını görür.
- [ ] AC-4 — Yanlış şifre ve var olmayan kullanıcı adı **aynı** "Kullanıcı adı veya şifre hatalı." mesajını verir; kullanıcı giriş yapmamış kalır, kullanıcı adı alanı dolu, şifre alanı boştur.
- [ ] AC-5 — Kullanıcı adı ya da şifre boş gönderildiğinde "Kullanıcı adı ve şifre gerekli." mesajı gösterilir ve giriş yapılmaz.
- [ ] AC-6 — Giriş sonrası yönlendirme yalnızca uygulamanın kendi sayfalarına yapılır; giriş formuna verilen dış bir adres (ör. `https://kotu.example`) yok sayılır ve ana sayfaya gidilir.
- [ ] AC-7 — Çıkış yapan kullanıcı "Çıkış yapıldı." bilgisiyle giriş ekranına döner; ardından açtığı her sayfa yeniden giriş ister.
- [ ] AC-8 — Bağlı olduğu personel kaydı bulunmayan bir hesapla giriş yapılamaz; AC-4'teki genel mesaj gösterilir.
- [ ] AC-9 — Şifreler bellekte açık metin olarak tutulmaz; başarılı ya da hatalı giriş sırasında yazılan loglarda ve sayfalarda şifre yer almaz.
- [ ] AC-10 — Gizli anahtar tanımlı değilken uygulama başlatılmak istendiğinde başlamaz ve gizli anahtarın eksik olduğunu söyleyen bir mesaj verir (anahtarın değeri hiçbir zaman yazdırılmaz).

## Definition of Done
- [ ] Every acceptance criterion mapped to proof (test or reproducible observation)
- [ ] `scripts/check` green
- [ ] Independent review done; real findings fixed, noise rejected with written rationale
- [ ] Docs / ADRs updated if behavior or architecture changed
- [ ] Spec moved to `specs/done/` (it becomes immutable there)

## Scorecard (fill at ship — honest numbers make the process improvable)
| Metric | Value |
|---|---|
| Spec revisions | |
| Fix rounds | |
| Review findings: real / noise | |
| Regressions introduced | |
| Bugs escaped to production | |
