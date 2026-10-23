# Conventions

## Language
<!-- Set at bootstrap (step 0) and mirrored in AGENTS.md. Changing it later is allowed — edit both
     places; existing documents are not translated retroactively. -->
- Chat language (interviews, sessions): Turkish
- Document language (docs/, specs, plans, ADRs, review and verify reports): Turkish
- Always English (protocol, not prose): ANEW core files, template headings and field labels,
  `Status:` values (Draft / Approved / In progress / Shipped), `Approved by / on:`, `Source:`.
- Code identifiers, branch names, commit messages: English. Kullanıcıya görünen arayüz metinleri ve
  domain değerleri (`Beklemede`, `Onaylandi`, `Reddedildi`) Türkçedir.
- Agent messages (handoff summaries, refusals, `Next:` lines): chat language; command names, file
  paths and protocol fields verbatim.

## Language & framework versions
- Python 3.14, Flask 3.1 (`requirements.txt`). Geliştirme araçları `requirements-dev.txt` içinde sabitlenmiş sürümlerle durur.
- Kurulum: `"$(scripts/py)" -m pip install -r requirements-dev.txt`. Proje içinde `.venv` varsa
  `scripts/py` onu kullanır; tavsiye edilen kurulum budur.
- Python'u her yerde `scripts/py` ile çağırın. Windows'ta `python` komutu Microsoft Store kısayoluna gidebilir.

## Naming
- PEP 8: modül, fonksiyon ve değişken `snake_case`; sınıf `PascalCase`; sabit `UPPER_CASE`.
- Domain terimleri `docs/domain.md` tablosundaki İngilizce karşılıklarıyla adlandırılır (`employee`, `leave_request`, `entitlement`, `remaining`).
- Testler: `tests/test_<modül>.py`, `test_<davranış>` (ör. `test_entitlement_is_14_days_for_1_to_5_years`).

## Error handling
- Hatalar sessizce yutulmaz. `except Exception: pass/return` yasaktır (ruff `BLE001`).
- Beklenen hata (geçersiz form, yetersiz bakiye) kullanıcıya anlaşılır bir Türkçe mesajla gösterilir; işlem başarılı gibi davranılmaz.
- Beklenmeyen hata `logging` ile loglanır. Kullanıcıya genel bir mesaj gösterilir; stack trace, iç hata kodu ya da dahili telefon numarası gösterilmez.
- `service`, hata durumunu `True`/`False` dönüşle değil, adı konmuş bir istisnayla ya da açık bir sonuç nesnesiyle bildirir.
- Bugünkü `app.py` bu kurala uymuyor (`docs/domain.md` OD-7). Kural yeni kod için geçerli.

## Data rules
- Tarihler `datetime.date`, zaman damgaları `datetime` tipindedir. Formdan `YYYY-MM-DD` biçiminde okunur.
  "Bugün", test edilebilsin diye tek bir yerden alınır (enjekte edilebilir bir saat).
- Gün sayıları tam sayıdır (`int`); yarım gün izin yoktur.
- Kimlikler (ID) tam sayıdır ve `repository` tarafından üretilir.
- Durum değerleri yalnızca `docs/domain.md`'de listelenen üç değerdir; serbest metin değildir.
- Kişisel veri (ad, sağlık nedeni vb.) loglara yazılmaz (`docs/security.md`).

## Enforced by tooling
- `ruff check .` (`ruff.toml`; `./scripts/check` içinde): pyflakes (F), sözdizimi ve import hataları (E4/E7/E9, W),
  import sırası (I), modern Python (UP), olası hatalar (B), kör `except` (BLE), güvenlik (S; ör. `debug=True`), Ruff kuralları (RUF).
- **Taban çizgisi:** `app.py`'nin bootstrap anındaki bulguları `ruff.toml` içinde dosya bazında muaf tutulur.
  Liste yalnızca kısalır: `app.py`'ye dokunan bir spec düzelttiği kuralı listeden siler. Listeye ekleme yapmak bir ADR gerektirir.
- Review'da kontrol edilenler (tooling'de yok): katman sınırları (`docs/architecture.md`), hata mesajları, Jinja autoescape kullanımı.
