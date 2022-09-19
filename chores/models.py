from django.db import models


class Chore(models.Model):
    name = models.CharField("Name", max_length=100)
    description = models.TextField("Description")
    repeat_interval = models.DurationField("Repeat Interval")
