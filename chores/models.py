from django.contrib.auth import get_user_model
from django.db import models


class Chore(models.Model):
    name = models.CharField("Name", max_length=100)
    description = models.TextField("Description")
    repeat_interval = models.DurationField("Repeat Interval")
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return "Chore(name={}, description={}, repeat_interval={}, user={})".format(
            self.name, self.description, self.repeat_interval, self.user)
