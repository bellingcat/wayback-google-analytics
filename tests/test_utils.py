from unittest import TestCase

from osint_ga.utils import get_limit_from_frequency

class UtilsTestCase(TestCase):
    """Tests for utils.py"""

    def test_get_limit_from_frequency(self):
        """Tests that get_limit_from_frequency returns correct limit."""

        """Returns a correct limit for 'yearly' frequency."""
        self.assertEqual(get_limit_from_frequency(frequency="yearly", start_date="20120101000000", end_date="20130101000000"), 2)
        self.assertEqual(get_limit_from_frequency(frequency="yearly", start_date="20120101000000", end_date="20140101000000"), 3)
        self.assertEqual(get_limit_from_frequency(frequency="yearly", start_date="19990101000000", end_date="20150101000000"), 17)

        """Returns a correct limit for 'monthly' frequency."""
        self.assertEqual(get_limit_from_frequency(frequency="monthly", start_date="20120101000000", end_date="20120201000000"), 2)
        self.assertEqual(get_limit_from_frequency(frequency="monthly", start_date="20120101000000", end_date="20121205000000"), 12)
        self.assertEqual(get_limit_from_frequency(frequency="monthly", start_date="20120101000000", end_date="20130101000000"), 13)
        self.assertEqual(get_limit_from_frequency(frequency="monthly", start_date="20120101000000", end_date="20140101000000"), 25)
        self.assertEqual(get_limit_from_frequency(frequency="monthly", start_date="19990801000000", end_date="20150617000000"), 191)

        """Returns a correct limit for 'daily' frequency."""
        self.assertEqual(get_limit_from_frequency(frequency="daily", start_date="20120101000000", end_date="20120102000000"), 2)
        self.assertEqual(get_limit_from_frequency(frequency="daily", start_date="20120101000000", end_date="20120131000000"), 31)
        self.assertEqual(get_limit_from_frequency(frequency="daily", start_date="19990213000000", end_date="20150617000000"), 5969)

        """Returns a correct limit for 'hourly' frequency."""
        self.assertEqual(get_limit_from_frequency(frequency="hourly", start_date="20120101000000", end_date="20120101010000"), 2)
        self.assertEqual(get_limit_from_frequency(frequency="hourly", start_date="20120101000000", end_date="20120101020000"), 3)
        self.assertEqual(get_limit_from_frequency(frequency="hourly", start_date="20120101000000", end_date="20120101230000"), 24)
        self.assertEqual(get_limit_from_frequency(frequency="hourly", start_date="19990213000000", end_date="20150617000000"), 143233)

    def test_get_limit_from_frequency_invalid(self):
        """Tests that get_limit_from_frequency raises ValueError if parameters incorrect."""

        """Raises ValueError without valid start date"""
        with self.assertRaises(ValueError):
            get_limit_from_frequency(frequency="yearly", start_date=None, end_date="20130101000000")

        """Raises ValueError without valid frequency"""
        with self.assertRaises(ValueError):
            get_limit_from_frequency(frequency=None, start_date="20120101000000", end_date="20130101000000")
            get_limit_from_frequency(frequency="weekly", start_date="20120101000000", end_date="20130101000000")