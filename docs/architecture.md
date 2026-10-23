# Architecture

## System overview
LeaveManager, şirket içi personel izin takip uygulamasıdır: personel izin talebi girer, İK talepleri
ve bakiyeleri izler. Tek süreçli bir Flask uygulamasıdır; hedef mimari **katmanlı monolit**tir
(`web` → `service` → `repository`). Gerekçe: küçük ekip ve tek uygulama için en ucuz, iş kurallarını
test edilebilir kılan ayrım ([ADR 0001](decisions/0001-layered-monolith.md)).

**Bugünkü durum (bootstrap, 2026-10-23):** her şey tek dosyada, `app.py` içinde. Katmanlar orada sınıf
olarak var ama sınırlar delik: `LeaveService.status_badge` HTML üretiyor; route'lar `Db`'ye doğrudan
erişiyor ve iş kuralını (bakiye kontrolü) tekrar ediyor. Veri bellekte duruyor ve her başlatmada
`seed()` ile sıfırlanıyor. Kodu katmanlara bölmek ayrı bir refactor spec'iyle yapılır
(`workflows/refactor.md`); o zamana kadar yeni kod hedef mimariye uyar.

## Modules / components and ownership

| Module | Single responsibility | Owns |
|---|---|---|
| `web` | HTTP route'ları, form okuma ve doğrulama, Jinja şablonlarıyla HTML üretimi | Sayfalar, form alanları, kullanıcıya gösterilen mesajlar |
| `service` | İş kuralları: hak, kıdem, gün sayımı, bakiye, talep oluşturma ve durum geçişleri | `docs/domain.md` içindeki BR-n kuralları |
| `repository` | Veriyi okuma ve yazma. Bugün bellekte; ileride bir veritabanı (ADR ile) | Personel ve izin talebi kayıtları |

## Communication rules
- Çağrı yönü tek yönlüdür: `web` → `service` → `repository`. Ters yönde ya da katman atlayarak çağrı yapılmaz.
- `web`, veriye yalnızca `service` üzerinden ulaşır.
- İş kuralı tek yerde, `service` içinde yaşar. `web` bir kuralı kopyalamaz; erken uyarı göstermesi gerekiyorsa `service`'e sorar.
- Olay, kuyruk ya da arka plan işi yoktur. Gerekirse ADR ile eklenir.

## Forbidden dependencies (make them testable)
- `service` ve `repository`, `flask`'ı import etmez ve HTML üretmez.
- `repository`, `service` ya da `web`'i import etmez.
- `web`, `repository`'yi doğrudan import etmez.
- Yeni bir framework, ORM, veritabanı ya da harici servis ancak kabul edilmiş bir ADR ile eklenir.
- `app.py` bugün bu kuralların bir kısmını ihlal ediyor (bkz. System overview). İhlaller refactor
  spec'iyle kapanır; yeni kod bu ihlalleri artıramaz.

## Deliberately out of scope
- Kalıcı veri saklama (veritabanı). Bugün bellekte; geçiş ayrı bir karar ve ADR gerektirir.
- Kimlik doğrulama ve yetkilendirme. İlk özellik adayı (`docs/security.md`).
- Talep onaylama ve reddetme ekranı. Kodda yok, durumlar yalnızca seed verisinde değişiyor.
- Resmi tatil takvimi, e-posta bildirimi, raporlama ve dışa aktarma.
- Devreden izin (`recalculate_year_end`, yorum satırında; bkz. `docs/domain.md` OD-8).
