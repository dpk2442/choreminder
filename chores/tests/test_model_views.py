import datetime
from datetime import timedelta as td

from django.test import TestCase
from django.utils import timezone

from chores.model_views import (Chore, ChoreState, ChoreStatus, Log,
                                add_delta_with_away_dates, compute_status)

from .utils import create_away_date, create_chore, create_log, get_user


class TestAddDeltaWithAwayDates(TestCase):

    def test_no_away_dates(self):
        user = get_user()
        start_time = timezone.now()
        delta_time = td(days=5)

        result = add_delta_with_away_dates(user, start_time, delta_time)
        self.assertEqual(result,  start_time + delta_time)

    def test_away_date_before(self):
        user = get_user()

        now = timezone.now()
        _ = create_away_date(user, now - td(days=5), now - td(days=3))

        result = add_delta_with_away_dates(user, now, td(days=1))
        self.assertEqual(result,  now + td(days=1))

    def test_away_date_after(self):
        user = get_user()

        now = timezone.now()
        _ = create_away_date(user, now + td(days=5), now + td(days=6))

        result = add_delta_with_away_dates(user, now, td(days=2))
        self.assertEqual(result,  now + td(days=2))

    def test_away_date_overlaps_end(self):
        user = get_user()

        now = timezone.now()
        _ = create_away_date(
            user, now.date() + td(days=1), now.date() + td(days=2))

        result = add_delta_with_away_dates(user, now, td(days=2))
        self.assertEqual(result, now + td(days=4))

    def test_away_date_overlaps_start(self):
        user = get_user()

        now = timezone.now()
        _ = create_away_date(user, now.date() - td(days=1),
                             now.date() + td(days=1))

        result = add_delta_with_away_dates(user, now, td(days=2))
        self.assertEqual(result, now + td(days=3))

    def test_away_date_multiple(self):
        user = get_user()

        now = timezone.now()
        _ = create_away_date(user, now.date() + td(days=1),
                             now.date() + td(days=3))
        _ = create_away_date(user, now.date() + td(days=2),
                             now.date() + td(days=4))
        _ = create_away_date(user, now.date() + td(days=6),
                             now.date() + td(days=8))

        result = add_delta_with_away_dates(user, now, td(days=3))
        self.assertEqual(result, now + td(days=10))


class ComputeStatusTest(TestCase):

    def test_no_latest_log(self):
        status = compute_status(get_user(), timezone.now(), None, None, None)
        self.assertEqual(status, ChoreStatus(
            ChoreState.DUE, None, 0, None, None))

    def test_completed(self):
        now = timezone.now()
        last_log_timestamp = now
        due_duration = td(days=1)

        for expected_percentage in (0, 25, 50, 75):
            status = compute_status(
                get_user(), now, last_log_timestamp, due_duration, None)
            self.assertEqual(status, ChoreStatus(ChoreState.COMPLETED, ChoreState.DUE,
                             expected_percentage, last_log_timestamp + due_duration, None))
            last_log_timestamp -= td(hours=6)

    def test_due_no_overdue(self):
        now = timezone.now()
        last_log_timestamp = now - td(days=1)
        due_duration = td(days=1)

        for _ in range(10):
            status = compute_status(
                get_user(), now, last_log_timestamp, due_duration, None)
            self.assertEqual(status, ChoreStatus(
                ChoreState.DUE, None, 0, last_log_timestamp + due_duration, None))
            last_log_timestamp -= td(hours=6)

    def test_due_with_overdue(self):
        now = timezone.now()
        last_log_timestamp = now - td(days=1)
        due_duration = td(days=1)
        overdue_duration = td(days=1)

        for expected_percentage in (0, 25, 50, 75):
            status = compute_status(
                get_user(), now, last_log_timestamp, due_duration, overdue_duration)
            self.assertEqual(status, ChoreStatus(
                ChoreState.DUE, ChoreState.OVERDUE, expected_percentage,
                last_log_timestamp + due_duration,
                last_log_timestamp + due_duration + overdue_duration
            ))
            last_log_timestamp -= td(hours=6)

    def test_overdue(self):
        now = timezone.now()
        last_log_timestamp = now - td(days=2)
        due_duration = td(days=1)
        overdue_duration = td(days=1)

        for _ in range(10):
            status = compute_status(
                get_user(), now, last_log_timestamp, due_duration, overdue_duration)
            self.assertEqual(status, ChoreStatus(
                ChoreState.OVERDUE, None, 0,
                last_log_timestamp + due_duration,
                last_log_timestamp + due_duration + overdue_duration
            ))
            last_log_timestamp -= td(hours=6)


class ChoreModelViewTest(TestCase):

    def test_latest_chore(self):
        user = get_user()
        chore = create_chore(user)
        chore_view = Chore(chore)

        self.assertIsNone(chore_view.latest_log)

        now = timezone.now()
        create_log(now-datetime.timedelta(days=1), chore, user)
        log2 = create_log(now+datetime.timedelta(days=1), chore, user)

        self.assertEqual(chore_view.latest_log, Log(log2))

    def test_weight(self):
        user = get_user()
        chore = create_chore(user)
        chore_view = Chore(chore)

        chore_view._status = ChoreStatus(
            ChoreState.COMPLETED, None, 10, None, None)
        self.assertEqual(chore_view.weight, 10)

        chore_view._status = ChoreStatus(
            ChoreState.DUE, None, 10, None, None)
        self.assertEqual(chore_view.weight, 110)

        chore_view._status = ChoreStatus(
            ChoreState.OVERDUE, None, 10, None, None)
        self.assertEqual(chore_view.weight, 210)
