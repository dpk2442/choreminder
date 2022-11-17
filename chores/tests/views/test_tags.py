from django.urls import reverse

from chores import forms, model_views, models
from ..utils import create_random_string
from .utils import AuthenticatedTest


class TagsListViewTests(AuthenticatedTest):

    def test_no_tags(self):
        response = self.client.get(reverse("chores:list_tags"))
        self.assertContains(response, "No tags to display.")
        self.assertEqual(response.context["tags"], [])

    def test_some_tags(self):
        tag1 = self.create_tag_in_db()
        tag2 = self.create_tag_in_db()
        response = self.client.get(reverse("chores:list_tags"))
        self.assertContains(response, tag1.name)
        self.assertContains(response, tag2.name)
        self.assertEqual(response.context["tags"], [
                         model_views.Chore(tag1), model_views.Chore(tag2)])

        # test user 2 cannot list
        self.client.force_login(self.user2)
        response = self.client.get(reverse("chores:list_tags"))
        self.assertContains(response, "No tags to display.")
        self.assertEqual(response.context["tags"], [])


class TagAddViewTests(AuthenticatedTest):

    def test_get(self):
        response = self.client.get(reverse("chores:add_tag"))
        self.assertContains(response, "Name")
        self.assertIsNotNone(response.context["form"])
        self.assertIsInstance(response.context["form"], forms.TagForm)

    def test_post_valid(self):
        tag_name = create_random_string()
        response = self.client.post(reverse("chores:add_tag"), dict(
            name=tag_name,
        ))
        self.assertRedirects(response, reverse("chores:list_tags"))

        chore: models.Tag = models.Tag.objects.get(
            name=tag_name)
        self.assertEqual(chore.name, tag_name)

    def test_post_invalid(self):
        response = self.client.post(reverse("chores:add_tag"), dict())

        self.assertContains(response, "This field is required.", 1)
        self.assertQuerysetEqual(models.Tag.objects.all(), [])


class TagEditViewTests(AuthenticatedTest):

    def test_get(self):
        tag = self.create_tag_in_db()
        response = self.client.get(
            reverse("chores:edit_tag", args=(tag.id,)))
        self.assertContains(response, tag.name)

        form = response.context["form"]
        self.assertIsNotNone(form)
        self.assertIsInstance(form, forms.TagForm)
        self.assertEqual(form.instance, tag)

    def test_get_does_not_exist(self):
        response = self.client.get(reverse("chores:edit_tag", args=(0,)))
        self.assertEqual(response.status_code, 404)

    def test_post_valid(self):
        tag = self.create_tag_in_db()
        new_tag_name = create_random_string()
        response = self.client.post(reverse("chores:edit_tag", args=(tag.id,)), dict(
            name=new_tag_name,
        ))
        self.assertRedirects(response, reverse("chores:list_tags"))

        tag: models.Tag = models.Tag.objects.get(pk=tag.id)
        self.assertEqual(tag.name, new_tag_name)

        # test user 2 cannot update
        self.client.force_login(self.user2)
        response = self.client.post(reverse("chores:edit_tag", args=(tag.id,)), dict(
            name="failed edit",
        ))
        self.assertEqual(response.status_code, 404)
        tag = models.Tag.objects.get(pk=tag.id)
        self.assertEqual(tag.name, new_tag_name)

    def test_post_invalid(self):
        tag = self.create_tag_in_db()
        response = self.client.post(
            reverse("chores:edit_tag", args=(tag.id,)), dict())

        self.assertContains(response, "This field is required.", 1)


class TagDeleteViewTests(AuthenticatedTest):

    def test_get(self):
        tag = self.create_tag_in_db()
        response = self.client.get(
            reverse("chores:delete_tag", args=(tag.id,)))
        self.assertContains(
            response, "Are you sure you want to delete \"{}\"".format(tag.name))

    def test_get_does_not_exist(self):
        response = self.client.get(
            reverse("chores:delete_tag", args=(0,)))
        self.assertEqual(response.status_code, 404)

    def test_post(self):
        tag = self.create_tag_in_db()
        response = self.client.post(
            reverse("chores:delete_tag", args=(tag.id,)))
        self.assertRedirects(response, reverse("chores:list_tags"))

        tags = models.Tag.objects.filter(pk=tag.id)
        self.assertQuerysetEqual(tags, [])

    def test_other_user_delete(self):
        tag = self.create_tag_in_db()
        self.client.force_login(self.user2)
        response = self.client.post(
            reverse("chores:delete_tag", args=(tag.id,)))
        self.assertEqual(response.status_code, 404)
