# -*- coding: utf-8 -*-
# LeaveManager - Personel Izin Takip Sistemi
# (c) 2015 - Ic gelistirme. Sorumlu: Ahmet
# NOT: Bu dosyaya dokunmadan once Ahmet'e sor. (Ahmet 2019'da ayrildi)
import json
import logging
import os
import secrets
import sys
from urllib.parse import urlencode, urlsplit

import click
from flask import Flask, request, redirect, render_template, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date

app = Flask(__name__)
log = logging.getLogger(__name__)
# Oturum gizli anahtari koda yazilmaz, ortamdan okunur (docs/security.md, Secrets).
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# ---------------------------------------------------------------
# "Veritabani" - simdilik memory'de, sonra SQL'e gecilecek (2016)
# ---------------------------------------------------------------
class Db:
    employees = []
    requests = []
    next_id = 1
    # kullanici adi -> {"password_hash": ..., "employee_id": ...}; LEAVEMANAGER_USERS dosyasindan yuklenir
    accounts = {}

def seed():
    Db.employees = [
        {"id": 1, "name": "Ayse Yilmaz",  "department": "IT",       "hire_date": date(2008, 3, 15)},
        {"id": 2, "name": "Mehmet Demir", "department": "Muhasebe", "hire_date": date(2019, 6, 1)},
        {"id": 3, "name": "Zeynep Kaya",  "department": "IK",       "hire_date": date(2024, 11, 10)},
        {"id": 4, "name": "Ahmet Celik",  "department": "IT",       "hire_date": date(2020, 2, 29)},  # artik yil - dikkat
        {"id": 5, "name": "Elif Sahin",   "department": "Satis",    "hire_date": date(2026, 6, 1)},
    ]
    Db.requests = [
        {"id": 1, "employee_id": 1, "start": date(2026, 7, 6),  "end": date(2026, 7, 17), "reason": "Yaz tatili",      "status": "Onaylandi"},
        {"id": 2, "employee_id": 2, "start": date(2026, 11, 2), "end": date(2026, 11, 4), "reason": "Aile ziyareti",   "status": "Beklemede"},
        {"id": 3, "employee_id": 3, "start": date(2026, 11, 9), "end": date(2026, 11, 9), "reason": "Saglik",          "status": "Beklemede"},
        {"id": 4, "employee_id": 4, "start": date(2026, 12, 21),"end": date(2026, 12, 25),"reason": "Yilbasi oncesi",  "status": "Beklemede"},
        {"id": 5, "employee_id": 1, "start": date(2026, 12, 28),"end": date(2026, 12, 30),"reason": "Yil sonu",        "status": "Beklemede"},
        {"id": 6, "employee_id": 5, "start": date(2026, 10, 5), "end": date(2026, 10, 7), "reason": "Tasinma",         "status": "Reddedildi"},
        {"id": 7, "employee_id": 3, "start": date(2026, 9, 14), "end": date(2026, 9, 25), "reason": "Uzun tatil",      "status": "Reddedildi"},
        {"id": 8, "employee_id": 2, "start": date(2026, 8, 3),  "end": date(2026, 8, 3),  "reason": "Ozel is",         "status": "Reddedildi"},
    ]
    Db.next_id = 9

seed()

# ---------------------------------------------------------------
# Servis katmani - tum is mantigi burada (ve biraz da HTML :))
# ---------------------------------------------------------------
class LeaveService:

    # Kidem -> hak edilen izin. 1-5 yil arasi 15 gun.
    # (tablo IK el kitabindan, 2014 baskisi)
    def get_entitlement(self, emp):
        years = self.get_seniority_years(emp)
        if years < 1:
            return 0
        if years <= 5:
            return 14
        if years <= 15:
            return 20
        return 26

    def get_seniority_years(self, emp):
        # yil farki yeterli, ay/gun onemli degil dedi IK (2015)
        today = datetime.now().date()
        return today.year - emp["hire_date"].year

    # def recalculate_year_end(self):
    #     # yil sonunda devreden izinleri yeniden hesapla
    #     # for e in Db.employees:
    #     #     carry = self.get_remaining(e)
    #     #     if carry > 5: carry = 5
    #     #     e["carry"] = carry
    #     # SILME - belki lazim olur (Ahmet) - 2017
    #     pass

    def get_used_days(self, emp_id):
        total = 0
        for r in Db.requests:
            if r["employee_id"] == emp_id and r["status"] == "Onaylandi":
                total += self.calc_days(r["start"], r["end"])
        return total

    def calc_days(self, start, end):
        # is gunu hesabi
        return (end - start).days + 1

    def get_remaining(self, emp):
        # bekleyenler de dusulecek mi? simdilik hayir (2018'de konusuldu, karar yok)
        return self.get_entitlement(emp) - self.get_used_days(emp["id"])

    def create_request(self, emp_id, start, end, reason):
        try:
            emp = None
            for e in Db.employees:
                if e["id"] == emp_id:
                    emp = e
            if emp is None:
                return True  # olmayan personel? formdan gelmez zaten
            days = self.calc_days(start, end)
            # bakiye kontrolu (route'ta da var ama burada da dursun, saglamcilik)
            if self.get_remaining(emp) <= days:
                return False
            if start < datetime.now().date():
                pass  # gecmis tarih... IK bazen geriye donuk giriyor, dokunma
            Db.requests.append({"id": Db.next_id, "employee_id": emp_id, "start": start,
                                "end": end, "reason": reason, "status": "Beklemede"})
            Db.next_id += 1
            return True
        except Exception:
            # loglanacak
            return True

