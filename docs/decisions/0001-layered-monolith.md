# ADR 0001 — Katmanlı monolit: web → service → repository

- Status: Accepted
- Date: 2026-10-23

## Context
LeaveManager 2015'ten kalma, tek dosyalık (`app.py`) bir Flask uygulaması. İş kuralları, HTML ve veri
erişimi aynı dosyada iç içe: bakiye kontrolü iki yerde ve farklı biçimde yazılmış, servis katmanı HTML
üretiyor. Test yok. Değişiklik yapmadan önce iş kurallarını izole edip test edebilmemiz gerekiyor.
Ekip küçük, uygulama şirket içi ve tek süreçli.

## Decision
Uygulama tek süreçli bir monolit olarak kalır ve üç katmana ayrılır: `web` (HTTP ve şablonlar),
`service` (iş kuralları, Flask'tan bağımsız) ve `repository` (veri). Çağrı yönü tek yönlüdür.

## Consequences
- **Kazanç:** İş kuralları Flask olmadan unit test edilebilir. Kural tek yerde yaşar, tekrar ve
  çelişki (form `<`, servis `<=`) yapısal olarak önlenir. Veritabanına geçiş yalnızca `repository`'yi etkiler.
- **Maliyet:** Mevcut `app.py`'nin bölünmesi bir refactor spec'i ve karakterizasyon testleri ister.
  Bölünene kadar kod, belgelenen mimariye uymaz; bu fark `docs/architecture.md` içinde açıkça yazılı.

## Alternatives considered
- **Tek dosya olarak bırakmak:** Bugünkü sorunların (tekrarlanan kural, test edilemeyen mantık) kaynağı bu; reddedildi.
- **Modüler monolit veya servisler:** Tek bir alan (izin) ve küçük ekip için gereksiz karmaşıklık; reddedildi.

## Revisit triggers
- İzin dışında ikinci bir alan eklenmesi (ör. bordro, vardiya): modüler monolit düşünülür.
- Başka bir sistemin LeaveManager verisine API ile erişmesi gerekirse.
