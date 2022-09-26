from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone


class Chore(models.Model):
    name = models.CharField("Name", max_length=100)
    description = models.TextField("Description")
    due_duration = models.DurationField("Due Duration")
    overdue_duration = models.DurationField("Overdue Duration")
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def latest_log(self):
        return self.log_set.order_by("-timestamp").first()

    def next_due(self):
        latest_log = self.latest_log()
        if latest_log is None:
            return None

        return self.latest_log().timestamp + self.due_duration

    def display_status(self):
        now = timezone.now()
        next_due = self.next_due()
        if next_due is None:
            return "N/A"

        overdue = next_due + self.overdue_duration
        if next_due > now:
            return "Completed"
        elif now < overdue:
            return "Due"
        else:
            return "Overdue"

    def __str__(self):
        return ("Chore("
                "id={}, name={}, description={}, "
                "due_duration={}, overdue_duration={}, user={})").format(
            self.id, self.name, self.description, self.due_duration, self.overdue_duration, self.user)


class Log(models.Model):
    timestamp = models.DateTimeField("Timestamp")
    chore = models.ForeignKey(Chore, on_delete=models.CASCADE)
    user = models.ForeignKey(
        get_user_model(), on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return "Log(id={}, timestamp={}, chore={}, user={})".format(
            self.id, self.timestamp, self.chore, self.user)
