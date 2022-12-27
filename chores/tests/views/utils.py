import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from chores import models
from ..utils import create_random_string


class AuthenticatedTest(TestCase):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def create_chore_in_db(self, tags=None) -> models.Chore:
        chore = models.Chore.objects.create(
            name=create_random_string(),
            description="Test Description",
            due_duration=datetime.timedelta(days=1),
            overdue_duration=datetime.timedelta(),
            user=self.user)

        if tags is not None:
            chore.tags.set(tags)

        return chore

    def create_log_in_db(self, chore: models.Chore) -> models.Log:
        return models.Log.objects.create(
            timestamp=timezone.now(),
            chore=chore,
            user=self.user)

    def create_tag_in_db(self) -> models.Tag:
        return models.Tag.objects.create(
            name=create_random_string(),
            user=self.user)

    def create_away_date_in_db(self, start_date=None, end_date=None) -> models.AwayDate:
        if start_date is None:
            start_date = timezone.now().today()

        if end_date is None:
            end_date = start_date + datetime.timedelta(days=1)

        return models.AwayDate.objects.create(
            name=create_random_string(),
            start_date=start_date,
            end_date=end_date,
            user=self.user,
        )

    def setUp(self) -> None:
        super().setUp()
        self.user, _ = User.objects.get_or_create(
            username=create_random_string())
        self.user2, _ = User.objects.get_or_create(
            username=create_random_string())
        self.client.force_login(self.user)
