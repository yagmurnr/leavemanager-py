"""Characterization of the new-request form flow BR-6…BR-10 and OD-7 (spec 0001, AC-6…AC-11).

The form is posted through the Flask test client; outcomes are judged by the redirect, the page
content and whether a request was stored. Observed behavior is pinned as is, warts included.
"""

from datetime import date

import app
from tests.conftest import add_employee

# Hired 2019 → 7 years on the frozen today (2026-10-23) → 20 days entitlement, nothing used.
REMAINING = 20


def _employee_with_20_days():
    return add_employee(emp_id=1, hire_date=date(2019, 6, 1))


def _post(client, employee_id="1", start="2026-11-02", end="2026-11-02", reason="Aile ziyareti"):
    return client.post("/new", data={"employee_id": employee_id, "start": start, "end": end,
                                     "reason": reason})


def _redirects_to_requests(resp):
    return resp.status_code == 302 and resp.headers["Location"].endswith("/requests")


def test_br6_form_rejects_when_days_exceed_remaining(client):
    _employee_with_20_days()
    resp = _post(client, start="2026-11-02", end="2026-11-22")  # 21 days = remaining + 1
    assert resp.status_code == 200
    assert "bakiye yetersiz" in resp.get_data(as_text=True)
    assert app.Db.requests == []


def test_br7_od4_days_equal_remaining_silently_dropped(client):
    _employee_with_20_days()
    resp = _post(client, start="2026-11-02", end="2026-11-21")  # 20 days = remaining
    assert _redirects_to_requests(resp)
    assert "bakiye yetersiz" not in resp.get_data(as_text=True)
    assert app.Db.requests == []


def test_br7_days_below_remaining_saved(client):
    _employee_with_20_days()
    resp = _post(client, start="2026-11-02", end="2026-11-20")  # 19 days = remaining - 1
    assert _redirects_to_requests(resp)
    assert len(app.Db.requests) == 1


def test_br8_new_request_is_pending_and_redirects(client):
    _employee_with_20_days()
    resp = _post(client, start="2026-11-02", end="2026-11-04", reason="Aile ziyareti")
    assert _redirects_to_requests(resp)
    assert len(app.Db.requests) == 1
    req = app.Db.requests[0]
    assert req["employee_id"] == 1
    assert req["start"] == date(2026, 11, 2)
    assert req["end"] == date(2026, 11, 4)
    assert req["reason"] == "Aile ziyareti"
    assert req["status"] == "Beklemede"


def test_br9_past_dated_request_accepted(client):
    _employee_with_20_days()
    resp = _post(client, start="2026-10-01", end="2026-10-03")  # before frozen today
    assert _redirects_to_requests(resp)
    assert len(app.Db.requests) == 1
    assert app.Db.requests[0]["start"] == date(2026, 10, 1)


def test_br10_od6_reversed_range_accepted(client):
    _employee_with_20_days()
    resp = _post(client, start="2026-11-10", end="2026-11-09")  # end before start
    assert _redirects_to_requests(resp)
    assert len(app.Db.requests) == 1
    assert app.Db.requests[0]["end"] < app.Db.requests[0]["start"]


def test_od7_unknown_employee_silently_redirects(client):
    _employee_with_20_days()
    resp = _post(client, employee_id="999")
    assert _redirects_to_requests(resp)
    assert app.Db.requests == []


def test_od7_invalid_date_silently_redirects(client):
    _employee_with_20_days()
    resp = _post(client, start="23.10.2026")
    assert _redirects_to_requests(resp)
    assert app.Db.requests == []
