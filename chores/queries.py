from typing import List

from chores import model_views, models
from chores.typing import UserType


def query_chores(user: UserType) -> List[model_views.Chore]:
    if user is None:
        raise ValueError("Invalid user provided")

    return list(map(model_views.Chore, models.Chore.objects.filter(user=user).order_by("id")))


def query_tags(user: UserType) -> List[model_views.Tag]:
    if user is None:
        raise ValueError("Invalid user provided")

    return list(map(model_views.Tag, models.Tag.objects.filter(user=user).order_by("id")))
