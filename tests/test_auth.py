"""Spec 0003: login and session (AC-1…AC-10)."""

import json
import logging
import runpy
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import flask
import pytest
from werkzeug.security import generate_password_hash

import app
from tests.conftest import add_employee
from tests.html_text import visible_text

PASSWORD = "Dogru-Sifre-123"  # noqa: S105 - test credential
WRONG = "yanlis-sifre"
BAD_LOGIN = "Kullanıcı adı veya şifre hatalı."  # noqa: RUF001 - Turkish dotless i on purpose
MISSING = "Kullanıcı adı ve şifre gerekli."  # noqa: RUF001 - Turkish dotless i on purpose


def add_account(username="ayse", password=PASSWORD, employee_id=1):
    # Cheap hash settings keep the suite fast; the app's own hashing is checked in AC-9.
    app.Db.accounts[username] = {"password_hash": generate_password_hash(password, "pbkdf2:sha256:1000"),
                                 "employee_id": employee_id}


def _login(client, username="ayse", password=PASSWORD, next_url=None):
    data = {"username": username, "password": password}
    if next_url is not None:
        data["next"] = next_url
    return client.post("/login", data=data)


def _location(resp):
    loc = urlparse(resp.headers["Location"])
    return loc.netloc, loc.path


def _is_logged_in(client):
    return client.get("/").status_code == 200


@pytest.mark.parametrize("path", ["/", "/requests", "/new"])
def test_ac1_anonymous_is_redirected_to_login_without_data(anon_client, path):
    app.seed()
    resp = anon_client.get(path)
    assert resp.status_code == 302
    assert _location(resp) == ("", "/login")
    body = resp.get_data(as_text=True)
    for e in app.Db.employees:
        assert e["name"] not in body


def test_ac2_anonymous_form_post_creates_no_request(anon_client):
    add_employee(emp_id=1, hire_date=date(2019, 6, 1))
    resp = anon_client.post("/new", data={"employee_id": "1", "start": "2026-11-02", "end": "2026-11-02",
                                          "reason": "x"})
    assert resp.status_code == 302
    assert _location(resp) == ("", "/login")
    assert app.Db.requests == []


def test_ac3_login_returns_to_requested_page_and_shows_name(anon_client):
    add_employee(emp_id=1, name="Ayşe Yılmaz")  # noqa: RUF001 - Turkish dotless i on purpose
    add_account()
    first = anon_client.get("/requests")
    login_page = anon_client.get(first.headers["Location"])
    assert login_page.status_code == 200
    resp = _login(anon_client, next_url="/requests")
    assert resp.status_code == 302
    assert _location(resp) == ("", "/requests")
    page = anon_client.get("/requests")
    assert page.status_code == 200
    assert "Ayşe Yılmaz" in visible_text(page.get_data(as_text=True))  # noqa: RUF001


def test_ac3_login_without_next_goes_home(anon_client):
    add_employee(emp_id=1)
    add_account()
    resp = _login(anon_client)
    assert _location(resp) == ("", "/")
    assert _is_logged_in(anon_client)


def test_ac4_wrong_password_and_unknown_user_give_same_message(anon_client):
    add_employee(emp_id=1)
    add_account()
    wrong = _login(anon_client, password=WRONG)
    unknown = _login(anon_client, username="olmayan")
    for resp in (wrong, unknown):
        assert resp.status_code == 200
        assert BAD_LOGIN in visible_text(resp.get_data(as_text=True))
    assert visible_text(wrong.get_data(as_text=True)) == visible_text(unknown.get_data(as_text=True))
    html = wrong.get_data(as_text=True)
    assert 'value="ayse"' in html  # username kept
    assert WRONG not in html  # password field emptied
    assert not _is_logged_in(anon_client)


@pytest.mark.parametrize(("username", "password"), [("", PASSWORD), ("ayse", ""), ("   ", PASSWORD)])
def test_ac5_empty_fields_are_rejected(anon_client, username, password):
    add_employee(emp_id=1)
    add_account()
    resp = _login(anon_client, username=username, password=password)
    assert resp.status_code == 200
    assert MISSING in visible_text(resp.get_data(as_text=True))
    assert not _is_logged_in(anon_client)


@pytest.mark.parametrize("next_url", ["https://kotu.example", "//kotu.example", "/\\kotu.example",
                                      "javascript:alert(1)"])
def test_ac6_external_next_is_ignored(anon_client, next_url):
    add_employee(emp_id=1)
    add_account()
    resp = _login(anon_client, next_url=next_url)
    assert resp.status_code == 302
    assert _location(resp) == ("", "/")


def test_ac7_logout_ends_session(anon_client):
    add_employee(emp_id=1)
    add_account()
    _login(anon_client)
    assert _is_logged_in(anon_client)
    resp = anon_client.get("/logout")
    assert _location(resp) == ("", "/login")
    page = anon_client.get("/login")
    assert "Çıkış yapıldı." in visible_text(page.get_data(as_text=True))  # noqa: RUF001
    for path in ("/", "/requests", "/new"):
        assert _location(anon_client.get(path)) == ("", "/login")


def _replay_cookie(cookie_value):
    other = app.app.test_client()
    other.set_cookie("session", cookie_value)
    return other


