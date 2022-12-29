from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Chore(models.Model):
    name = models.CharField("Name", max_length=100)
    description = models.TextField("Description", blank=True)
    due_duration = models.DurationField("Due Duration")
    overdue_duration = models.DurationField(
        "Overdue Duration", null=True, blank=True)
    tags = models.ManyToManyField(
        "Tag", blank=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def clean(self):
        errors = {}

        if self.due_duration is not None and \
                (self.due_duration.seconds != 0 or self.due_duration.microseconds != 0):
            errors["due_duration"] = "The due duration must be specified in days"

        if self.overdue_duration is not None and \
                (self.overdue_duration.seconds != 0 or self.overdue_duration.microseconds != 0):
            errors["overdue_duration"] = "The overdue duration must be specified in days"

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return ("Chore("
                "id={}, name={}, description={}, "
                "due_duration={}, overdue_duration={}, tags={}, user={})").format(
            self.id, self.name, self.description, self.due_duration, self.overdue_duration,
            self.tags, self.user)


class Log(models.Model):
    timestamp = models.DateTimeField("Timestamp")
    chore = models.ForeignKey(Chore, on_delete=models.CASCADE)
    user = models.ForeignKey(
        get_user_model(), on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return "Log(id={}, timestamp={}, chore={}, user={})".format(
            self.id, self.timestamp, self.chore, self.user)


class Tag(models.Model):
    name = models.CharField("Name", max_length=100)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return "Tag(name={}, user={})".format(self.name, self.user)


class AwayDate(models.Model):
    name = models.CharField("Name", max_length=100)
    start_date = models.DateField("Start Date")
    end_date = models.DateField("End Date")
    user = models.ForeignKey(
        get_user_model(), on_delete=models.SET_NULL, null=True)

    def clean(self):
        if self.start_date is not None and self.end_date is not None and self.start_date > self.end_date:
            raise ValidationError(dict(
                start_date="The start date must be on or before the end date",
                end_date="The end date must be on or after the start date",
            ))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return "AwayDate(id={}, name={}, start_date={}, end_date={}, user={}".format(
            self.id, self.name, self.start_date, self.end_date, self.user)
