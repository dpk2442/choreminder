import datetime
import random
import string

from django.contrib.auth.models import User
from django.utils import timezone

from chores import models


def get_user() -> User:
    user, _ = User.objects.get_or_create(username="test")
    return user


def create_random_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=20))


def create_random_user() -> User:
    return User.objects.create(username=create_random_string())


def create_chore(user: User, tag: models.Tag = None) -> models.Chore:
    chore = models.Chore.objects.create(
        name=create_random_string(),
        description="Test Description",
        due_duration=datetime.timedelta(days=1),
        overdue_duration=datetime.timedelta(days=1),
        user=user,
    )

    if tag is not None:
        chore.tags.set((tag,))

    return chore


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


def create_away_date(user: User) -> models.AwayDate:
    start_date = timezone.now().today()
    end_date = start_date + datetime.timedelta(days=1)

    return models.AwayDate.objects.create(
        name=create_random_string(),
        start_date=start_date,
        end_date=end_date,
        user=user,
    )
