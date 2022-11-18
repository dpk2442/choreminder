from . import queries
from .typing import UserType


def get_sorted_chores(user: UserType):
    chores = queries.query_chores(user)
    chores.sort(key=lambda chore: chore.weight, reverse=True)
    return chores
