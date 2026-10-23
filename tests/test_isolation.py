"""R-3, R-4, AC-13: no test sees the real clock or another test's data."""

from datetime import date

import app
from tests.conftest import DEFAULT_TODAY, add_employee


def test_clock_is_frozen_by_default():
    assert app.datetime.now().date() == DEFAULT_TODAY


def test_clock_can_be_set_per_test(set_today):
    set_today(date(2027, 3, 1))
    assert app.datetime.now().date() == date(2027, 3, 1)


def test_clock_keeps_strptime_behavior():
    assert app.datetime.strptime("2026-11-02", "%Y-%m-%d").date() == date(2026, 11, 2)


def test_data_starts_empty_each_test():
    assert app.Db.employees == []
    assert app.Db.requests == []
    assert app.Db.next_id == 1


def test_data_written_here_is_gone_in_the_next_test_a():
    add_employee(emp_id=99)
    assert len(app.Db.employees) == 1


def test_data_written_here_is_gone_in_the_next_test_b():
    assert all(e["id"] != 99 for e in app.Db.employees)
