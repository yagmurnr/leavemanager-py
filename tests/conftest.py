"""Shared fixtures for the characterization tests (spec 0001).

Every test runs against a frozen clock and an empty in-memory store, so no test depends on the
real date or on data left behind by another test (docs/testing.md, Resource hygiene rule 5).
"""

from datetime import date, datetime

import pytest

import app

DEFAULT_TODAY = date(2026, 10, 23)


class _Clock:
    today = DEFAULT_TODAY


class FrozenDatetime(datetime):
    """app.datetime replacement: now() returns the frozen day, everything else is datetime."""

    @classmethod
    def now(cls, tz=None):
        d = _Clock.today
        return cls(d.year, d.month, d.day, 12, 0, 0, tzinfo=tz)


@pytest.fixture(autouse=True)
def frozen_clock(monkeypatch):
    """Freeze "today" for every test. Call set_today(...) to move it within a test."""
    monkeypatch.setattr(_Clock, "today", DEFAULT_TODAY)
    monkeypatch.setattr(app, "datetime", FrozenDatetime)


@pytest.fixture(autouse=True)
def empty_db(monkeypatch):
    """Start every test with no employees, requests or accounts; restored after the test."""
    monkeypatch.setattr(app.Db, "employees", [])
    monkeypatch.setattr(app.Db, "requests", [])
    monkeypatch.setattr(app.Db, "next_id", 1)
    monkeypatch.setattr(app.Db, "accounts", {})


TEST_SECRET_KEY = "test-only-secret-key"  # noqa: S105 - test value, never used outside tests
TEST_USERNAME = "test.kullanici"


@pytest.fixture(autouse=True)
def secret_key(monkeypatch):
    """Every test has a session key, also when app.py is started as __main__ (spec 0003, R10)."""
    monkeypatch.setenv("SECRET_KEY", TEST_SECRET_KEY)
    monkeypatch.setitem(app.app.config, "SECRET_KEY", TEST_SECRET_KEY)


@pytest.fixture
def set_today(monkeypatch):
    def _set(d):
        monkeypatch.setattr(_Clock, "today", d)

    return _set


@pytest.fixture
def svc():
    return app.LeaveService()


@pytest.fixture
def anon_client():
    """A client that has not logged in."""
    app.app.config["TESTING"] = True
    return app.app.test_client()


@pytest.fixture
def client(anon_client):
    """A logged-in client (account TEST_USERNAME, employee 1): the pre-login tests run as a user."""
    app.Db.accounts[TEST_USERNAME] = {"password_hash": "unused", "employee_id": 1}
    with anon_client.session_transaction() as s:
        s["username"] = TEST_USERNAME
    return anon_client


def add_employee(emp_id=1, hire_date=date(2020, 1, 1), name="Test Personel", department="IT"):
    emp = {"id": emp_id, "name": name, "department": department, "hire_date": hire_date}
    app.Db.employees.append(emp)
    return emp


def add_request(employee_id, start, end, status, reason="test"):
    req = {"id": app.Db.next_id, "employee_id": employee_id, "start": start, "end": end,
           "reason": reason, "status": status}
    app.Db.requests.append(req)
    app.Db.next_id += 1
    return req
