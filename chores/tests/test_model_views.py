import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from chores import model_views
from .utils import create_chore, create_log, get_user


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

    def test_display_status(self):
        user = get_user()
        chore = create_chore(user)
        chore_view = model_views.Chore(chore)
        now = timezone.now()
        self.assertEqual(chore_view.display_status(), "N/A")
        create_log(now - datetime.timedelta(days=3), chore, user)
        self.assertEqual(chore_view.display_status(), "Overdue")
        create_log(now - datetime.timedelta(days=1.5), chore, user)
        self.assertEqual(chore_view.display_status(), "Due")
        create_log(now - datetime.timedelta(days=0.5), chore, user)
        self.assertEqual(chore_view.display_status(), "Completed")
        create_log(now + datetime.timedelta(days=1), chore, user)
        self.assertEqual(chore_view.display_status(), "Completed")
