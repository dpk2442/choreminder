from django import forms

from chores import models
from chores.type_helpers import UserType


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
            "due_duration": "The number of days since last completion before a task is considered due.",
            "overdue_duration": "The number of days after a task is due before a it is considered overdue.",
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


class AwayDateForm(forms.ModelForm):
    class Meta:
        model = models.AwayDate
        fields = ["name", "start_date", "end_date"]
        widgets = {
            "start_date": forms.DateInput(attrs=dict(type="date")),
            "end_date": forms.DateInput(attrs=dict(type="date")),
        }
