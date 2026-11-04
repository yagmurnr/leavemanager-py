# Spec 0001 — İş kuralları için karakterizasyon testleri (BR-1…BR-10)

- Status: In progress
- Mode: lite
- Plan: `specs/plans/0001-plan.md`

## Intent
Ekip, LeaveManager'ın izin kurallarını değiştirmeden önce bir güvenlik ağı istiyor. Bugün hiç test
yok ve sekiz açık kararın (OD-1…OD-8) her biri ileride bir değişiklik talebi olacak. Bu iş, uygulamanın
**bugünkü** davranışını, hataları ve tutarsızlıkları dahil olmak üzere, otomatik testlerle sabitler.
Böylece sonraki her değişiklik neyi bilerek değiştirdiğini, neyi yanlışlıkla bozduğunu gösterebilir.
Başarı: `docs/domain.md` içindeki her BR-n en az bir testle korunur ve testler `./scripts/check` içinde
koşar. Bilerek yapılmayan: hiçbir davranış düzeltilmez, hiçbir açık karar kapatılmaz, uygulama kodu değişmez.

## Requirements
- R-1: Testler bugünkü davranışı gözlemlendiği gibi doğrular; davranışın "olması gereken" hali test edilmez. Hatalı görünen davranış (BR-7, BR-10) da olduğu gibi sabitlenir.
- R-2: `app.py` bu iş kapsamında değiştirilmez. Testler uygulamayı olduğu gibi kullanır.
- R-3: Testler gerçek saate bağlı değildir. "Bugün" her testte sabit ve bilinen bir tarihtir; testler hangi gün çalıştırılırsa çalıştırılsın aynı sonucu verir.
- R-4: Her test bilinen bir veri durumuyla başlar ve bıraktığı veri bir sonraki testi etkilemez.
- R-5: Testler iş kurallarını hem kuralın kendisi seviyesinde (hak, kıdem, gün, kullanılan, kalan) hem de kullanıcının talep girdiği akış seviyesinde (form gönderimi) doğrular. BR-6 ile BR-7 arasındaki fark yalnızca akış seviyesinde görünür.
- R-6: Testler `./scripts/check` içinde, hızlı profilde de koşar.
- R-7: Her test adı, koruduğu kuralı (BR-n) ya da açık kararı (OD-n) anar; kırmızıya düşen bir test hangi kuralın değiştiğini söyler.

## User experience
none — no user interface

## Constraints & out of scope
- Kapsam dışı: OD-1…OD-8'in herhangi birini düzeltmek ya da karara bağlamak; XSS ve `debug=True` düzeltmesi; kodu katmanlara bölmek (ayrı refactor spec'i).
- Kapsam dışı: seed verisinin kendisi (demo verisidir, kural değildir).
- Kapsam dışı: arayüz görünümü, HTML yapısı ve stil testleri. Sayfalar yalnızca sonuçları (yönlendirme, hata mesajı, kayıt oluşup oluşmadığı) üzerinden doğrulanır.
- Yeni bir çalışma zamanı bağımlılığı eklenmez. Test için gereken araç `requirements-dev.txt` içinde sabit sürümüyle durur.
- Testler sunucu açmaz ve arka planda süreç bırakmaz (`docs/testing.md`, Resource hygiene).
- Split: proposed (a) kural seviyesi BR-1…BR-5, (b) talep akışı BR-6…BR-10 ve hata durumları; kept as one — yagmur.cilek, 2026-10-23: tek kullanıcı yeteneği yok, sadece test ekleniyor; ayrı spec maliyeti kazançtan büyük.

## Acceptance criteria
Sabit "bugün" = **2026-10-23** (aksi belirtilmedikçe).

