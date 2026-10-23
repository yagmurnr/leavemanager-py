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
  1. **Kayıtlı XSS:** talepteki "Neden" alanı, personel adı ve diğer veriler escape edilmeden basılıyor (`body|safe`).
  2. **`debug=True` kalıcı:** ağdan erişilebilirse Werkzeug debugger üzerinden uzaktan kod çalıştırma riski var.
  3. **Kimlik doğrulama yok** (aşağıda).

  Her biri bir spec ile kapatılır. Kapatılana kadar uygulama `localhost` dışına açılmaz.

## AuthN / AuthZ
- **Bugün:** kimlik doğrulama yok. Sayfaya ulaşabilen herkes, herhangi bir personel adına talep girebilir.
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
