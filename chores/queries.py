from typing import List

from chores import model_views, models
from chores.type_helpers import UserType


def query_chores(user: UserType, tag_id: int | None) -> List[model_views.Chore]:
    if user is None:
        raise ValueError("Invalid user provided")

    filter_args = dict(user=user)
    if tag_id is not None:
        filter_args["tags__id"] = tag_id

    return list(map(model_views.Chore, models.Chore.objects.filter(**filter_args).order_by("id")))


def query_tags(user: UserType) -> List[model_views.Tag]:
    if user is None:
        raise ValueError("Invalid user provided")

    return list(map(model_views.Tag, models.Tag.objects.filter(user=user).order_by("id")))
