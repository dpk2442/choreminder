from datetime import timedelta as td

from django.test import TestCase
from django.utils import timezone

from chores import actions, model_views
from .utils import create_chore, create_log, get_user


class TestGetSortedChores(TestCase):

    def test_sorted_properly(self):
        now = timezone.now()
        user = get_user()

        chore_completed = create_chore(user)
        create_log(now - td(hours=1), chore_completed, user)

        chore_due = create_chore(user)
        create_log(now - td(days=1, hours=1), chore_due, user)

        chore_overdue = create_chore(user)
        create_log(now - td(days=2, hours=1), chore_overdue, user)

        chore_no_log = create_chore(user)

        self.assertEqual(actions.get_sorted_chores(user), list(map(model_views.Chore, [
                         chore_overdue, chore_due, chore_no_log, chore_completed])))
