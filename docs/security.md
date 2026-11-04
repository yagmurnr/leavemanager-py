# Security

Uygulama yalnızca şirket içinde kullanılır ve internete açılmaz. Veri, kişisel veridir (KVKK):
çalışan adı, izin nedeni (ör. "Sağlık") hassas sayılır.

## Secrets
- Secrets never enter the repo, specs, prompts, or chat. `.env` is gitignored; provide `.env.example`.
- Agents never print secret values, even when debugging.
- Flask `SECRET_KEY` (oturum eklendiğinde) ortam değişkeninden okunur, koda yazılmaz.

## Input & output
- Formdan gelen her değer sınırda (`web`) doğrulanır: personel var mı, tarih biçimi geçerli mi, bitiş ≥ başlangıç mı, neden alanı uzunluk sınırını aşıyor mu?
- Bütün HTML, Jinja şablonlarıyla ve **autoescape açık** olarak üretilir. Kullanıcı verisini string
  birleştirerek HTML'e koymak, `|safe` ya da `Markup` kullanmak yasaktır (review'da kontrol edilir).
- Hata mesajlarında stack trace, iç hata kodu, dosya yolu ya da kişisel veri gösterilmez.
- Debug modu yalnızca bir ortam değişkeniyle (ör. `FLASK_DEBUG=1`) ve sadece geliştirici makinesinde açılır; kodda `debug=True` yasaktır (ruff `S201`).
- **Bilinen açıklar (bugünkü `app.py`):**
  1. ~~**Kayıtlı XSS**~~ — kapatıldı (spec 0002): sayfalar `templates/` altındaki autoescape'li şablonlardan üretiliyor.
  2. ~~**`debug=True` kalıcı**~~ — kapatıldı (spec 0002): debug yalnızca `FLASK_DEBUG=1` ile açılıyor; beklenmeyen hata genel bir sayfa gösteriyor. `S201` taban çizgisinden silindi.
  3. **Kimlik doğrulama** — giriş eklendi (spec 0003); rol bazlı yetki hâlâ yok (spec 0004, aşağıda).

  Her biri bir spec ile kapatılır. Kapatılana kadar uygulama `localhost` dışına açılmaz.
  Hata mesajındaki iç kod ve dahili telefon (`ERR-412 … dahili 4127`) hâlâ duruyor; `docs/domain.md` OD-7 ile kapanır.

## AuthN / AuthZ
- **Bugün (spec 0003):** giriş zorunlu. Giriş ekranı dışındaki her sayfa oturum ister. Hesaplar
  `LEAVEMANAGER_USERS` ortam değişkeninin gösterdiği JSON dosyasında, şifreler yalnızca hash olarak
  (`flask --app app hash-password`) tutulur; dosya depoya girmez (`users.json` gitignore'da,
  biçim `users.example.json`). Oturum çerezi `HttpOnly` ve `SameSite=Lax`; `SECRET_KEY` yoksa
  `python app.py` başlamaz. Hatalı giriş loglanır, kullanıcı adı ve şifre loglanmaz.
- **Henüz yok:** rol bazlı yetki. Giriş yapan herkes bütün verileri görür ve herkes adına talep
  girebilir (spec 0004). Formlarda CSRF token'ı yok; `SameSite=Lax` başka siteden gelen POST'a
  oturum çerezini eklemez, tam koruma 0004'e önerildi.
- **Hedef (ilk özellik adayı):** varsayılan olarak her şey reddedilir. Personel yalnızca kendi
  talebini görür ve girer; İK bütün talepleri ve bakiyeleri görür; onaylama ve reddetme yalnızca İK
  rolüyle yapılır. Yetki kontrolü `service` katmanında yapılır; yalnızca arayüzde bir butonu gizlemek yeterli değildir.

## Dependencies
- Yeni bir bağımlılık spec'in planında gerekçesiyle önerilir ve plan onayında insan tarafından onaylanır. Framework seviyesindeki bağımlılıklar ADR ister (`docs/architecture.md`).
- Kontrol edilecekler: lisans (MIT, BSD, Apache gibi izin verici bir lisans), son 12 ayda bakım görmüş olması, bilinen CVE'ler (`pip-audit`).
- Sürümler `requirements*.txt` dosyalarında `==` ile sabitlenir.

## Review lens
Security is a mandatory dimension of every independent review (see `prompts/review.md`), not a
separate afterthought phase.
