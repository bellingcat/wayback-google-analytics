from unittest import TestCase
from osint_ga.output import (
    init_output,
    write_output,
    get_codes_df,
    get_urls_df,
    format_archived_codes,
    format_active,
)


class OutputTestCase(TestCase):
    """Tests for output.py"""

    def setUp(self):
        """Create test data"""

    def test_format_active(self):
        """Does format_active convert list of "active" values from df into formatted string?"""

        test_active_list = [
            "Current (at https://www.example.com)",
            "2019-01-01 - 2020-01-01 (at https://www.example.com)",
            "2018-01-01 - 2019-01-01 (at https://www.example.com)",
        ]

        expected = (
            "1. Current (at https://www.example.com)\n\n"
            "2. 2019-01-01 - 2020-01-01 (at https://www.example.com)\n\n"
            "3. 2018-01-01 - 2019-01-01 (at https://www.example.com)"
        )

        self.assertEqual(format_active(test_active_list), expected)
        self.assertTrue(type(format_active(test_active_list)) is str)

    def test_format_archived_codes(self):
        """Does format_archived_codes convert dict of archived codes into formatted string?"""

        archived_codes = {
            "UA-21085468-1": {
                "first_seen": "04/01/2014:04:02",
                "last_seen": "03/01/2012:06:00",
            },
            "UA-113949143-1": {
                "first_seen": "01/01/2019:19:39",
                "last_seen": "01/01/2023:00:16",
            },
        }

        expected = (
            "1. UA-21085468-1 (04/01/2014:04:02 - 03/01/2012:06:00)\n\n"
            "2. UA-113949143-1 (01/01/2019:19:39 - 01/01/2023:00:16)"
        )

        self.assertEqual(format_archived_codes(archived_codes), expected)
        self.assertTrue(type(format_archived_codes(archived_codes)) is str)
