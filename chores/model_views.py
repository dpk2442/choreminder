from typing import Generic, TypeVar

from django.db.models import Model as DjangoModel
from django.utils import timezone

from chores import models

DjangoModelType = TypeVar("DjangoModelType", bound=DjangoModel)


class ModelViewBase(Generic[DjangoModelType]):

    def __init__(self, obj: DjangoModelType):
        self._obj = obj

    def __str__(self) -> str:
        return str(self._obj)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ModelViewBase) and self._obj == other._obj


class Chore(ModelViewBase):

    def __init__(self, chore: models.Chore):
        super().__init__(chore)
        self._fetched_latest_log = False
        self._latest_log = None

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

    def next_due(self):
        if self.latest_log is None:
            return None

        return self.latest_log.timestamp + self._obj.due_duration

    def display_status(self):
        now = timezone.now()
        next_due = self.next_due()
        if next_due is None:
            return "N/A"

        overdue = next_due + self._obj.overdue_duration
        if next_due > now:
            return "Completed"
        elif now < overdue:
            return "Due"
        else:
            return "Overdue"


class Log(ModelViewBase):

    def __init__(self, log: models.Log):
        super().__init__(log)

    @property
    def timestamp(self):
        return self._obj.timestamp
