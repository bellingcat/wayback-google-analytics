import os
from unittest import TestCase
from unittest.mock import patch, Mock
from datetime import datetime
from shutil import rmtree
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
        self.test_timestamp = "01-01-2023(12:00:00)"
        self.test_path = "./output/"
        self.valid_types = ["csv", "txt", "json", "xlsx"]

    def tearDown(self):
        """Removes any created directories after each test"""
        if os.path.exists(self.test_path):
            rmtree(self.test_path)

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

    @patch("osint_ga.output.datetime", autospec=True)
    def test_init_output_valid_types(self, mock_datetime):
        """Does init_output create a dict with correct keys?"""
        mock_now = Mock(
            return_value=datetime.strptime(self.test_timestamp, "%d-%m-%Y(%H:%M:%S)")
        )
        mock_datetime.now = mock_now

        for type in self.valid_types:
            with self.subTest(type=type):
                expected_file_path = os.path.join(
                    self.test_path, f"{self.test_timestamp}.{type}"
                )

                returned_file_path = init_output(type)

                """Does it return correct file path for each type?"""
                print(
                    "returned = ", returned_file_path, "expected = ", expected_file_path
                )
                self.assertEqual(returned_file_path, expected_file_path)

                """Does it create correct file for each type?"""
                if type == "csv":
                    self.assertTrue(
                        os.path.exists(os.path.join(self.test_path, f"{self.test_timestamp}_codes.csv"))
                    )
                    self.assertTrue(
                        os.path.exists(os.path.join(self.test_path, f"{self.test_timestamp}_urls.csv"))
                    )
                else:
                    self.assertTrue(os.path.exists(returned_file_path))

    def test_init_output_invalid_type(self):
        """Does init_output raise error with incorrect type?"""

        """Should raise error with 'docx'"""
        with self.assertRaises(ValueError):
            init_output("docx")

        """Should raise error with 'md'"""
        with self.assertRaises(ValueError):
            init_output("md")
