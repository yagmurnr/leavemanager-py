"""Characterization of the leave rules BR-1…BR-5 as they behave today (spec 0001, AC-1…AC-5).

These pin observed behavior, warts included; a red test here means a rule changed.
"""

from datetime import date

import pytest

from tests.conftest import add_employee, add_request


@pytest.mark.parametrize(
    ("seniority", "expected"),
    [(0, 0), (1, 14), (5, 14), (6, 20), (15, 20), (16, 26), (30, 26)],
)
def test_br1_entitlement_by_seniority(svc, seniority, expected):
    # Frozen today is 2026-10-23; seniority is a plain year difference (BR-2).
    emp = add_employee(hire_date=date(2026 - seniority, 6, 1))
    assert svc.get_seniority_years(emp) == seniority
    assert svc.get_entitlement(emp) == expected


def test_br2_seniority_counts_calendar_years_only(svc, set_today):
    set_today(date(2026, 1, 1))
    emp = add_employee(hire_date=date(2025, 12, 31))
    assert svc.get_seniority_years(emp) == 1


def test_br2_future_hire_is_zero_years(svc, set_today):
    set_today(date(2026, 1, 1))
    emp = add_employee(hire_date=date(2026, 12, 31))
    assert svc.get_seniority_years(emp) == 0


def test_br2_leap_day_hire_does_not_fail(svc):
    emp = add_employee(hire_date=date(2020, 2, 29))
    assert svc.get_seniority_years(emp) == 6
    assert svc.get_entitlement(emp) == 20


def test_br3_single_day_is_one_day(svc):
    assert svc.calc_days(date(2026, 11, 9), date(2026, 11, 9)) == 1


def test_br3_weekend_is_not_deducted(svc):
    # Friday 2026-11-06 → Monday 2026-11-09: Saturday and Sunday are counted.
    assert svc.calc_days(date(2026, 11, 6), date(2026, 11, 9)) == 4


def test_br3_end_before_start_is_zero_days(svc):
    assert svc.calc_days(date(2026, 11, 10), date(2026, 11, 9)) == 0


def test_br4_used_counts_only_approved(svc):
    add_employee(emp_id=1)
    add_request(1, date(2026, 7, 6), date(2026, 7, 8), "Onaylandi")     # 3 days
    add_request(1, date(2026, 8, 3), date(2026, 8, 3), "Onaylandi")     # 1 day
    add_request(1, date(2026, 11, 2), date(2026, 11, 6), "Beklemede")   # not counted
    add_request(1, date(2026, 9, 14), date(2026, 9, 25), "Reddedildi")  # not counted
    add_employee(emp_id=2)
    add_request(2, date(2026, 7, 1), date(2026, 7, 10), "Onaylandi")    # other employee
    assert svc.get_used_days(1) == 4


def test_br4_used_is_zero_without_approved(svc):
    add_employee(emp_id=1)
    add_request(1, date(2026, 11, 2), date(2026, 11, 6), "Beklemede")
    assert svc.get_used_days(1) == 0


def test_br5_remaining_is_entitlement_minus_used(svc):
    emp = add_employee(emp_id=1, hire_date=date(2019, 6, 1))  # 7 years → 20 days
    add_request(1, date(2026, 7, 6), date(2026, 7, 10), "Onaylandi")   # 5 days
    assert svc.get_remaining(emp) == 15


def test_br5_remaining_can_be_negative(svc):
    emp = add_employee(emp_id=1, hire_date=date(2026, 6, 1))  # 0 years → 0 days
    add_request(1, date(2026, 10, 5), date(2026, 10, 7), "Onaylandi")  # 3 days
    assert svc.get_remaining(emp) == -3
