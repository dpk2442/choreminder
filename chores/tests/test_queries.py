from django.test import TestCase

from chores import model_views, queries
from .utils import create_tag, create_chore, create_random_user


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


class TestQueryTags(TestCase):

    def test_invalid_user(self):
        with self.assertRaises(ValueError) as cm:
            queries.query_tags(None)

        self.assertEqual(str(cm.exception), "Invalid user provided")

    def test_valid_user(self):
        user1 = create_random_user()
        user2 = create_random_user()

        tag1 = create_tag(user1)
        tag2 = create_tag(user1)

        self.assertEqual(queries.query_tags(user1), [
                         model_views.Tag(tag1), model_views.Tag(tag2)])
        self.assertEqual(queries.query_tags(user2), [])
