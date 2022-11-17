import datetime
import random
import string

from django.contrib.auth.models import User

from chores import models


def get_user() -> User:
    user, _ = User.objects.get_or_create(username="test")
    return user


def create_random_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=20))


def create_random_user() -> User:
    return User.objects.create(username=create_random_string())


def create_chore(user: User) -> models.Chore:
    return models.Chore.objects.create(
        name=create_random_string(),
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


def create_tag(user: User) -> models.Tag:
    return models.Tag.objects.create(
        name=create_random_string(),
        user=user,
    )
