from wayback_google_analytics.main import main, setup_args
import unittest
import sys
from io import StringIO


class TestMain(unittest.TestCase):
    """Tests for main.py"""

    def setUp(self):
        # Capture any errors to stderr
        self.held_stderr = StringIO()
        self.held_stdout = StringIO()
        sys.stdout = self.held_stdout
        sys.stderr = self.held_stderr

    def tearDown(self):
        # Reset sys.stderr
        self.held_stdout.close()
        self.held_stderr.close()
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def test_setup_args_help_message(self):
        """Does main.py -h print usage message?"""

        sys.argv = ["main.py", "-h"]
        with self.assertRaises(SystemExit):
            setup_args()

        """Should print help message to terminal"""
        output = self.held_stdout.getvalue().strip()
        self.assertIn("usage: main.py [-h]", output)

    def test_setup_args_no_arguments(self):
        """Does setup_args return error message if no arguments provided?"""
        sys.argv = ["main.py"]
        with self.assertRaises(SystemExit):
            setup_args()

        """Should print help and error message to terminal"""
        output = self.held_stderr.getvalue().strip()
        self.assertIn("usage: main.py [-h]", output)
        self.assertIn("main.py: error:", output)

    def test_setup_args_invalid_multiple_inputs(self):
        """Does setup_args return error message if multiple inputs provided?"""

        sys.argv = [
            "main.py",
            "-i",
            "tests/test_urls.txt",
            "-u",
            "https://www.google.com",
        ]
        with self.assertRaises(SystemExit):
            setup_args()

        """Should print help and error message to terminal"""
        output = self.held_stderr.getvalue().strip()
        self.assertIn("usage: main.py [-h]", output)
        self.assertIn("main.py: error:", output)

    def test_setup_args_invalid_output(self):
        """Does setup_args return error message if invalid output provided?"""

        sys.argv = ["main.py", "-i", "tests/test_urls.txt", "-o", "invalid_output"]
        with self.assertRaises(SystemExit):
            setup_args()

        """Should print error message to terminal"""
        output = self.held_stderr.getvalue().strip()
        self.assertIn("main.py: error:", output)

    def test_setup_args_valid_args(self):
        """Does setup_args return args if valid args provided?"""

        sys.argv = [
            "main.py",
            "--input_file",
            "tests/test_urls.txt",
            "--output",
            "json",
            "--start_date",
            "01/01/2012:12:00",
            "--end_date",
            "01/01/2013:12:00",
            "--frequency",
            "daily",
            "--limit",
            "10",
            "--skip_current",
        ]
        args = setup_args()

        """Should return args"""
        self.assertIsNotNone(args)

        """Args should contain proper values"""
        self.assertEqual(args.input_file, "tests/test_urls.txt")
        self.assertEqual(args.output, "json")
        self.assertEqual(args.start_date, "01/01/2012:12:00")
        self.assertEqual(args.end_date, "01/01/2013:12:00")
        self.assertEqual(args.frequency, "daily")
        self.assertEqual(args.limit, "10")
        self.assertEqual(args.skip_current, True)

    def test_setup_args_valid_args_shorthand(self):
        """Does setup_args return args if valid args provided using shorthand commands?"""

        sys.argv = [
            "main.py",
            "-i",
            "tests/test_urls.txt",
            "-o",
            "json",
            "-s",
            "01/01/2012:12:00",
            "-e",
            "01/01/2013:12:00",
            "-f",
            "daily",
            "-l",
            "10",
            "-sc",
        ]
        args = setup_args()

        """Should return args"""
        self.assertIsNotNone(args)

        """Args should contain proper values"""
        self.assertEqual(args.input_file, "tests/test_urls.txt")
        self.assertEqual(args.output, "json")
        self.assertEqual(args.start_date, "01/01/2012:12:00")
        self.assertEqual(args.end_date, "01/01/2013:12:00")
        self.assertEqual(args.frequency, "daily")
        self.assertEqual(args.limit, "10")
        self.assertEqual(args.skip_current, True)
