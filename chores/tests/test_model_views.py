import datetime
from datetime import timedelta as td

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from chores import model_views
from .utils import create_chore, create_log, get_user


class ComputeStatusTest(TestCase):

    def test_no_latest_log(self):
        status = model_views.compute_status(timezone.now(), None, None, None)
        self.assertEqual(status, model_views.ChoreStatus(None, None, 0))

    def test_completed(self):
        now = timezone.now()
        last_log_timestamp = now
        due_duration = td(days=1)

        for expected_percentage in (0, 25, 50, 75):
            status = model_views.compute_status(
                now, last_log_timestamp, due_duration, None)
            self.assertEqual(
                status, model_views.ChoreStatus("completed", "due", expected_percentage))
            last_log_timestamp -= td(hours=6)

    def test_due_no_overdue(self):
        now = timezone.now()
        last_log_timestamp = now - td(days=1)
        due_duration = td(days=1)

        for _ in range(10):
            status = model_views.compute_status(
                now, last_log_timestamp, due_duration, None)
            self.assertEqual(
                status, model_views.ChoreStatus("due", None, 0))
            last_log_timestamp -= td(hours=6)

    def test_due_with_overdue(self):
        now = timezone.now()
        last_log_timestamp = now - td(days=1)
        due_duration = td(days=1)
        overdue_duration = td(days=1)

        for expected_percentage in (0, 25, 50, 75):
            status = model_views.compute_status(
                now, last_log_timestamp, due_duration, overdue_duration)
            self.assertEqual(
                status, model_views.ChoreStatus("due", "overdue", expected_percentage))
            last_log_timestamp -= td(hours=6)

    def test_overdue(self):
        now = timezone.now()
        last_log_timestamp = now - td(days=2)
        due_duration = td(days=1)
        overdue_duration = td(days=1)

        for _ in range(10):
            status = model_views.compute_status(
                now, last_log_timestamp, due_duration, overdue_duration)
            self.assertEqual(
                status, model_views.ChoreStatus("overdue", None, 0))
            last_log_timestamp -= td(hours=6)


class ChoreModelViewTest(TestCase):

    def test_latest_chore(self):
        user = get_user()
        chore = create_chore(user)
        chore_view = model_views.Chore(chore)

        self.assertIsNone(chore_view.latest_log)

        now = timezone.now()
        create_log(now-datetime.timedelta(days=1), chore, user)
        log2 = create_log(now+datetime.timedelta(days=1), chore, user)

        self.assertEqual(chore_view.latest_log, model_views.Log(log2))

    def test_next_due(self):
        user = get_user()
        chore = create_chore(user)
        chore_view = model_views.Chore(chore)

        self.assertIsNone(chore_view.next_due())

        now = timezone.now()
        create_log(now, chore, user)
        self.assertEqual(chore_view.next_due(), now +
                         datetime.timedelta(days=1))
