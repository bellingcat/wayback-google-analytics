from unittest import TestCase

from osint_ga.codes import get_UA_code, get_GA_code, get_GTM_code


class CodesTestCase(TestCase):
    """Tests for codes.py"""

    def setUp(self):
        """Create test html data"""

        self.test_html_1 = """
        <html>
            <head>
                <script async src="https://www.googletagmanager.com/gtag/js?id=UA-12345678-1"></script>
                <script>
                    window.dataLayer = window.dataLayer || [];
                    function gtag(){dataLayer.push(arguments);}
                    gtag("js", new Date());
                    gtag("config", "UA-12345678-1");
                    gtag("config", "G-12345678-1");
                    gtag("config", "GTM-23451");
                </script>
            </head>
            <body>
                <p>"UA-12345678-2"</p>
                <p>"G-12345678-2"</p>
                <p>"GTM-2333234"</p>
            </body>
        </html>
        """

        self.test_html_2 = """
        <html>
            <head>
                <script async src="https://www.googletagmanager.com/gtag/js?id=UA-12345678-1"></script>
                <script>
                    window.dataLayer = window.dataLayer || [];
                    function gtag(){dataLayer.push(arguments);}
                    gtag("js", new Date());
                    gtag("config", "UA-12345678-1");
                    gtag("config", "UA-12345678-2");
                    gtag("config", "UA-12345678");
                    gtag("config", "G-12345678-1");
                    gtag("config", "G-12345678-2");
                    gtag("config", "G-12345678");
                    gtag("config", "GTM-23451");
                    gtag("config", "GTM-2333234");
                    gtag("config", "GTM-2124");
                </script>
            </head>
            <body>
                <p>"UA-12345678-2"</p>
                <p>"G-12345678-2"</p>
                <p>"GTM-2333234"</p>
            </body>
        </html>
        """

        self.test_html_no_UA_code = """
        <html>
            <head>
                <script async src="https://www.googletagmanager.com/gtag/js?id=NOCODEHERE"></script>
                <script>
                    window.dataLayer = window.dataLayer || [];
                    function gtag(){dataLayer.push(arguments);}
                    gtag("js", new Date());
                    gtag("config", "NOCODEHERE");
                </script>
            </head>
            <body>
                <p>"UA-12345678-2"</p>
                <p>"G-12345678-2"</p>
                <p>"GTM-2333234"</p>
            </body>
        </html>
        """

    def test_get_single_UA_code(self):
        """Test get_UA_code w/ single code"""

        """Does it return correct UA code?"""
        self.assertEqual(get_UA_code(self.test_html_1)[0], "UA-12345678-1")

    def test_get_multiple_UA_codes(self):
        """Test get_UA_code w/ multiple UA codes"""

        """Does it handle multiple UA codes in a single input?"""
        UA_codes = get_UA_code(self.test_html_2)
        self.assertEqual(len(UA_codes), 3)
        self.assertIn("UA-12345678-1", UA_codes)
        self.assertIn("UA-12345678-2", UA_codes)
        self.assertIn("UA-12345678", UA_codes)

    def test_get_UA_codes_invalid(self):
        """Test get_UA_code w/ invalid UA code"""

        """Does it return empty list if no UA code is found?"""
        self.assertIsInstance(get_UA_code(self.test_html_no_UA_code), list)
        self.assertEqual(len(get_UA_code(self.test_html_no_UA_code)), 0)

    def test_get_single_GA_code(self):
        """Test get_GA_code w/ single GA code"""

        """Does it return correct GA code?"""
        self.assertEqual(get_GA_code(self.test_html_1)[0], "G-12345678-1")

    def test_get_multiple_GA_codes(self):
        """Test get_GA_code w/ multiple GA codes"""

        """Does it handle multiple GA codes in a single input?"""
        GA_codes = get_GA_code(self.test_html_2)
        self.assertEqual(len(GA_codes), 3)
        self.assertIn("G-12345678-1", GA_codes)
        self.assertIn("G-12345678-2", GA_codes)
        self.assertIn("G-12345678", GA_codes)

    def test_get_GA_codes_invalid(self):
        """Test get_GA_code w/ invalid GA code"""

        """Does it return empty list if no GA code is found?"""
        self.assertIsInstance(get_GA_code(self.test_html_no_UA_code), list)
        self.assertEqual(len(get_GA_code(self.test_html_no_UA_code)), 0)

    def test_get_single_GTM_code(self):
        """Test get_GTM_code w/ single GTM code"""

        """Does it return correct GTM code?"""
        self.assertEqual(get_GTM_code(self.test_html_1)[0], "GTM-23451")

    def test_get_multiple_GTM_codes(self):
        """Test get_GTM_code w/ multiple GTM codes"""

        """Does it handle multiple GTM codes in a single input?"""
        GTM_codes = get_GTM_code(self.test_html_2)
        self.assertEqual(len(GTM_codes), 3)
        self.assertIn("GTM-23451", GTM_codes)
        self.assertIn("GTM-2333234", GTM_codes)
        self.assertIn("GTM-2124", GTM_codes)

    def test_get_GTM_codes_invalid(self):
        """Test get_GTM_code w/ invalid GTM code"""

        """Does it return empty list if no GTM code is found?"""
        self.assertIsInstance(get_GTM_code(self.test_html_no_UA_code), list)
        self.assertEqual(len(get_GTM_code(self.test_html_no_UA_code)), 0)


