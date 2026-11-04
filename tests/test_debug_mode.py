"""Spec 0002: debug mode is off unless asked for (CB-5), and errors show no internals (CB-4).

Starting the app is simulated: Flask.run is replaced, app.py runs as __main__ via runpy, so no
server is started and no port is opened (docs/testing.md, Resource hygiene).
"""

import runpy
from datetime import date
from pathlib import Path

import flask

import app
from tests.conftest import add_employee
from tests.html_text import visible_text

APP_PY = str(Path(app.__file__))


def _start_app_directly(monkeypatch):
    started = {}

    def fake_run(self, *args, **kwargs):
        started["app"] = self
        started["kwargs"] = kwargs

    monkeypatch.setattr(flask.Flask, "run", fake_run)
    runpy.run_path(APP_PY, run_name="__main__")
    return started


def test_cb5_debug_off_when_started_directly_without_env(monkeypatch):
    monkeypatch.delenv("FLASK_DEBUG", raising=False)
    started = _start_app_directly(monkeypatch)
    assert started["kwargs"].get("debug") is not True
    assert started["app"].debug is False


def test_cb5_debug_on_only_with_env_flag(monkeypatch):
    monkeypatch.setenv("FLASK_DEBUG", "1")
    started = _start_app_directly(monkeypatch)
    assert started["app"].debug is True


def test_cb4_unexpected_error_shows_generic_page_without_traceback(client, monkeypatch):
    # Production-like: the error reaches the error page instead of the test. PROPAGATE_EXCEPTIONS
    # is pinned too, otherwise it follows DEBUG and a developer's FLASK_DEBUG=1 turns this red.
    monkeypatch.setitem(app.app.config, "TESTING", False)
    monkeypatch.setitem(app.app.config, "PROPAGATE_EXCEPTIONS", False)
    add_employee(emp_id=1, hire_date=date(2019, 6, 1))
    # A request of an employee that does not exist makes the request list fail (plan 0001, R5).
    app.Db.requests.append({"id": 1, "employee_id": 999, "start": date(2026, 11, 2),
                            "end": date(2026, 11, 2), "reason": "x", "status": "Beklemede"})
    resp = client.get("/requests")
    html = resp.get_data(as_text=True)
    assert resp.status_code == 500
    assert "Beklenmeyen bir hata" in visible_text(html)
    for leak in ("Traceback", "IndexError", "app.py", "Werkzeug", "File \""):
        assert leak not in html
