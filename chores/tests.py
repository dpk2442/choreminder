import datetime
import random
import string

from django.test import TestCase
from django.urls import reverse

from chores import forms, models


def create_chore_name() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=20))


def create_chore_in_db() -> int:
    return models.Chore.objects.create(
        name=create_chore_name(), description="Test Description", repeat_interval=datetime.timedelta(days=1))


class ChoreIndexViewTests(TestCase):

    def test_no_chores(self):
        response = self.client.get(reverse("chores:index"))
        self.assertContains(response, "No chores to display.")
        self.assertQuerysetEqual(response.context["chores"], [])

    def test_some_chores(self):
        chore1 = create_chore_in_db()
        chore2 = create_chore_in_db()
        response = self.client.get(reverse("chores:index"))
        self.assertContains(response, chore1.name)
        self.assertContains(response, chore2.name)
        self.assertQuerysetEqual(response.context["chores"], [chore1, chore2])


class ChoreAddViewTests(TestCase):

    def test_get(self):
        response = self.client.get(reverse("chores:add_chore"))
        self.assertContains(response, "Name")
        self.assertIsNotNone(response.context["form"])
        self.assertIsInstance(response.context["form"], forms.ChoreForm)

    def test_post_valid(self):
        chore_name = create_chore_name()
        response = self.client.post(reverse("chores:add_chore"), dict(
            name=chore_name,
            description="description",
            repeat_interval="1 day",
        ))
        self.assertRedirects(response, reverse("chores:index"))

        chore = models.Chore.objects.get(name=chore_name)
        self.assertEqual(chore.name, chore_name)
        self.assertEqual(chore.description, "description")
        self.assertEqual(chore.repeat_interval, datetime.timedelta(days=1))

    def test_post_invalid(self):
        chore_name = create_chore_name()
        response = self.client.post(reverse("chores:add_chore"), dict(
            name=chore_name,
        ))

        self.assertContains(response, "This field is required.", 2)
        self.assertQuerysetEqual(
            models.Chore.objects.filter(name=chore_name), [])


class ChoreEditViewTests(TestCase):

    def test_get(self):
        chore = create_chore_in_db()
        response = self.client.get(
            reverse("chores:edit_chore", args=(chore.id,)))
        self.assertContains(response, chore.name)

        form = response.context["form"]
        self.assertIsNotNone(form)
        self.assertIsInstance(form, forms.ChoreForm)
        self.assertEqual(form.instance, chore)

    def test_get_does_not_exist(self):
        response = self.client.get(reverse("chores:edit_chore", args=(0,)))
        self.assertEqual(response.status_code, 404)

    def test_post_valid(self):
        chore = create_chore_in_db()
        response = self.client.post(reverse("chores:edit_chore", args=(chore.id,)), dict(
            name=chore.name,
            description="edited description",
            repeat_interval="1 day",
        ))
        self.assertRedirects(response, reverse("chores:index"))

        chore = models.Chore.objects.get(pk=chore.id)
        self.assertEqual(chore.name, chore.name)
        self.assertEqual(chore.description, "edited description")
        self.assertEqual(chore.repeat_interval, datetime.timedelta(days=1))

    def test_post_invalid(self):
        chore = create_chore_in_db()
        response = self.client.post(reverse("chores:edit_chore", args=(chore.id,)), dict(
            name=chore.name,
        ))

        self.assertContains(response, "This field is required.", 2)
        chore = models.Chore.objects.get(pk=chore.id)
        self.assertNotEqual(chore.description, "edited description")


class ChoreDeleteViewTests(TestCase):

    def test_get(self):
        chore = create_chore_in_db()
        response = self.client.get(
            reverse("chores:delete_chore", args=(chore.id,)))
        self.assertContains(
            response, "Are you sure you want to delete \"{}\"".format(chore.name))

    def test_get_does_not_exist(self):
        response = self.client.get(reverse("chores:delete_chore", args=(0,)))
        self.assertEqual(response.status_code, 404)

    def test_post(self):
        chore = create_chore_in_db()
        response = self.client.post(
            reverse("chores:delete_chore", args=(chore.id,)))
        self.assertRedirects(response, reverse("chores:index"))

        chores = models.Chore.objects.filter(pk=chore.id)
        self.assertQuerysetEqual(chores, [])