def test_ac7_copied_cookie_is_rejected_after_logout(anon_client):
    # Review F-1: logging out must end the session on the server, not only in this browser.
    add_employee(emp_id=1)
    add_account()
    _login(anon_client)
    stolen = anon_client.get_cookie("session").value
    assert _is_logged_in(_replay_cookie(stolen))  # the copy works while logged in ...
    anon_client.get("/logout")
    assert _location(_replay_cookie(stolen).get("/")) == ("", "/login")  # ... and not after logout


def test_sessions_end_when_app_restarts(anon_client, monkeypatch):
    # Spec 0003 Constraints: restarting the app drops open sessions (review F-1).
    add_employee(emp_id=1)
    add_account()
    _login(anon_client)
    assert _is_logged_in(anon_client)
    monkeypatch.setattr(app.auth, "generation", "a-new-process")
    assert _location(anon_client.get("/")) == ("", "/login")


def test_ac8_account_without_employee_cannot_log_in(anon_client):
    add_account(employee_id=42)  # no employee 42
    resp = _login(anon_client)
    assert resp.status_code == 200
    assert BAD_LOGIN in visible_text(resp.get_data(as_text=True))
    assert not _is_logged_in(anon_client)


# --- AC-9: passwords never stored or shown in plain text ---

def _hash_with_cli(password):
    result = app.app.test_cli_runner().invoke(args=["hash-password"], input=f"{password}\n{password}\n")
    assert result.exit_code == 0
    return result.output.strip().splitlines()[-1]


def test_ac9_passwords_stored_hashed(anon_client, tmp_path):
    add_employee(emp_id=1)
    hashed = _hash_with_cli(PASSWORD)
    assert PASSWORD not in hashed
    users = tmp_path / "users.json"
    users.write_text(json.dumps([
        {"username": "ayse", "password_hash": hashed, "employee_id": 1},
        {"username": "duz", "password": PASSWORD, "employee_id": 1},  # plain text: refused
        {"username": "ornek", "password_hash": "BURAYA: hash", "employee_id": 1},  # placeholder: refused
        {"username": "bozuk", "password_hash": "foo$bar$baz", "employee_id": 1},  # unknown method: refused
    ]), encoding="utf-8")
    app.Db.accounts = app.load_accounts(str(users))
    assert set(app.Db.accounts) == {"ayse"}
    assert PASSWORD not in json.dumps(app.Db.accounts)
    assert _location(_login(anon_client)) == ("", "/")
    assert _login(anon_client, username="duz").status_code == 200  # no such account


@pytest.mark.parametrize("content", ["5", "null", "{}", "\"metin\""])
def test_accounts_file_with_wrong_shape_loads_nothing_without_crashing(tmp_path, content):
    # Review F-3: a malformed file is logged and ignored (plan R8), never a crash at startup.
    users = tmp_path / "users.json"
    users.write_text(content, encoding="utf-8")
    assert app.load_accounts(str(users)) == {}


def test_ac9_password_not_in_logs_or_pages(anon_client, caplog):
    caplog.set_level(logging.DEBUG)
    add_employee(emp_id=1)
    add_account()
    bodies = [_login(anon_client, password=WRONG).get_data(as_text=True),
              _login(anon_client, username="olmayan").get_data(as_text=True)]
    _login(anon_client)
    bodies += [anon_client.get(p).get_data(as_text=True) for p in ("/", "/requests", "/new")]
    assert "Hatali giris" in caplog.text  # the failures are logged ...
    for secret in (PASSWORD, WRONG, "ayse", "olmayan"):
        assert secret not in caplog.text  # ... without username or password
    for body in bodies:
        assert PASSWORD not in body and WRONG not in body


# --- AC-10: no session key, no start ---

def _start_app_directly(monkeypatch):
    started = {}
    monkeypatch.setattr(flask.Flask, "run", lambda self, *a, **kw: started.setdefault("app", self))
    runpy.run_path(str(Path(app.__file__)), run_name="__main__")
    return started


def test_ac10_refuses_to_start_without_secret_key(monkeypatch, capsys):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(SystemExit) as exit_info:
        _start_app_directly(monkeypatch)
    assert exit_info.value.code != 0
    assert "SECRET_KEY" in str(exit_info.value.code)


def test_ac10_starts_with_secret_key_and_never_prints_it(monkeypatch, capsys):
    monkeypatch.setenv("SECRET_KEY", "cok-gizli-deger-123")
    started = _start_app_directly(monkeypatch)
    assert "app" in started
    out = capsys.readouterr()
    assert "cok-gizli-deger-123" not in out.out + out.err


# --- QA gaps (plan 0003, VERIFY triage): login screen states and menu ---

def test_login_screen_empty_state_has_labeled_fields(anon_client):
    html = anon_client.get("/login").get_data(as_text=True)
    text = visible_text(html)
    for label in ("Kullanıcı adı", "Şifre", "Giriş"):  # noqa: RUF001 - Turkish dotless i on purpose
        assert label in text
    assert '<label for="username">' in html and 'id="username"' in html
    assert '<label for="password">' in html and 'type="password"' in html
    assert 'type="submit"' in html
    assert "Yeni Talep" not in text  # no menu before login


def test_login_screen_shows_username_as_plain_text(anon_client):
    resp = _login(anon_client, username='<b>x</b>"', password=WRONG)
    html = resp.get_data(as_text=True)
    assert "<b>x</b>" not in html
    assert "&lt;b&gt;x&lt;/b&gt;" in html
