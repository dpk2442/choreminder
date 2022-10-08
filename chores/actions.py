from typing import Union

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser

from . import queries


def get_sorted_chores(user: Union[AbstractBaseUser, AnonymousUser]):
    chores = queries.query_chores(user)
    chores.sort(key=lambda chore: chore.weight, reverse=True)
    return chores
