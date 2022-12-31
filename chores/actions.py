from collections import OrderedDict

from . import queries
from .model_views import ChoreState
from .type_helpers import UserType


def get_grouped_sorted_chores(user: UserType, tag_id: int | None):
    chores = queries.query_chores(user, tag_id)
    chores.sort(key=lambda chore: chore.weight, reverse=True)
    groups = {
        ChoreState.OVERDUE: [],
        ChoreState.DUE: [],
        ChoreState.COMPLETED: [],
    }

    while chores:
        chore = chores.pop(0)
        groups[chore.status.state].append(chore)

    groups = OrderedDict((
        ("Pending", groups[ChoreState.OVERDUE] + groups[ChoreState.DUE]),
        ("Completed", groups[ChoreState.COMPLETED]),
    ))

    return groups
