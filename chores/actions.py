from . import queries
from .type_helpers import UserType


def get_sorted_chores(user: UserType, tag_id: int | None):
    chores = queries.query_chores(user, tag_id)
    chores.sort(key=lambda chore: chore.weight, reverse=True)
    return chores
