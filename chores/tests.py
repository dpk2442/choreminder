import datetime
import random
import string

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from chores import forms, models


def create_chore_name() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=20))


class AuthenticatedTest(TestCase):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def create_chore_in_db(self) -> int:
        return models.Chore.objects.create(
            name=create_chore_name(),
            description="Test Description",
            repeat_interval=datetime.timedelta(days=1),
            user=self.user)

    def setUp(self) -> None:
        super().setUp()
        self.user, _ = User.objects.get_or_create(username="test")
        self.user2, _ = User.objects.get_or_create(username="test2")
        self.client.force_login(self.user)


class ChoreIndexViewTests(AuthenticatedTest):

    def test_no_chores(self):
        response = self.client.get(reverse("chores:index"))
        self.assertContains(response, "No chores to display.")
        self.assertQuerysetEqual(response.context["chores"], [])

    def test_some_chores(self):
        chore1 = self.create_chore_in_db()
        chore2 = self.create_chore_in_db()
        response = self.client.get(reverse("chores:index"))
        self.assertContains(response, chore1.name)
        self.assertContains(response, chore2.name)
        self.assertQuerysetEqual(response.context["chores"], [chore1, chore2])

        self.client.force_login(self.user2)
        response = self.client.get(reverse("chores:index"))
        self.assertContains(response, "No chores to display.")
        self.assertQuerysetEqual(response.context["chores"], [])


class LoginTest(TestCase):

    def test_redirects_if_not_logged_in(self):
        response = self.client.get(reverse("chores:index"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "{}?next={}".format(
            reverse("login"), reverse("chores:index")))

    def test_shows_logout_if_logged_in(self):
        user, _ = User.objects.get_or_create(username="test")
        self.client.force_login(user)
        response = self.client.get(reverse("chores:index"))
        self.assertContains(
            response, "<a href=\"{}\">Logout</a>".format(reverse("logout")))


class ChoreAddViewTests(AuthenticatedTest):

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

        # test user 2 cannot list
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


class ChoreEditViewTests(AuthenticatedTest):

    def test_get(self):
        chore = self.create_chore_in_db()
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
        chore = self.create_chore_in_db()
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

        # test user 2 cannot update
        self.client.force_login(self.user2)
        response = self.client.post(reverse("chores:edit_chore", args=(chore.id,)), dict(
            name=chore.name,
            description="updated by another user",
            repeat_interval="1 day",
        ))
        self.assertEqual(response.status_code, 404)
        chore = models.Chore.objects.get(pk=chore.id)
        self.assertEqual(chore.description, "edited description")

    def test_post_invalid(self):
        chore = self.create_chore_in_db()
        response = self.client.post(reverse("chores:edit_chore", args=(chore.id,)), dict(
            name=chore.name,
        ))

        self.assertContains(response, "This field is required.", 2)
        chore = models.Chore.objects.get(pk=chore.id)
        self.assertNotEqual(chore.description, "edited description")


class ChoreDeleteViewTests(AuthenticatedTest):

    def test_get(self):
        chore = self.create_chore_in_db()
        response = self.client.get(
            reverse("chores:delete_chore", args=(chore.id,)))
        self.assertContains(
            response, "Are you sure you want to delete \"{}\"".format(chore.name))

    def test_get_does_not_exist(self):
        response = self.client.get(reverse("chores:delete_chore", args=(0,)))
        self.assertEqual(response.status_code, 404)

    def test_post(self):
        chore = self.create_chore_in_db()
        response = self.client.post(
            reverse("chores:delete_chore", args=(chore.id,)))
        self.assertRedirects(response, reverse("chores:index"))

        chores = models.Chore.objects.filter(pk=chore.id)
        self.assertQuerysetEqual(chores, [])

    def test_other_user_delete(self):
        chore = self.create_chore_in_db()
        self.client.force_login(self.user2)
        response = self.client.post(
            reverse("chores:delete_chore", args=(chore.id,)))
        self.assertEqual(response.status_code, 404)