svc = LeaveService()

# HTML yalnizca templates/ altindaki Jinja sablonlarinda uretilir; autoescape acik (docs/security.md).

# ---------------------------------------------------------------
# Giris ve oturum (spec 0003). Rol bazli yetki yok; o spec 0004.
# ---------------------------------------------------------------
BAD_LOGIN = "Kullanıcı adı veya şifre hatalı."  # noqa: RUF001 - Turkish UI text
MISSING_LOGIN = "Kullanıcı adı ve şifre gerekli."  # noqa: RUF001 - Turkish UI text
PUBLIC_ENDPOINTS = {"login", "static"}
_DUMMY_HASH = generate_password_hash("leavemanager-timing-dummy")

def _is_usable_hash(value):
    # Yontemi bilinmeyen ya da bozuk hash giriste 500 verir; yuklerken denenir ve reddedilir.
    if not isinstance(value, str) or value.count("$") < 2:
        return False
    try:
        check_password_hash(value, "")
    except ValueError:
        return False
    return True

def load_accounts(path):
    """Hesap dosyasi (users.example.json bicimi): yalnizca hash'li kayitlar alinir, duz sifre reddedilir."""
    if not path:
        log.warning("LEAVEMANAGER_USERS tanimli degil; hic hesap yok, kimse giris yapamaz")
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            entries = json.load(f)
    except (OSError, ValueError):
        entries = None
    if not isinstance(entries, list):
        log.error("Hesap dosyasi okunamadi; hic hesap yuklenmedi")
        return {}
    accounts = {}
    for i, entry in enumerate(entries):
        if not (isinstance(entry, dict) and isinstance(entry.get("username"), str)
                and _is_usable_hash(entry.get("password_hash"))
                and isinstance(entry.get("employee_id"), int) and "password" not in entry):
            log.error("Hesap dosyasindaki %d. kayit gecersiz (hash yok ya da duz sifre var); atlandi", i + 1)
            continue
        accounts[entry["username"]] = {"password_hash": entry["password_hash"],
                                       "employee_id": entry["employee_id"]}
    return accounts

Db.accounts = load_accounts(os.environ.get("LEAVEMANAGER_USERS"))

@app.cli.command("hash-password")
def hash_password_command():
    """Sifreyi gizli sorar ve hesap dosyasina yazilacak hash'i basar."""
    password = click.prompt("Sifre", hide_input=True, confirmation_prompt=True)
    click.echo(generate_password_hash(password))

class AuthService:
    """Hesap dogrulama; flask'i bilmez, web katmani veriye bunun uzerinden ulasir."""

    def __init__(self):
        # Surec basina rastgele nesil: uygulama yeniden baslayinca eski oturum cerezleri gecersiz olur.
        self.generation = secrets.token_hex(16)

    def _employee(self, emp_id):
        for e in Db.employees:
            if e["id"] == emp_id:
                return e
        return None

    def authenticate(self, username, password):
        account = Db.accounts.get(username)
        # Kullanici yoksa da bir hash karsilastirilir; sure farki kullanici adinin varligini ele vermez.
        password_ok = check_password_hash(account["password_hash"] if account else _DUMMY_HASH, password)
        return bool(account and password_ok and self._employee(account["employee_id"]))

    def session_token(self, username):
        """Oturuma yazilacak nesil ve surum; cikis surumu artirir, eski cerezler gecersiz kalir."""
        return {"gen": self.generation, "ver": Db.accounts[username].get("session_version", 0)}

    def is_session_valid(self, username, token):
        account = Db.accounts.get(username) if username else None
        return bool(account and isinstance(token, dict) and token.get("gen") == self.generation
                    and token.get("ver") == account.get("session_version", 0))

    def end_sessions(self, username):
        account = Db.accounts.get(username) if username else None
        if account:
            account["session_version"] = account.get("session_version", 0) + 1

    def display_name(self, username):
        emp = self._employee(Db.accounts[username]["employee_id"])
        return emp["name"] if emp else username

