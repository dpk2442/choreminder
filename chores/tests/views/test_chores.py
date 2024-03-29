import datetime
from collections import OrderedDict

from django.conf import settings
from django.template import defaultfilters
from django.urls import reverse
from django.utils import timezone

from chores import forms, model_views, models

from ..utils import create_random_string
from .utils import AuthenticatedTest


def build_chore_groups(pending_list, completed_list):
    return OrderedDict((
        ("Pending", pending_list),
        ("Completed", completed_list),
    ))


class ChoreIndexViewTests(AuthenticatedTest):

    def test_no_chores(self):
        response = self.client.get(reverse("chores:index"))
        self.assertContains(response, "No chores to display.")
        self.assertEqual(
            response.context["chore_groups"], build_chore_groups([], []))

    def test_some_chores(self):
        chore1 = self.create_chore_in_db()
        chore2 = self.create_chore_in_db()
        response = self.client.get(reverse("chores:index"))
        self.assertContains(response, chore1.name)
        self.assertContains(response, chore2.name)
        self.assertEqual(response.context["chore_groups"], build_chore_groups(
            [model_views.Chore(chore1), model_views.Chore(chore2)], []))

        # test user 2 cannot list
        self.client.force_login(self.user2)
        response = self.client.get(reverse("chores:index"))
        self.assertContains(response, "No chores to display.")
        self.assertEqual(
            response.context["chore_groups"], build_chore_groups([], []))

    def test_shows_next_due_and_status(self):
        chore = self.create_chore_in_db()
        log = self.create_log_in_db(chore)
        response = self.client.get(reverse("chores:index"))
        self.assertContains(response, "Completed")
        self.assertContains(response, defaultfilters.date(timezone.localtime(
            log.timestamp + datetime.timedelta(days=1)), settings.DATETIME_FORMAT))

    def test_shows_tags(self):
        tag1 = self.create_tag_in_db()
        tag2 = self.create_tag_in_db()
        _ = self.create_chore_in_db(tags=[tag1, tag2])
        response = self.client.get(reverse("chores:index"))
        self.assertContains(response, tag1.name)
        self.assertContains(response, tag2.name)

    def test_tag_filter(self):
        tag1 = self.create_tag_in_db()
        tag2 = self.create_tag_in_db()
        chore1 = self.create_chore_in_db(tags=[tag1])
        chore2 = self.create_chore_in_db(tags=[tag1, tag2])
        chore3 = self.create_chore_in_db(tags=[tag2])
        chore4 = self.create_chore_in_db()

        response = self.client.get(f"{reverse('chores:index')}?tag=")
        self.assertContains(response, chore1.name)
        self.assertContains(response, chore2.name)
        self.assertContains(response, chore3.name)
        self.assertContains(response, chore4.name)

        response = self.client.get(f"{reverse('chores:index')}?tag={tag1.id}")
        self.assertContains(response, chore1.name)
        self.assertContains(response, chore2.name)
        self.assertNotContains(response, chore3.name)
        self.assertNotContains(response, chore4.name)

        response = self.client.get(f"{reverse('chores:index')}?tag={tag2.id}")
        self.assertNotContains(response, chore1.name)
        self.assertContains(response, chore2.name)
        self.assertContains(response, chore3.name)
        self.assertNotContains(response, chore4.name)

    def test_chore_with_no_log_renders_not_completed(self):
        _ = self.create_chore_in_db()
        response = self.client.get(reverse("chores:index"))
        self.assertContains(response, "Never Completed")

    def test_clear_filters_rendered_only_when_filtering(self):
        tag = self.create_tag_in_db()
        _ = self.create_chore_in_db()

        response = self.client.get(reverse("chores:index"))
        self.assertNotContains(
            response, '<a class="button" href="/">Clear Filter</a>')

        response = self.client.get(f"{reverse('chores:index')}?tag={tag.id}")
        self.assertContains(
            response, '<a class="button" href="/">Clear Filter</a>')

    def test_chore_count_rendered(self):
        chore1 = self.create_chore_in_db()
        chore2 = self.create_chore_in_db()

        response = self.client.get(reverse("chores:index"))
        self.assertContains(response, "Pending (2)")
        self.assertContains(response, "Completed (0)")

        self.create_log_in_db(chore1)
        response = self.client.get(reverse("chores:index"))
        self.assertContains(response, "Pending (1)")
        self.assertContains(response, "Completed (1)")

        self.create_log_in_db(chore2)
        response = self.client.get(reverse("chores:index"))
        self.assertContains(response, "Pending (0)")
        self.assertContains(response, "Completed (2)")


