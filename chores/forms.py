from django import forms

from chores import models
from chores.typing import UserType


class TagChoiceField(forms.ModelChoiceField):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def label_from_instance(self, tag: models.Tag) -> str:
        return tag.name


class TagMultipleChoiceField(forms.ModelMultipleChoiceField):

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
            "tags": TagMultipleChoiceField
        }
        labels = {
            "overdue_duration": "Overdue Duration (Optional)"
        }
        help_texts = {
            "due_duration": "The amount of time since last completion before a task is considered due.",
            "overdue_duration": "The amount of time after a task is due before a it is considered overdue.",
        }

    def __init__(self, user: UserType, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tags"].queryset = models.Tag.objects.filter(user=user)


class TagForm(forms.ModelForm):
    class Meta:
        model = models.Tag
        fields = ["name"]


class TagFilterForm(forms.Form):
    tag = TagChoiceField(queryset=None, required=False)

    def __init__(self, user: UserType, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tag"].queryset = models.Tag.objects.filter(user=user)

    def has_tags(self):
        return len(self.fields["tag"].queryset) != 0
