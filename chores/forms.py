from django import forms

from chores import models


class ChoreForm(forms.ModelForm):
    class Meta:
        model = models.Chore
        fields = ["name", "description", "repeat_interval"]
