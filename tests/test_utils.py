from unittest import TestCase

from osint_ga.utils import get_limit_from_frequency, validate_dates, get_14_digit_timestamp, get_date_from_timestamp, COLLAPSE_OPTIONS

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
        with self.assertRaises(ValueError):
            get_limit_from_frequency(frequency="weekly", start_date="20120101000000", end_date="20130101000000")

    def test_validate_dates(self):
        """Does validate_dates return True for valid dates?"""

        """Returns True for valid dates"""
        self.assertTrue(validate_dates(start_date="01/01/2012:12:00", end_date="02/01/2012:12:00"))
        self.assertTrue(validate_dates(start_date="01/10/2023:12:00", end_date="03/11/2023:12:00"))

        """Handles dates without 24hr time"""
        self.assertTrue(validate_dates(start_date="01/01/2012", end_date="02/01/2012"))
        self.assertTrue(validate_dates(start_date="01/10/2023", end_date="03/11/2023"))
        self.assertTrue(validate_dates(start_date="01/01/2012:12:30", end_date="02/01/2012"))
        self.assertTrue(validate_dates(start_date="01/01/2012", end_date="02/01/2012:01:00"))

    def test_validate_dates_invalid(self):
        """Does validate dates return False for invalid dates?"""

        """Returns False for invalid dates"""
        self.assertFalse(validate_dates(start_date="01/01/2012:12:00", end_date="01/01/2012:12:00"))
        self.assertFalse(validate_dates(start_date="01/01/2012:12:00", end_date="01/01/2010:11:00"))
        self.assertFalse(validate_dates(start_date="01/02/2012", end_date="01/01/2012:11:00"))
        self.assertFalse(validate_dates(start_date="01/01/2012:12:30", end_date="02/01/2010"))

        """Raises TypeError without valid start date"""
        with self.assertRaises(TypeError):
            validate_dates(start_date=None, end_date="01/01/2012:12:00")
        with self.assertRaises(TypeError):
            validate_dates(start_date="01/01/2012:12:00", end_date=None)
        with self.assertRaises(TypeError):
            validate_dates(start_date=None, end_date=None)


    def test_get_14_digit_timestamp(self):
        """Does get_14_digit_timestamp return correct timestamp?"""

        """Returns correct timestamp"""
        self.assertEqual(get_14_digit_timestamp("01/01/2012:12:00"), "20120101120000")
        self.assertEqual(get_14_digit_timestamp("01/01/2012:12:00"), "20120101120000")
        self.assertEqual(get_14_digit_timestamp("01/01/2012:23:01"), "20120101230100")


    def test_get_date_from_timestamp(self):
        """Does get_date_from_timestamp return correct date?"""

        """Returns correct date"""
        self.assertEqual(get_date_from_timestamp("20120101120000"), "01/01/2012:12:00")
        self.assertEqual(get_date_from_timestamp("20140101231200"), "01/01/2014:23:12")
        self.assertEqual(get_date_from_timestamp("20230112010200"), "12/01/2023:01:02")

    def test_COLLAPSE_OPTIONS(self):
        """Does COLLAPSE_OPTIONS return correct frequency?"""

        """Returns correct frequency"""
        self.assertEqual(COLLAPSE_OPTIONS["yearly"], "4")
        self.assertEqual(COLLAPSE_OPTIONS["monthly"], "6")
        self.assertEqual(COLLAPSE_OPTIONS["daily"], "8")
        self.assertEqual(COLLAPSE_OPTIONS["hourly"], "10")

