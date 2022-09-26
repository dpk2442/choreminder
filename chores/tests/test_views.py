import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.template import defaultfilters
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from chores import forms, models
from .utils import create_chore_name


class AuthenticatedTest(TestCase):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def create_chore_in_db(self) -> models.Chore:
        return models.Chore.objects.create(
            name=create_chore_name(),
            description="Test Description",
            due_duration=datetime.timedelta(days=1),
            overdue_duration=datetime.timedelta(),
            user=self.user)

    def create_log_in_db(self, chore: models.Chore) -> models.Log:
        return models.Log.objects.create(
            timestamp=timezone.now(),
            chore=chore,
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

        # test user 2 cannot list
        self.client.force_login(self.user2)
        response = self.client.get(reverse("chores:index"))
        self.assertContains(response, "No chores to display.")
        self.assertQuerysetEqual(response.context["chores"], [])

    def test_shows_latest_log(self):
        chore = self.create_chore_in_db()
        log = self.create_log_in_db(chore)
        response = self.client.get(reverse("chores:index"))
        self.assertContains(response, defaultfilters.date(
            timezone.localtime(log.timestamp), settings.DATETIME_FORMAT))


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
            due_duration="1 day",
            overdue_duration="0",
        ))
        self.assertRedirects(response, reverse("chores:index"))

        chore: models.Chore = models.Chore.objects.get(name=chore_name)
        self.assertEqual(chore.name, chore_name)
        self.assertEqual(chore.description, "description")
        self.assertEqual(chore.due_duration, datetime.timedelta(days=1))
        self.assertEqual(chore.overdue_duration, datetime.timedelta())

    def test_post_invalid(self):
        chore_name = create_chore_name()
        response = self.client.post(reverse("chores:add_chore"), dict(
            name=chore_name,
        ))

        self.assertContains(response, "This field is required.", 3)
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
            due_duration="1 day",
            overdue_duration="0",
        ))
        self.assertRedirects(response, reverse("chores:index"))

        chore: models.Chore = models.Chore.objects.get(pk=chore.id)
        self.assertEqual(chore.name, chore.name)
        self.assertEqual(chore.description, "edited description")
        self.assertEqual(chore.due_duration, datetime.timedelta(days=1))
        self.assertEqual(chore.overdue_duration, datetime.timedelta())

        # test user 2 cannot update
        self.client.force_login(self.user2)
        response = self.client.post(reverse("chores:edit_chore", args=(chore.id,)), dict(
            name=chore.name,
            description="updated by another user",
            due_duration="1 day",
        ))
        self.assertEqual(response.status_code, 404)
        chore = models.Chore.objects.get(pk=chore.id)
        self.assertEqual(chore.description, "edited description")

    def test_post_invalid(self):
        chore = self.create_chore_in_db()
        response = self.client.post(reverse("chores:edit_chore", args=(chore.id,)), dict(
            name=chore.name,
        ))

        self.assertContains(response, "This field is required.", 3)
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


class ChoreLogViewTests(AuthenticatedTest):

    def test_unknown_chore(self):
        response = self.client.post(reverse("chores:log_chore", args=(1,)))
        self.assertEqual(response.status_code, 404)

    def test_success(self):
        chore = self.create_chore_in_db()
        response = self.client.post(
            reverse("chores:log_chore", args=(chore.id,)))
        self.assertRedirects(response, reverse("chores:index"))
        self.assertIsNotNone(chore.latest_log())
