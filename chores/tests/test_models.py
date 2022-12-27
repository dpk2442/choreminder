from datetime import timedelta as td

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from chores.models import AwayDate


class TestAwayDateValidation(TestCase):

    def test_start_less_than_end(self):
        start_date = timezone.now()
        end_date = start_date + td(days=1)

        away_date = AwayDate(
            name="name", start_date=start_date, end_date=end_date)

        away_date.clean()

    def test_start_equals_end(self):
        start_date = timezone.now()

        away_date = AwayDate(
            name="name", start_date=start_date, end_date=start_date)

        away_date.clean()

    def test_start_greater_than_end(self):
        start_date = timezone.now()
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
