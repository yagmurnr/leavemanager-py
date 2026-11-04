"""Spec 0002: pages show user data as plain text (CB-1…CB-3) and keep showing today's data (PB-2…PB-4).

Pages are judged by what a user sees (tests/html_text.py), not by the HTML shape.
"""

import re
from datetime import date

import app
from tests.conftest import add_employee
from tests.html_text import option_labels, styled_texts, table_rows, visible_text


def _page(client, path):
    resp = client.get(path)
    assert resp.status_code == 200
    return resp.get_data(as_text=True)


def _count(text, label):
    return int(re.search(label + r":\s*(\d+)", text).group(1))


# --- PB: what the pages show today, observed with the seed data on the frozen today 2026-10-23 ---

def test_pb2_dashboard_shows_same_counts_and_balances(client):
    app.seed()
    html = _page(client, "/")
    text = visible_text(html)
    assert (_count(text, "Bekleyen"), _count(text, "Onaylanan"), _count(text, "Reddedilen")) == (4, 1, 3)
    assert table_rows(html) == [
        ["Ad", "Birim", "Hak", "Kullanilan", "Kalan"],
        ["Ayse Yilmaz", "IT", "26", "12", "14"],
        ["Mehmet Demir", "Muhasebe", "20", "0", "20"],
        ["Zeynep Kaya", "IK", "14", "0", "14"],
        ["Ahmet Celik", "IT", "20", "0", "20"],
        ["Elif Sahin", "Satis", "0", "0", "0"],
    ]


def test_pb2_requests_page_shows_same_rows(client):
    app.seed()
    assert table_rows(_page(client, "/requests")) == [
        ["Personel", "Baslangic", "Bitis", "Gun", "Neden", "Durum"],
        ["Ayse Yilmaz", "2026-07-06", "2026-07-17", "12", "Yaz tatili", "Onaylandi"],
        ["Mehmet Demir", "2026-11-02", "2026-11-04", "3", "Aile ziyareti", "Beklemede"],
        ["Zeynep Kaya", "2026-11-09", "2026-11-09", "1", "Saglik", "Beklemede"],
        ["Ahmet Celik", "2026-12-21", "2026-12-25", "5", "Yilbasi oncesi", "Beklemede"],
        ["Ayse Yilmaz", "2026-12-28", "2026-12-30", "3", "Yil sonu", "Beklemede"],
        ["Elif Sahin", "2026-10-05", "2026-10-07", "3", "Tasinma", "Reddedildi"],
        ["Zeynep Kaya", "2026-09-14", "2026-09-25", "12", "Uzun tatil", "Reddedildi"],
        ["Mehmet Demir", "2026-08-03", "2026-08-03", "1", "Ozel is", "Reddedildi"],
    ]


def test_pb2_form_lists_same_employees(client):
    app.seed()
    html = _page(client, "/new")
    assert option_labels(html) == ["Ayse Yilmaz", "Mehmet Demir", "Zeynep Kaya", "Ahmet Celik", "Elif Sahin"]
    for label in ("Personel:", "Baslangic:", "Bitis:", "Neden:"):
        assert label in visible_text(html)


def test_pb3_status_badge_colors_unchanged(client):
    app.seed()
    badges = {text: style for style, text in styled_texts(_page(client, "/requests"))
              if text in ("Onaylandi", "Beklemede", "Reddedildi")}
    assert badges == {"Onaylandi": "color:green", "Beklemede": "color:orange", "Reddedildi": "color:red"}


def test_pb4_insufficient_balance_message_text_unchanged(client):
    add_employee(emp_id=1, hire_date=date(2026, 6, 1))  # 0 years → 0 days remaining
    resp = client.post("/new", data={"employee_id": "1", "start": "2026-11-02", "end": "2026-11-02",
                                     "reason": "x"})
    assert resp.status_code == 200
    assert ("HATA: ERR-412 NullReferenceGibi - bakiye yetersiz. IT'ye bildirin: dahili 4127"
            in visible_text(resp.get_data(as_text=True)))
