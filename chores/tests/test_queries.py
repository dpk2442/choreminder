from django.test import TestCase

from chores import model_views, queries
from .utils import create_category, create_chore, create_random_user


class TestQueryChores(TestCase):

    def test_invalid_user(self):
        with self.assertRaises(ValueError) as cm:
            queries.query_chores(None)

        self.assertEqual(str(cm.exception), "Invalid user provided")

    def test_valid_user(self):
        user1 = create_random_user()
        user2 = create_random_user()

        chore1 = create_chore(user1)
        chore2 = create_chore(user1)

        self.assertEqual(queries.query_chores(user1), [
                         model_views.Chore(chore1), model_views.Chore(chore2)])
        self.assertEqual(queries.query_chores(user2), [])


class TestQueryCategories(TestCase):

    def test_invalid_user(self):
        with self.assertRaises(ValueError) as cm:
            queries.query_categories(None)

        self.assertEqual(str(cm.exception), "Invalid user provided")

    def test_valid_user(self):
        user1 = create_random_user()
        user2 = create_random_user()

        category1 = create_category(user1)
        category2 = create_category(user1)

        self.assertEqual(queries.query_categories(user1), [
                         model_views.Category(category1), model_views.Category(category2)])
        self.assertEqual(queries.query_categories(user2), [])
