from django.urls import reverse

from chores import forms, model_views, models
from ..utils import create_random_string
from .test_chores import AuthenticatedTest


class CategoriesListViewTests(AuthenticatedTest):

    def test_no_categories(self):
        response = self.client.get(reverse("chores:list_categories"))
        self.assertContains(response, "No categories to display.")
        self.assertEqual(response.context["categories"], [])

    def test_some_categories(self):
        category1 = self.create_category_in_db()
        category2 = self.create_category_in_db()
        response = self.client.get(reverse("chores:list_categories"))
        self.assertContains(response, category1.name)
        self.assertContains(response, category2.name)
        self.assertEqual(response.context["categories"], [
                         model_views.Chore(category1), model_views.Chore(category2)])

        # test user 2 cannot list
        self.client.force_login(self.user2)
        response = self.client.get(reverse("chores:list_categories"))
        self.assertContains(response, "No categories to display.")
        self.assertEqual(response.context["categories"], [])


class CategoryAddViewTests(AuthenticatedTest):

    def test_get(self):
        response = self.client.get(reverse("chores:add_category"))
        self.assertContains(response, "Name")
        self.assertIsNotNone(response.context["form"])
        self.assertIsInstance(response.context["form"], forms.CategoryForm)

    def test_post_valid(self):
        category_name = create_random_string()
        response = self.client.post(reverse("chores:add_category"), dict(
            name=category_name,
        ))
        self.assertRedirects(response, reverse("chores:list_categories"))

        chore: models.Category = models.Category.objects.get(
            name=category_name)
        self.assertEqual(chore.name, category_name)

    def test_post_invalid(self):
        response = self.client.post(reverse("chores:add_category"), dict())

        self.assertContains(response, "This field is required.", 1)
        self.assertQuerysetEqual(models.Category.objects.all(), [])


class CategoryEditViewTests(AuthenticatedTest):

    def test_get(self):
        category = self.create_category_in_db()
        response = self.client.get(
            reverse("chores:edit_category", args=(category.id,)))
        self.assertContains(response, category.name)

        form = response.context["form"]
        self.assertIsNotNone(form)
        self.assertIsInstance(form, forms.CategoryForm)
        self.assertEqual(form.instance, category)

    def test_get_does_not_exist(self):
        response = self.client.get(reverse("chores:edit_category", args=(0,)))
        self.assertEqual(response.status_code, 404)

    def test_post_valid(self):
        category = self.create_category_in_db()
        new_category_name = create_random_string()
        response = self.client.post(reverse("chores:edit_category", args=(category.id,)), dict(
            name=new_category_name,
        ))
        self.assertRedirects(response, reverse("chores:list_categories"))

        category: models.Category = models.Category.objects.get(pk=category.id)
        self.assertEqual(category.name, new_category_name)

        # test user 2 cannot update
        self.client.force_login(self.user2)
        response = self.client.post(reverse("chores:edit_category", args=(category.id,)), dict(
            name="failed edit",
        ))
        self.assertEqual(response.status_code, 404)
        category = models.Category.objects.get(pk=category.id)
        self.assertEqual(category.name, new_category_name)

    def test_post_invalid(self):
        category = self.create_category_in_db()
        response = self.client.post(
            reverse("chores:edit_category", args=(category.id,)), dict())

        self.assertContains(response, "This field is required.", 1)


class CategoryDeleteViewTests(AuthenticatedTest):

    def test_get(self):
        category = self.create_category_in_db()
        response = self.client.get(
            reverse("chores:delete_category", args=(category.id,)))
        self.assertContains(
            response, "Are you sure you want to delete \"{}\"".format(category.name))

    def test_get_does_not_exist(self):
        response = self.client.get(
            reverse("chores:delete_category", args=(0,)))
        self.assertEqual(response.status_code, 404)

    def test_post(self):
        category = self.create_category_in_db()
        response = self.client.post(
            reverse("chores:delete_category", args=(category.id,)))
        self.assertRedirects(response, reverse("chores:list_categories"))

        categories = models.Category.objects.filter(pk=category.id)
        self.assertQuerysetEqual(categories, [])

    def test_other_user_delete(self):
        category = self.create_category_in_db()
        self.client.force_login(self.user2)
        response = self.client.post(
            reverse("chores:delete_category", args=(category.id,)))
        self.assertEqual(response.status_code, 404)
