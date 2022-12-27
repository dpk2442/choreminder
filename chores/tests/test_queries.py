from django.test import TestCase

from chores import model_views, queries

from .utils import (create_away_date, create_chore, create_random_user,
                    create_tag)


class TestQueryChores(TestCase):

    def test_invalid_user(self):
        with self.assertRaises(ValueError) as cm:
            queries.query_chores(None, None)

        self.assertEqual(str(cm.exception), "Invalid user provided")

    def test_valid_user(self):
        user1 = create_random_user()
        user2 = create_random_user()

        chore1 = create_chore(user1)
        chore2 = create_chore(user1)

        self.assertEqual(queries.query_chores(user1, None), [
                         model_views.Chore(chore1), model_views.Chore(chore2)])
        self.assertEqual(queries.query_chores(user2, None), [])

    def test_chore_tag_filter(self):
        user = create_random_user()

        tag1 = create_tag(user)
        chore1 = create_chore(user, tag=tag1)
        chore2 = create_chore(user, tag=tag1)

        tag2 = create_tag(user)
        chore3 = create_chore(user, tag=tag2)

        self.assertEqual(queries.query_chores(user, tag1.id), [
                         model_views.Chore(chore1), model_views.Chore(chore2)])
        self.assertEqual(queries.query_chores(user, tag2.id),
                         [model_views.Chore(chore3)])


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


class TestQueryAwayDates(TestCase):

    def test_invalid_user(self):
        with self.assertRaises(ValueError) as cm:
            queries.query_away_dates(None)

        self.assertEqual(str(cm.exception), "Invalid user provided")

    def test_valid_user(self):
        user1 = create_random_user()
        user2 = create_random_user()

        away_date1 = create_away_date(user1)
        away_date2 = create_away_date(user1)

        self.assertEqual(queries.query_away_dates(user1), [
                         model_views.AwayDate(away_date1), model_views.AwayDate(away_date2)])
        self.assertEqual(queries.query_away_dates(user2), [])
