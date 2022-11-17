import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from chores import models
from ..utils import create_random_string


class AuthenticatedTest(TestCase):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def create_chore_in_db(self) -> models.Chore:
        return models.Chore.objects.create(
            name=create_random_string(),
            description="Test Description",
            due_duration=datetime.timedelta(days=1),
            overdue_duration=datetime.timedelta(),
            user=self.user)

    def create_log_in_db(self, chore: models.Chore) -> models.Log:
        return models.Log.objects.create(
            timestamp=timezone.now(),
            chore=chore,
            user=self.user)

    def create_tag_in_db(self) -> models.Tag:
        return models.Tag.objects.create(
            name=create_random_string(),
            user=self.user)

    def setUp(self) -> None:
        super().setUp()
        self.user, _ = User.objects.get_or_create(
            username=create_random_string())
        self.user2, _ = User.objects.get_or_create(
            username=create_random_string())
        self.client.force_login(self.user)
