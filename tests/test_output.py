from datetime import datetime
import json
import os
import pandas as pd
from unittest import TestCase
from unittest.mock import patch, Mock
from shutil import rmtree

from wayback_google_analytics.output import (
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
        self.test_path = "./test_output"
        self.valid_types = ["csv", "txt", "json", "xlsx"]
        if not os.path.exists(self.test_path):
            os.makedirs(self.test_path)

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

    @patch("wayback_google_analytics.output.datetime", autospec=True)
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

                returned_file_path = init_output(type=type, output_dir=self.test_path)

                """Does it return correct file path for each type?"""
                self.assertEqual(returned_file_path, expected_file_path)

                """Does it create correct file for each type?"""
                if type == "csv":
                    self.assertTrue(
                        os.path.exists(
                            os.path.join(
                                self.test_path, f"{self.test_timestamp}_codes.csv"
                            )
                        )
                    )
                    self.assertTrue(
                        os.path.exists(
                            os.path.join(
                                self.test_path, f"{self.test_timestamp}_urls.csv"
                            )
                        )
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

    def test_write_output_txt(self):
        """Does write_output write results to correct text file?"""

        test_file = "./test_output/test_file.txt"
        test_results = {"test": "test"}
        with open(test_file, "w") as f:
            pass

        write_output(test_file, "txt", test_results)

        with open(test_file, "r") as f:
            test_data = json.load(f)

        os.remove(test_file)
        self.assertEqual(test_data, test_results)

    def test_write_output_json(self):
        """Does write_output write results to correct json file?"""

        test_file = "./test_output/test_file.json"
        test_results = {"test": "test"}
        with open(test_file, "w") as f:
            pass

        write_output(test_file, "json", test_results)

        with open(test_file, "r") as f:
            test_data = json.load(f)

        os.remove(test_file)
        self.assertEqual(test_data, test_results)

    @patch("wayback_google_analytics.output.get_urls_df", autospec=True)
    @patch("wayback_google_analytics.output.get_codes_df", autospec=True)
    def test_write_output_csv(self, mock_urls, mock_codes):
        """Does write_output write results to correct csv files?"""

        test_file = "./test_output/test_file.csv"
        test_file_urls = "./test_output/test_file_urls.csv"
        test_file_codes = "./test_output/test_file_codes.csv"
        test_results = {"test": "test"}
        mock_urls.return_value = pd.DataFrame([test_results])
        mock_codes.return_value = pd.DataFrame([test_results])

        with open(test_file_urls, "w") as f:
            pass

        with open(test_file_codes, "w") as f:
            pass

        write_output(test_file, "csv", test_results)

        test_data_urls = pd.read_csv(test_file_urls).to_dict(orient="records")[0]
        test_data_codes = pd.read_csv(test_file_codes).to_dict(orient="records")[0]

        os.remove(test_file_urls)
        os.remove(test_file_codes)

        self.assertEqual(test_data_urls, test_results)
        self.assertEqual(test_data_codes, test_results)

    @patch("wayback_google_analytics.output.get_urls_df", autospec=True)
    @patch("wayback_google_analytics.output.get_codes_df", autospec=True)
    def test_write_output_xlsx(self, mock_urls, mock_codes):
        """Does write_output write results to correct xlsx file?"""

        test_file = "./test_output/test_file.xlsx"
        test_results = {"test": "test"}
        mock_urls.return_value = pd.DataFrame([test_results])
        mock_codes.return_value = pd.DataFrame([test_results])

        with open(test_file, "w") as f:
            pass

        write_output(test_file, "xlsx", test_results)

        with pd.ExcelFile(test_file, engine="openpyxl") as xls:
            sheet_names = xls.sheet_names

            df_urls = xls.parse("URLs")
            df_codes = xls.parse("Codes")

        os.remove(test_file)

        self.assertEqual(sheet_names, ["URLs", "Codes"])
        self.assertEqual(df_urls.to_dict(orient="records")[0], test_results)
        self.assertEqual(df_codes.to_dict(orient="records")[0], test_results)

    def test_get_urls_df(self):
        """Does get_urls_df create appropriate df from dict?"""

        test_results = {
            "someurl.com": {
                "current_UA_code": "UA-12345678-1",
                "current_GA_code": "G-1234567890",
                "current_GTM_code": "GTM-12345678",
                "archived_UA_codes": {
                    "UA-12345678-1": {
                        "first_seen": "01/01/2019",
                        "last_seen": "01/01/2019",
                    },
                },
                "archived_GA_codes": {
                    "G-1234567890": {
                        "first_seen": "01/01/2019",
                        "last_seen": "01/01/2019",
                    }
                },
                "archived_GTM_codes": {
                    "GTM-12345678": {
                        "first_seen": "01/01/2019",
                        "last_seen": "01/01/2019",
                    },
                },
            }
        }

        expected_results = {
            "url": "someurl.com",
            "UA_Code": "UA-12345678-1",
            "GA_Code": "G-1234567890",
            "GTM_Code": "GTM-12345678",
            "Archived_UA_Codes": "1. UA-12345678-1 (01/01/2019 - 01/01/2019)",
            "Archived_GA_Codes": "1. G-1234567890 (01/01/2019 - 01/01/2019)",
            "Archived_GTM_Codes": "1. GTM-12345678 (01/01/2019 - 01/01/2019)",
        }

        actual_results = get_urls_df([test_results])

        self.assertEqual(actual_results.to_dict(orient="records")[0], expected_results)
        self.assertTrue(type(actual_results) is pd.DataFrame)

    def test_get_codes_df(self):
        """Does get_codes_df create appropriate df from dict?"""

        test_results = {
            "someurl.com": {
                "current_UA_code": "UA-12345678-1",
                "current_GA_code": "G-1234567890",
                "current_GTM_code": "GTM-12345678",
                "archived_UA_codes": {
                    "UA-12345678-1": {
                        "first_seen": "01/01/2019",
                        "last_seen": "01/01/2019",
                    },
                },
                "archived_GA_codes": {
                    "G-1234567890": {
                        "first_seen": "01/01/2019",
                        "last_seen": "01/01/2019",
                    }
                },
                "archived_GTM_codes": {
                    "GTM-12345678": {
                        "first_seen": "01/01/2019",
                        "last_seen": "01/01/2019",
                    },
                },
            }
        }

        expected_results = [
            {
                "code": "G-1234567890",
                "websites": "someurl.com",
                "active": "1. 01/01/2019 - 01/01/2019(at someurl.com)",
            },
            {
                "code": "GTM-12345678",
                "websites": "someurl.com",
                "active": "1. 01/01/2019 - 01/01/2019(at someurl.com)",
            },
            {
                "code": "UA-12345678-1",
                "websites": "someurl.com",
                "active": "1. 01/01/2019 - 01/01/2019(at someurl.com)",
            },
        ]

        actual_results = get_codes_df([test_results])

        self.assertEqual(actual_results.to_dict(orient="records"), expected_results)
        self.assertTrue(type(actual_results) is pd.DataFrame)
