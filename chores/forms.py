from typing import Union

from django import forms
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser

from chores import models


class TagChoiceField(forms.ModelMultipleChoiceField):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def label_from_instance(self, tag: models.Tag) -> str:
        return tag.name


class ChoreForm(forms.ModelForm):
    class Meta:
        model = models.Chore
        fields = ["name", "tags", "description",
                  "due_duration", "overdue_duration"]
        field_classes = {
            "tags": TagChoiceField
        }
        labels = {
            "overdue_duration": "Overdue Duration (Optional)"
        }
        help_texts = {
            "due_duration": "The amount of time since last completion before a task is considered due.",
            "overdue_duration": "The amount of time after a task is due before a it is considered overdue.",
        }

    def __init__(self, user: Union[AbstractBaseUser, AnonymousUser], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tags"].queryset = models.Tag.objects.filter(user=user)


class TagForm(forms.ModelForm):
    class Meta:
        model = models.Tag
        fields = ["name"]
