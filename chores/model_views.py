from django.utils import timezone

from chores import models


class Chore(object):

    def __init__(self, chore: models.Chore):
        self._chore = chore
        self._fetched_latest_log = False
        self._latest_log = None

    @property
    def id(self):
        return self._chore.id

    @property
    def name(self):
        return self._chore.name

    @property
    def description(self):
        return self._chore.description

    @property
    def latest_log(self):
        if not self._fetched_latest_log:
            db_log = self._chore.log_set.order_by("-timestamp").first()
            if db_log is not None:
                self._latest_log = Log(db_log)

        return self._latest_log

    def next_due(self):
        if self.latest_log is None:
            return None

        return self.latest_log.timestamp + self._chore.due_duration

    def display_status(self):
        now = timezone.now()
        next_due = self.next_due()
        if next_due is None:
            return "N/A"

        overdue = next_due + self._chore.overdue_duration
        if next_due > now:
            return "Completed"
        elif now < overdue:
            return "Due"
        else:
            return "Overdue"

    def __str__(self) -> str:
        return str(self._chore)

    def __eq__(self, other) -> bool:
        return isinstance(other, Chore) and self._chore == other._chore


class Log(object):

    def __init__(self, log: models.Log):
        self._log = log

    @property
    def timestamp(self):
        return self._log.timestamp

    def __str__(self) -> str:
        return str(self._log)

    def __eq__(self, other) -> bool:
        return isinstance(other, Log) and self._log == other._log
