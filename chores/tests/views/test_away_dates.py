from datetime import timedelta

from django.conf import settings
from django.template import defaultfilters
from django.urls import reverse
from django.utils import timezone

from chores import forms, model_views, models

from ..utils import create_random_string
from .utils import AuthenticatedTest


class AwayDatesListViewTests(AuthenticatedTest):

    def test_no_away_dates(self):
        response = self.client.get(reverse("chores:list_away_dates"))
        self.assertContains(response, "No away dates to display.")
        self.assertEqual(response.context["away_dates"], [])

    def test_some_away_dates(self):
        away_date1 = self.create_away_date_in_db()
        away_date2 = self.create_away_date_in_db()
        response = self.client.get(reverse("chores:list_away_dates"))
        self.assertContains(response, away_date1.name)
        self.assertContains(response, away_date2.name)
        self.assertEqual(response.context["away_dates"], [
                         model_views.Chore(away_date1), model_views.Chore(away_date2)])

        # test user 2 cannot list
        self.client.force_login(self.user2)
        response = self.client.get(reverse("chores:list_away_dates"))
        self.assertContains(response, "No away dates to display.")
        self.assertEqual(response.context["away_dates"], [])

    def test_away_dates_date_range(self):
        yesterday = timezone.now().today() - timedelta(days=1)
        away_date1 = self.create_away_date_in_db()
        away_date2 = self.create_away_date_in_db(
            start_date=yesterday, end_date=yesterday)
        response = self.client.get(reverse("chores:list_away_dates"))

        self.assertContains(response, "({} - {})".format(
            defaultfilters.date(away_date1.start_date, settings.DATE_FORMAT),
            defaultfilters.date(away_date1.end_date, settings.DATE_FORMAT),
        ))
        self.assertContains(response, "({})".format(
            defaultfilters.date(away_date2.start_date, settings.DATE_FORMAT),
        ))


class AwayDateAddViewTests(AuthenticatedTest):

    def test_get(self):
        response = self.client.get(reverse("chores:add_away_date"))
        self.assertContains(response, "Name")
        self.assertIsNotNone(response.context["form"])
        self.assertIsInstance(response.context["form"], forms.AwayDateForm)

    def test_post_valid(self):
        away_date_name = create_random_string()
        away_date_start_date = timezone.now().today()
        away_date_end_date = away_date_start_date + timedelta(days=1)
        response = self.client.post(reverse("chores:add_away_date"), dict(
            name=away_date_name,
            start_date=away_date_start_date.strftime("%Y-%m-%d"),
            end_date=away_date_end_date.strftime("%Y-%m-%d"),
        ))
        self.assertRedirects(response, reverse("chores:list_away_dates"))

        chore: models.AwayDate = models.AwayDate.objects.get(
            name=away_date_name)
        self.assertEqual(chore.name, away_date_name)

    def test_post_invalid(self):
        response = self.client.post(reverse("chores:add_away_date"), dict())

        self.assertContains(response, "This field is required.", 3)
        self.assertQuerysetEqual(models.AwayDate.objects.all(), [])


class AwayDateEditViewTests(AuthenticatedTest):

    def test_get(self):
        away_date = self.create_away_date_in_db()
        response = self.client.get(
            reverse("chores:edit_away_date", args=(away_date.id,)))
        self.assertContains(response, away_date.name)

        form = response.context["form"]
        self.assertIsNotNone(form)
        self.assertIsInstance(form, forms.AwayDateForm)
        self.assertEqual(form.instance, away_date)

    def test_get_does_not_exist(self):
        response = self.client.get(reverse("chores:edit_away_date", args=(0,)))
        self.assertEqual(response.status_code, 404)

    def test_post_valid(self):
        away_date = self.create_away_date_in_db()
        new_away_date_name = create_random_string()
        new_away_date_start_date = timezone.now().today()
        new_away_date_end_date = new_away_date_start_date + timedelta(days=1)
        response = self.client.post(reverse("chores:edit_away_date", args=(away_date.id,)), dict(
            name=new_away_date_name,
            start_date=new_away_date_start_date.strftime("%Y-%m-%d"),
            end_date=new_away_date_end_date.strftime("%Y-%m-%d"),
        ))
        self.assertRedirects(response, reverse("chores:list_away_dates"))

        away_date: models.AwayDate = models.AwayDate.objects.get(
            pk=away_date.id)
        self.assertEqual(away_date.name, new_away_date_name)

        # test user 2 cannot update
        self.client.force_login(self.user2)
        response = self.client.post(reverse("chores:edit_away_date", args=(away_date.id,)), dict(
            name="failed edit",
        ))
        self.assertEqual(response.status_code, 404)
        away_date = models.AwayDate.objects.get(pk=away_date.id)
        self.assertEqual(away_date.name, new_away_date_name)

    def test_post_invalid(self):
        away_date = self.create_away_date_in_db()
        response = self.client.post(
            reverse("chores:edit_away_date", args=(away_date.id,)), dict())

        self.assertContains(response, "This field is required.", 3)


class AwayDateDeleteViewTests(AuthenticatedTest):

    def test_get(self):
        away_date = self.create_away_date_in_db()
        response = self.client.get(
            reverse("chores:delete_away_date", args=(away_date.id,)))
        self.assertContains(
            response, "Are you sure you want to delete \"{}\"".format(away_date.name))

    def test_get_does_not_exist(self):
        response = self.client.get(
            reverse("chores:delete_away_date", args=(0,)))
        self.assertEqual(response.status_code, 404)

    def test_post(self):
        away_date = self.create_away_date_in_db()
        response = self.client.post(
            reverse("chores:delete_away_date", args=(away_date.id,)))
        self.assertRedirects(response, reverse("chores:list_away_dates"))

        away_dates = models.AwayDate.objects.filter(pk=away_date.id)
        self.assertQuerysetEqual(away_dates, [])

    def test_other_user_delete(self):
        away_date = self.create_away_date_in_db()
        self.client.force_login(self.user2)
        response = self.client.post(
            reverse("chores:delete_away_date", args=(away_date.id,)))
        self.assertEqual(response.status_code, 404)
