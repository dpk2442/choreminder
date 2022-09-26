from django import forms

from chores import models


class ChoreForm(forms.ModelForm):
    class Meta:
        model = models.Chore
        fields = ["name", "description", "due_duration", "overdue_duration"]
        help_texts = {
            "due_duration": "The amount of time since last completion before a task is considered due.",
            "overdue_duration": "The amount of time after a task is due before a it is considered overdue.",
        }
