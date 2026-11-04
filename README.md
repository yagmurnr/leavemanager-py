# LeaveManager (Python/Flask)

Calistirma:

    pip install -r requirements.txt

1. Her kullanici icin sifre hash'i uretin (sifre gizli sorulur, ekrana yazilmaz):

       flask --app app hash-password

2. `users.example.json` dosyasini `users.json` olarak kopyalayin; her kullaniciya
   `username`, uretilen `password_hash` ve bagli oldugu personelin `employee_id` degerini yazin.
   `users.json` depoya girmez (`.gitignore`).

3. Gizli anahtar ve hesap dosyasiyla baslatin:

       SECRET_KEY=<uzun-rastgele-deger> LEAVEMANAGER_USERS=users.json python app.py

   `SECRET_KEY` yoksa uygulama baslamaz. Uretmek icin:
   `python -c "import secrets; print(secrets.token_hex(32))"`.
   `flask run` ile baslatma desteklenmez (gizli anahtar kontrolu `python app.py` icindedir).
   Debug yalnizca gelistirici makinesinde `FLASK_DEBUG=1` ile acilir.

Adres: http://localhost:5000 (yalnizca localhost; rol bazli yetki gelene kadar disari acilmaz).
