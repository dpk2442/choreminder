from typing import List, Union

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser

from chores import model_views, models


def query_chores(user: Union[AbstractBaseUser, AnonymousUser]) -> List[model_views.Chore]:
    if user is None:
        raise ValueError("Invalid user provided")

    return list(map(model_views.Chore, models.Chore.objects.filter(user=user).order_by("id")))


def query_tags(user: Union[AbstractBaseUser, AnonymousUser]) -> List[model_views.Tag]:
    if user is None:
        raise ValueError("Invalid user provided")

    return list(map(model_views.Tag, models.Tag.objects.filter(user=user).order_by("id")))
