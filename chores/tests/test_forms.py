from django.test import TestCase

from chores import forms, models
from .utils import create_random_user, create_tag, get_user


class TestTagChoiceField(TestCase):

    def test_label_from_instance(self):
        user = get_user()
        tag = create_tag(user)
        field = forms.TagChoiceField(queryset=models.Tag.objects.all())
        self.assertEquals(field.label_from_instance(tag), tag.name)


class TestChoreForm(TestCase):

    def test_init(self):
        user1 = create_random_user()
        user2 = create_random_user()
        tag = create_tag(user1)

        form = forms.ChoreForm(user1)
        self.assertQuerysetEqual(form.fields["tags"].queryset, [tag])

        form = forms.ChoreForm(user2)
        self.assertQuerysetEqual(form.fields["tags"].queryset, [])
