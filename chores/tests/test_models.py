import datetime
from pydoc import describe
from time import time

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from chores import models
from .utils import create_chore_name


def get_user() -> User:
    user, _ = User.objects.get_or_create(username="test")
    return user


def create_chore(user: User) -> models.Chore:
    return models.Chore.objects.create(
        name=create_chore_name(),
        description="Test Description",
        due_duration=datetime.timedelta(days=1),
        overdue_duration=datetime.timedelta(days=1),
        user=user,
    )


def create_log(timestamp: datetime.datetime, chore: models.Chore, user: User) -> models.Log:
    return models.Log.objects.create(
        timestamp=timestamp,
        chore=chore,
        user=user,
    )


class ChoreModelTest(TestCase):

    def test_latest_chore(self):
        user = get_user()
        chore = create_chore(user)

        self.assertIsNone(chore.latest_log())

        now = timezone.now()
        create_log(now-datetime.timedelta(days=1), chore, user)
        log2 = create_log(now+datetime.timedelta(days=1), chore, user)

        self.assertEqual(chore.latest_log(), log2)

    def test_next_due(self):
        user = get_user()
        chore = create_chore(user)

        self.assertIsNone(chore.next_due())

        now = timezone.now()
        create_log(now, chore, user)
        self.assertEqual(chore.next_due(), now + datetime.timedelta(days=1))

    def test_display_status(self):
        user = get_user()
        chore = create_chore(user)
        now = timezone.now()
        self.assertEqual(chore.display_status(), "N/A")
        create_log(now - datetime.timedelta(days=3), chore, user)
        self.assertEqual(chore.display_status(), "Overdue")
        create_log(now - datetime.timedelta(days=1.5), chore, user)
        self.assertEqual(chore.display_status(), "Due")
        create_log(now - datetime.timedelta(days=0.5), chore, user)
        self.assertEqual(chore.display_status(), "Completed")
        create_log(now + datetime.timedelta(days=1), chore, user)
        self.assertEqual(chore.display_status(), "Completed")