- [x] AC-1 — BR-1 Hak: kıdem 0 → 0 gün; 1 ve 5 → 14 gün; 6 ve 15 → 20 gün; 16 ve 30 → 26 gün.
- [x] AC-2 — BR-2 Kıdem: işe giriş 2025-12-31 olan personelin kıdemi 2026-01-01'de 1 yıldır; işe giriş 2026-12-31 ve bugün 2026-01-01 iken kıdem 0'dır; işe giriş 2020-02-29 (artık yıl) olan personelin kıdemi 2026-10-23'te 6'dır ve hata vermez.
- [x] AC-3 — BR-3 Gün sayımı: aynı gün başlayıp biten talep 1 gün; 2026-11-06 (Cuma) → 2026-11-09 (Pazartesi) 4 gün (hafta sonu düşülmez); bitiş başlangıçtan bir gün önceyse 0 gün.
- [x] AC-4 — BR-4 Kullanılan: aynı personelin `Onaylandi`, `Beklemede` ve `Reddedildi` talepleri varken yalnızca `Onaylandi` olanların günleri toplanır; hiç onaylı talebi olmayan personelde 0'dır.
- [x] AC-5 — BR-5 Kalan: Hak − Kullanılan; kullanılan haktan büyükse kalan negatiftir (ör. hak 0, kullanılan 3 → −3).
- [x] AC-6 — BR-6 Form bakiye kontrolü: talep günü kalandan 1 fazlaysa talep kaydedilmez ve sayfada "bakiye yetersiz" ifadesini içeren bir hata mesajı gösterilir (mesajın geri kalanı OD-7 kapsamında değişeceği için sabitlenmez).
- [x] AC-7 — BR-7 Servis bakiye kontrolü: talep günü kalana **eşitse** talep kaydedilmez, hata gösterilmez ve kullanıcı talep listesine yönlendirilir. Talep günü kalandan 1 azsa talep kaydedilir. (OD-4)
- [x] AC-8 — BR-8 Yeni talep: başarılı bir form gönderimi, girilen personel, tarihler ve nedenle `Beklemede` durumunda yeni bir talep oluşturur ve talep listesine yönlendirir.
- [x] AC-9 — BR-9 Geçmiş tarih: başlangıcı bugünden önce olan bir talep (bakiye yeterliyse) kabul edilir ve kaydedilir.
- [x] AC-10 — BR-10 Ters aralık: kalanı pozitif olan bir personel için bitişi başlangıçtan önce olan bir talep kabul edilir ve kaydedilir. (OD-6)
- [x] AC-11 — OD-7 Hata davranışı: olmayan bir personel ya da geçersiz tarih biçimiyle yapılan form gönderimi talep oluşturmaz, hata göstermez ve talep listesine yönlendirir.
- [x] AC-12 — Testler `./scripts/check` ve `./scripts/check --fast` içinde koşar. İkisi de yeşil ve test sayısını gösterir; residue testi temiz.
- [x] AC-13 — Testler iki farklı gerçek tarihte (ör. sistem saati bugün ve 2027-03-01 gibi davranırken) aynı sonucu verir: "bugün" sabitlenmeden kalan bir test yoktur. Kanıt: test takımı farklı bir sabit "bugün" ile bir kez daha çalıştırılabilir ve tarihe bağlı olmayan testler aynı sonucu verir; plan bunun yolunu tanımlar, mümkün değilse kanıt review'da kod incelemesidir.

## Definition of Done
- [x] Every acceptance criterion mapped to proof (test or reproducible observation)
- [x] `scripts/check` green
- [x] Independent review done; real findings fixed, noise rejected with written rationale
- [x] Docs / ADRs updated if behavior or architecture changed
- [ ] Spec moved to `specs/done/` (it becomes immutable there)

## Scorecard (fill at ship — honest numbers make the process improvable)
| Metric | Value |
|---|---|
| Spec revisions | 0 (spec onaydan sonra yalnızca Status değişti) |
| Fix rounds | 1 (`[plan 0001/fix-1]`; round 2 review fix diff üzerinde, yeni düzeltme yok) |
| Review findings: real / noise | 2 / 2 (F-1, F-2 / F-3, F-4) |
| Regressions introduced | 0 (`app.py` değişmedi; 19/19 mutasyon testleri kırmızıya düşürdü) |
| Bugs escaped to production | |