class ChoreAddViewTests(AuthenticatedTest):

    def test_get(self):
        response = self.client.get(reverse("chores:add_chore"))
        self.assertContains(response, "Name")
        self.assertContains(response, "Tags")
        self.assertContains(response, "Description")
        self.assertContains(response, "Due Duration")
        self.assertContains(response, "Overdue Duration")
        self.assertIsNotNone(response.context["form"])
        self.assertIsInstance(response.context["form"], forms.ChoreForm)

    def test_post_valid(self):
        chore_name = create_random_string()
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

    def test_post_valid_no_overdue(self):
        chore_name = create_random_string()
        response = self.client.post(reverse("chores:add_chore"), dict(
            name=chore_name,
            description="description",
            due_duration="1 day",
        ))
        self.assertRedirects(response, reverse("chores:index"))

        chore: models.Chore = models.Chore.objects.get(name=chore_name)
        self.assertEqual(chore.name, chore_name)
        self.assertEqual(chore.description, "description")
        self.assertEqual(chore.due_duration, datetime.timedelta(days=1))
        self.assertIsNone(chore.overdue_duration)

    def test_post_invalid(self):
        chore_name = create_random_string()
        response = self.client.post(reverse("chores:add_chore"), dict(
            name=chore_name,
        ))

        self.assertContains(response, "This field is required.", 1)
        self.assertQuerySetEqual(
            models.Chore.objects.filter(name=chore_name), [])

    def test_description_optional(self):
        chore_name = create_random_string()
        response = self.client.post(reverse("chores:add_chore"), dict(
            name=chore_name,
            due_duration="1 day",
        ))
        self.assertRedirects(response, reverse("chores:index"))

        chore: models.Chore = models.Chore.objects.get(name=chore_name)
        self.assertEqual(chore.name, chore_name)
        self.assertEqual(chore.description, "")


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
            dte_duration="1 day",
        ))
        self.assertEqual(response.status_code, 404)
        chore = models.Chore.objects.get(pk=chore.id)
        self.assertEqual(chore.description, "edited description")

    def test_post_valid_remove_overdue(self):
        chore = self.create_chore_in_db()
        response = self.client.post(reverse("chores:edit_chore", args=(chore.id,)), dict(
            name=chore.name,
            description="edited description",
            due_duration="1 day",
        ))
        self.assertRedirects(response, reverse("chores:index"))

        chore: models.Chore = models.Chore.objects.get(pk=chore.id)
        self.assertEqual(chore.name, chore.name)
        self.assertEqual(chore.description, "edited description")
        self.assertEqual(chore.due_duration, datetime.timedelta(days=1))
        self.assertIsNone(chore.overdue_duration)

    def test_post_invalid(self):
        chore = self.create_chore_in_db()
        response = self.client.post(reverse("chores:edit_chore", args=(chore.id,)), dict(
            name=chore.name,
        ))

        self.assertContains(response, "This field is required.", 1)
        chore = models.Chore.objects.get(pk=chore.id)
        self.assertNotEqual(chore.description, "edited description")

    def test_description_optional(self):
        chore = self.create_chore_in_db()
        response = self.client.post(reverse("chores:edit_chore", args=(chore.id,)), dict(
            name=chore.name,
            due_duration="1 day",
            overdue_duration="0",
        ))
        self.assertRedirects(response, reverse("chores:index"))

        chore: models.Chore = models.Chore.objects.get(pk=chore.id)
        self.assertEqual(chore.name, chore.name)
        self.assertEqual(chore.description, "")
        self.assertEqual(chore.due_duration, datetime.timedelta(days=1))
        self.assertEqual(chore.overdue_duration, datetime.timedelta())


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
        self.assertQuerySetEqual(chores, [])

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
        self.assertEqual(chore.log_set.count(), 1)

    def test_redirects_using_referer(self):
        chore = self.create_chore_in_db()
        response = self.client.post(
            reverse("chores:log_chore", args=(chore.id,)), HTTP_REFERER="http://example.com/path/?tag=1")
        self.assertRedirects(response, f"{reverse('chores:index')}?tag=1")

    def test_ignores_empty_tag_query(self):
        chore = self.create_chore_in_db()
        response = self.client.post(
            reverse("chores:log_chore", args=(chore.id,)), HTTP_REFERER="/?tag=")
        self.assertRedirects(response, reverse("chores:index"))

    def test_htmx_returns_rendered_chore_list(self):
        chore = self.create_chore_in_db()
        response = self.client.post(
            reverse("chores:log_chore", args=(chore.id,)), headers={"HX-Request": "true"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, chore.id)