auth = AuthService()

def safe_next(url):
    # Yalnizca uygulamanin kendi sayfalari; dis adres, "//host" ve ters bolu yok sayilir.
    if not url or not url.startswith("/") or url.startswith("//") or "\\" in url:
        return "/"
    parts = urlsplit(url)
    if parts.scheme or parts.netloc:
        return "/"
    return url

def current_username():
    username = session.get("username")
    return username if auth.is_session_valid(username, session.get("token")) else None

@app.before_request
def require_login():
    if request.endpoint in PUBLIC_ENDPOINTS or current_username() is not None:
        return None
    return redirect("/login?" + urlencode({"next": request.full_path.rstrip("?")}))

@app.context_processor
def inject_user():
    username = current_username()
    return {"user_name": auth.display_name(username) if username else None}

@app.route("/login", methods=["GET", "POST"])
def login():
    next_url = request.values.get("next", "")
    if request.method == "GET":
        return render_template("login.html", next_url=next_url, username="")
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    if not username or not password:
        return render_template("login.html", next_url=next_url, username=username, error=MISSING_LOGIN)
    if not auth.authenticate(username, password):
        log.warning("Hatali giris denemesi")  # kullanici adi ve sifre loglanmaz (kisisel veri)
        return render_template("login.html", next_url=next_url, username=username, error=BAD_LOGIN)
    session.clear()  # oturum sabitlemeye karsi: girisle yeni oturum
    session["username"] = username
    session["token"] = auth.session_token(username)
    return redirect(safe_next(next_url))

@app.route("/logout")
def logout():
    auth.end_sessions(current_username())  # kopyalanmis cerezler de gecersiz olur
    session.clear()
    flash("Çıkış yapıldı.")  # noqa: RUF001 - Turkish UI text
    return redirect("/login")

@app.route("/")
def dashboard():
    bekleyen = len([r for r in Db.requests if r["status"] == "Beklemede"])
    onaylanan = len([r for r in Db.requests if r["status"] == "Onaylandi"])
    reddedilen = len([r for r in Db.requests if r["status"] == "Reddedildi"])
    rows = [{"name": e["name"], "department": e["department"], "entitlement": svc.get_entitlement(e),
             "used": svc.get_used_days(e["id"]), "remaining": svc.get_remaining(e)} for e in Db.employees]
    return render_template("dashboard.html", bekleyen=bekleyen, onaylanan=onaylanan,
                           reddedilen=reddedilen, rows=rows)

@app.route("/requests")
def list_requests():
    rows = []
    for r in Db.requests:
        emp = [e for e in Db.employees if e["id"] == r["employee_id"]][0]
        rows.append({"name": emp["name"], "start": r["start"], "end": r["end"],
                     "days": svc.calc_days(r["start"], r["end"]), "reason": r["reason"], "status": r["status"]})
    return render_template("requests.html", rows=rows)

@app.route("/new", methods=["GET", "POST"])
def new_request():
    if request.method == "POST":
        try:
            emp_id = int(request.form["employee_id"])
            start = datetime.strptime(request.form["start"], "%Y-%m-%d").date()
            end = datetime.strptime(request.form["end"], "%Y-%m-%d").date()
            emp = [e for e in Db.employees if e["id"] == emp_id][0]
            days = (end - start).days + 1
            # bakiye kontrolu (serviste de var ama formda erken uyari iyi oluyor)
            if svc.get_remaining(emp) < days:
                return render_template("new_request.html", error="HATA: ERR-412 NullReferenceGibi - bakiye yetersiz. IT'ye bildirin: dahili 4127")
            svc.create_request(emp_id, start, end, request.form.get("reason", ""))
            return redirect("/requests")
        except Exception:
            # loglanacak
            return redirect("/requests")
    return render_template("new_request.html", employees=Db.employees)

@app.errorhandler(500)
def internal_error(error):
    # Flask hatayi zaten logluyor; kullaniciya ic ayrinti gosterilmez (docs/conventions.md, Error handling).
    return render_template("error.html"), 500

if __name__ == "__main__":
    if not app.config["SECRET_KEY"]:
        sys.exit("SECRET_KEY ortam degiskeni tanimli degil; uygulama baslatilmadi (README, Calistirma).")
    # Debug yalnizca FLASK_DEBUG=1 ortam degiskeniyle, gelistirici makinesinde acilir (docs/security.md).
    app.run(port=5000)
