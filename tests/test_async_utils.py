import asynctest
from asynctest.mock import patch, MagicMock
import aiohttp

from wayback_google_analytics.async_utils import (
    get_codes_from_single_timestamp,
    get_codes_from_snapshots,
    get_snapshot_timestamps,
    DEFAULT_HEADERS,
)


class AsyncUtilsTestCase(asynctest.TestCase):
    """Tests for async_utils.py"""

    @patch("aiohttp.ClientSession.get")
    async def test_get_snapshot_timestamps(self, mock_get):
        """Does get_snapshot_timestamps return correct, formatted timestamps?"""

        # Mock the response from the server
        mock_response = MagicMock()

        async def mock_text_method():
            return "20120101000000\n20130102000000\n20140103000000\n20150104000000\n20160105000000\n20170106000000\n20180107000000\n20190108000000\n20200109000000\n20210110000000"

        mock_response.text = mock_text_method

        # Mock session.get to return response mocked above
        mock_get.return_value.__aenter__.return_value = mock_response

        async with aiohttp.ClientSession() as session:
            result = await get_snapshot_timestamps(
                session=session,
                url="https://www.someurl.com",
                start_date="20120101000000",
                end_date="20210102000000",
                frequency=4,
                limit=10,
            )

        expected_timestamp_list = [
            "20120101000000",
            "20130102000000",
            "20140103000000",
            "20150104000000",
            "20160105000000",
            "20170106000000",
            "20180107000000",
            "20190108000000",
            "20200109000000",
            "20210110000000",
        ]

        """Does get_snapshot_timestamps return correct, formatted timestamps?"""
        self.assertEqual(result, expected_timestamp_list)

        """Does get_snapshot_timestamps call session.get with correct parameters?"""
        expected_CDX_url = "http://web.archive.org/cdx/search/cdx?url=https://www.someurl.com&matchType=domain&filter=statuscode:200&fl=timestamp&output=JSON&collapse=timestamp:4&limit=10&from=20120101000000&to=20210102000000"
        mock_get.assert_called_with(expected_CDX_url, headers=DEFAULT_HEADERS)

    @patch("aiohttp.ClientSession.get")
    @patch("wayback_google_analytics.async_utils.get_UA_code")
    @patch("wayback_google_analytics.async_utils.get_GA_code")
    @patch("wayback_google_analytics.async_utils.get_GTM_code")
    async def test_get_codes_from_single_timestamp(
        self, mock_GTM, mock_GA, mock_UA, mock_get
    ):
        """Does get_codes_from_single_timestamp return correct codes from a single archive.org snapshot?"""

        # Mock the response from the server
        mock_response = MagicMock()

        async def mock_text_method():
            return "<html> ... fake data ... </html>"

        mock_response.text = mock_text_method
        mock_get.return_value.__aenter__.return_value = mock_response

        # Mock get_code functions
        mock_UA.return_value = ["UA-12345678-1"]
        mock_GA.return_value = ["G-12345678"]
        mock_GTM.return_value = ["GTM-12345678"]

        results = {
            "UA_codes": {},
            "GA_codes": {},
            "GTM_codes": {},
        }

        async with aiohttp.ClientSession() as session:
            await get_codes_from_single_timestamp(
                session=session,
                timestamp="20120101000000",
                base_url="https://web.archive.org/web/{timestamp}/https://www.someurl.com",
                results=results,
            )

        """Does it update results accordingly?"""
        self.assertIn("UA-12345678-1", results["UA_codes"])
        self.assertIn("G-12345678", results["GA_codes"])
        self.assertIn("GTM-12345678", results["GTM_codes"])

        """Does it call get with correct parameters?"""
        expected_url = (
            "https://web.archive.org/web/20120101000000/https://www.someurl.com"
        )
        mock_get.assert_called_with(expected_url, headers=DEFAULT_HEADERS)

    async def test_get_codes_from_snapshots(self):
        """Does get_codes_from_snapshots run once for each timestamp provided?"""

        # Mock get_codes_from_single_timestamp
        mock_get_codes_from_single_timestamp = asynctest.CoroutineMock()

        """Does it call get_codes_from_single_timestamp for each timestamp?"""
        with asynctest.mock.patch(
            "wayback_google_analytics.async_utils.get_codes_from_single_timestamp",
            mock_get_codes_from_single_timestamp,
        ):
            session = asynctest.Mock()
            url = "https://www.someurl.com"
            timestamps = [
                "20120101000000",
                "20130102000000",
                "20140103000000",
                "20150104000000",
                "20160105000000",
                "20170106000000",
                "20180107000000",
                "20190108000000",
                "20200109000000",
                "20210110000000",
            ]
            result = await get_codes_from_snapshots(session, url, timestamps)

            self.assertEqual(
                mock_get_codes_from_single_timestamp.call_count, len(timestamps)
            )

        # Resets call_count NOTE: There may be a better way to do this.
        mock_get_codes_from_single_timestamp = asynctest.CoroutineMock()

        with asynctest.mock.patch(
            "wayback_google_analytics.async_utils.get_codes_from_single_timestamp",
            mock_get_codes_from_single_timestamp,
        ):
            session = asynctest.Mock()
            url = "https://www.someurl.com"
            timestamps = ["20120101000000", "20130102000000", "20140103000000"]
            result = await get_codes_from_snapshots(session, url, timestamps)

            self.assertEqual(
                mock_get_codes_from_single_timestamp.call_count, len(timestamps)
            )

        # Resets call_count
        mock_get_codes_from_single_timestamp = asynctest.CoroutineMock()

        with asynctest.mock.patch(
            "wayback_google_analytics.async_utils.get_codes_from_single_timestamp",
            mock_get_codes_from_single_timestamp,
        ):
            session = asynctest.Mock()
            url = "https://www.someurl.com"
            timestamps = []
            result = await get_codes_from_snapshots(session, url, timestamps)

            self.assertEqual(
                mock_get_codes_from_single_timestamp.call_count, len(timestamps)
            )
