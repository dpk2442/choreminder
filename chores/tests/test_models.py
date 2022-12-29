from datetime import timedelta as td

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from chores.models import AwayDate, Chore


class TestChoreValidation(TestCase):

    def test_due_duration(self):
        Chore(due_duration=td(days=1)).clean()

        with self.assertRaises(ValidationError) as cm:
            Chore(due_duration=td(microseconds=99999999999)).clean()

        self.assertIn(
            "'due_duration': ['The due duration must be specified in days']", str(cm.exception))

    def test_overdue_duration(self):
        Chore(overdue_duration=td(days=1)).clean()

        with self.assertRaises(ValidationError) as cm:
            Chore(overdue_duration=td(microseconds=99999999999)).clean()

        self.assertIn(
            "'overdue_duration': ['The overdue duration must be specified in days']", str(cm.exception))

    def test_both_durations_invalid(self):
        with self.assertRaises(ValidationError) as cm:
            Chore(due_duration=td(microseconds=99999999999),
                  overdue_duration=td(microseconds=99999999999)).clean()

        self.assertIn(
            "'due_duration': ['The due duration must be specified in days']", str(cm.exception))
        self.assertIn(
            "'overdue_duration': ['The overdue duration must be specified in days']", str(cm.exception))


class TestAwayDateValidation(TestCase):

    def test_start_less_than_end(self):
        start_date = timezone.now().date()
        end_date = start_date + td(days=1)

        away_date = AwayDate(
            name="name", start_date=start_date, end_date=end_date)

        away_date.clean()

    def test_start_equals_end(self):
        start_date = timezone.now().date()

        away_date = AwayDate(
            name="name", start_date=start_date, end_date=start_date)

        away_date.clean()

    def test_start_greater_than_end(self):
        start_date = timezone.now().date()
        end_date = start_date - td(days=1)

        away_date = AwayDate(
            name="name", start_date=start_date, end_date=end_date)

        with self.assertRaises(ValidationError) as ex:
            away_date.clean()

        self.assertIn(
            "'start_date': ['The start date must be on or before the end date']", str(ex.exception))
        self.assertIn(
            "'end_date': ['The end date must be on or after the start date']", str(ex.exception))

    def test_start_end_none(self):
        away_date = AwayDate(name="name", start_date=None, end_date=None)

        away_date.clean()


class TestAwayDateContainsDate(TestCase):

    def test_date_before(self):
        now = timezone.now()
        start_date = now.date()
        end_date = start_date + td(days=1)
        test_date = now - td(days=1)

        # test date range
        self.assertFalse(AwayDate(start_date=start_date,
                         end_date=end_date).contains_date(test_date))

        # test single date away
        self.assertFalse(AwayDate(start_date=start_date,
                         end_date=start_date).contains_date(test_date))

    def test_date_after(self):
        now = timezone.now()
        start_date = now.date()
        end_date = start_date + td(days=1)
        test_date = now + td(days=2)

        # test date range
        self.assertFalse(AwayDate(start_date=start_date,
                         end_date=end_date).contains_date(test_date))

        # test single date away
        self.assertFalse(AwayDate(start_date=start_date,
                         end_date=start_date).contains_date(test_date))

    def test_date_during(self):
        now = timezone.now()
        start_date = now.date()
        end_date = start_date + td(days=2)

        # test date range
        self.assertTrue(AwayDate(start_date=start_date,
                                 end_date=end_date).contains_date(now + td(days=1)))

        # test single date away
        self.assertTrue(AwayDate(start_date=start_date,
                                 end_date=start_date).contains_date(now))
