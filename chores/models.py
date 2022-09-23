from django.contrib.auth import get_user_model
from django.db import models


class Chore(models.Model):
    name = models.CharField("Name", max_length=100)
    description = models.TextField("Description")
    repeat_interval = models.DurationField("Repeat Interval")
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def latest_log(self):
        return self.log_set.order_by("-timestamp").first()

    def __str__(self):
        return "Chore(id={}, name={}, description={}, repeat_interval={}, user={})".format(
            self.id, self.name, self.description, self.repeat_interval, self.user)


class Log(models.Model):
    timestamp = models.DateTimeField("Timestamp")
    chore = models.ForeignKey(Chore, on_delete=models.CASCADE)
    user = models.ForeignKey(
        get_user_model(), on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return "Log(id={}, timestamp={}, chore={}, user={})".format(
            self.id, self.timestamp, self.chore, self.user)
