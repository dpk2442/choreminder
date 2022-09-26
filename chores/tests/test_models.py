import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from chores import models
from .utils import create_chore_name


class ChoreModelTest(TestCase):

    def test_latest_chore(self):
        user, _ = User.objects.get_or_create(username="test")
        chore = models.Chore.objects.create(
            name=create_chore_name(),
            description="Test Description",
            due_duration=datetime.timedelta(days=1),
            overdue_duration=datetime.timedelta(),
            user=user)

        self.assertIsNone(chore.latest_log())

        now = timezone.now()
        log1 = models.Log.objects.create(
            timestamp=now-datetime.timedelta(days=1), chore=chore, user=user)
        log2 = models.Log.objects.create(
            timestamp=now+datetime.timedelta(days=1), chore=chore, user=user)

        self.assertEqual(chore.latest_log(), log2)
