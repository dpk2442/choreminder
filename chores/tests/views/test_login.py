from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


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
