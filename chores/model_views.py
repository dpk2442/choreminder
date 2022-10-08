import datetime
from typing import Generic, Optional, TypeVar

from django.db.models import Model as DjangoModel
from django.utils import timezone

from chores import models

DjangoModelType = TypeVar("DjangoModelType", bound=DjangoModel)


def calculate_percentage(val):
    return round(100 * val, 2)


def compute_status(current_time: datetime.datetime,
                   latest_log_timestamp: Optional[datetime.datetime],
                   due_duration: datetime.timedelta,
                   overdue_duration: Optional[datetime.timedelta]) -> "ChoreStatus":
    if latest_log_timestamp is None:
        return ChoreStatus("due", None, 0)
    else:
        next_due = latest_log_timestamp + due_duration
        if next_due > current_time:
            return ChoreStatus("completed", "due", calculate_percentage(
                (current_time - latest_log_timestamp) / due_duration))
        elif overdue_duration is None:
            return ChoreStatus("due", None, 0)
        else:
            overdue_time = next_due + overdue_duration
            if current_time < overdue_time:
                return ChoreStatus("due", "overdue", calculate_percentage(
                    (current_time - next_due) / overdue_duration))
            else:
                return ChoreStatus("overdue", None, 0)


class ModelViewBase(Generic[DjangoModelType]):

    def __init__(self, obj: DjangoModelType):
        self._obj = obj

    def __str__(self) -> str:
        return str(self._obj)

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ModelViewBase) and self._obj == other._obj


class Chore(ModelViewBase[models.Chore]):

    def __init__(self, chore: models.Chore):
        super().__init__(chore)
        self._fetched_latest_log = False
        self._latest_log = None
        self._status = None

    @property
    def id(self):
        return self._obj.id

    @property
    def name(self):
        return self._obj.name

    @property
    def description(self):
        return self._obj.description

    @property
    def latest_log(self):
        if not self._fetched_latest_log:
            db_log = self._obj.log_set.order_by("-timestamp").first()
            if db_log is not None:
                self._latest_log = Log(db_log)

        return self._latest_log

    @property
    def status(self):
        if self._status is None:
            self._status = compute_status(timezone.now(),
                                          self.latest_log and self.latest_log.timestamp or None,
                                          self._obj.due_duration,
                                          self._obj.overdue_duration)

        return self._status

    @property
    def weight(self):
        status = self.status
        if status.state == "completed":
            return status.percentage
        elif status.state == "due":
            return status.percentage + 100
        elif status.state == "overdue":
            return status.percentage + 200
        else:
            raise ValueError("State value is unexpected")

    def next_due(self) -> datetime.datetime:
        if self.latest_log is None:
            return None

        return self.latest_log.timestamp + self._obj.due_duration


class Log(ModelViewBase[models.Log]):

    def __init__(self, log: models.Log):
        super().__init__(log)

    @property
    def timestamp(self):
        return self._obj.timestamp


class ChoreStatus(object):

    def __init__(self, state: Optional[str], next_state: Optional[str], percentage: float):
        self.state = state
        self.next_state = next_state
        self.percentage = percentage

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, ChoreStatus)
                and other is not None
                and self.state == other.state
                and self.next_state == other.next_state
                and self.percentage == other.percentage)

    def __str__(self):
        return f"ChoreStatus(state={self.state}, next_state={self.next_state}, percentage={self.percentage})"

    def __repr__(self) -> str:
        return self.__str__()
