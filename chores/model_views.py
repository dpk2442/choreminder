import datetime
from enum import Enum
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
        return ChoreStatus(ChoreState.DUE, None, 0, None, None)
    else:
        next_due = latest_log_timestamp + due_duration
        next_overdue = next_due + overdue_duration if overdue_duration is not None else None
        if next_due > current_time:
            percentage = calculate_percentage(
                (current_time - latest_log_timestamp) / due_duration)
            return ChoreStatus(ChoreState.COMPLETED, ChoreState.DUE, percentage, next_due, next_overdue)
        elif next_overdue is None:
            return ChoreStatus(ChoreState.DUE, None, 0, next_due, next_overdue)
        else:
            if current_time < next_overdue:
                percentage = calculate_percentage(
                    (current_time - next_due) / overdue_duration)
                return ChoreStatus(ChoreState.DUE, ChoreState.OVERDUE, percentage, next_due, next_overdue)
            else:
                return ChoreStatus(ChoreState.OVERDUE, None, 0, next_due, next_overdue)


class ChoreState(Enum):
    COMPLETED = 1
    DUE = 2
    OVERDUE = 3

    def __str__(self):
        match self:
            case None:
                return ""
            case ChoreState.COMPLETED:
                return "Completed"
            case ChoreState.DUE:
                return "Due"
            case ChoreState.OVERDUE:
                return "Overdue"

        raise ValueError("State value is unexpected")


class ChoreStatus(object):

    def __init__(self,
                 state: Optional[ChoreState],
                 next_state: Optional[ChoreState],
                 percentage: float,
                 next_due: datetime.datetime,
                 next_overdue: Optional[datetime.datetime]):
        self.state = state
        self.next_state = next_state
        self.percentage = percentage
        self.next_due = next_due
        self.next_overdue = next_overdue

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, ChoreStatus)
            and other is not None
            and self.state == other.state
            and self.next_state == other.next_state
            and self.percentage == other.percentage
            and self.next_due == other.next_due
            and self.next_overdue == other.next_overdue
        )

    def __str__(self):
        return "ChoreStatus(state={}, next_state={}, percentage={}, next_due={}, next_overdue={})".format(
            self.state, self.next_state, self.percentage, self.next_due, self.next_overdue
        )

    def __repr__(self) -> str:
        return self.__str__()


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
        self._tags = None

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
        match status.state:
            case ChoreState.COMPLETED:
                return status.percentage
            case ChoreState.DUE:
                return status.percentage + 100
            case ChoreState.OVERDUE:
                return status.percentage + 200

        raise ValueError("State value is unexpected")

    @property
    def tags(self):
        if self._tags is None:
            self._tags = list(map(Tag, self._obj.tags.all()))

        return self._tags


class Log(ModelViewBase[models.Log]):

    def __init__(self, log: models.Log):
        super().__init__(log)

    @property
    def timestamp(self):
        return self._obj.timestamp


class Tag(ModelViewBase[models.Tag]):

    def __init__(self, tag: models.Tag):
        super().__init__(tag)

    @property
    def id(self):
        return self._obj.id

    @property
    def name(self):
        return self._obj.name


class AwayDate(ModelViewBase[models.AwayDate]):

    def __init__(self, away_date: models.AwayDate):
        super().__init__(away_date)

    @property
    def id(self):
        return self._obj.id

    @property
    def name(self):
        return self._obj.name

    @property
    def start_date(self):
        return self._obj.start_date

    @property
    def end_date(self):
        return self._obj.end_date
