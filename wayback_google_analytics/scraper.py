import aiohttp
import asyncio
from wayback_google_analytics.codes import (
    get_UA_code,
    get_GA_code,
    get_GTM_code,
)
from wayback_google_analytics.async_utils import (
    get_snapshot_timestamps,
    get_codes_from_snapshots,
)

from wayback_google_analytics.utils import (
    DEFAULT_HEADERS,
)


async def get_html(session, url):
    """Returns html from a single url.

    Args:
        session (aiohttp.ClientSession)
        url (str): Url to scrape html from.

    Returns:
        html (str): html from url.
    """

    try:
        async with session.get(url, headers=DEFAULT_HEADERS) as response:
            return await response.text()
    except aiohttp.ServerTimeoutError as e:
        print(f"Request to {url} timed out", e)
    except aiohttp.ClientError as e:
        print(f"Failed to reach {url}", e)
    except Exception as e:
        print(f"Error getting data from {url}", e)
        return None


async def process_url(session, url, start_date, end_date, frequency, limit):
    """Returns a dictionary of current and archived UA/GA codes for a single url.

    Args:
        session (aiohttp.ClientSession)
        url (str): Url to scrape.
        start_date (str): Start date for time range
        end_date (str): End date for time range
        frequency (int):
        limit (int):

    Returns:
        "someurl.com": {
            "current_UA_code": "UA-12345678-1",
            "current_GA_code": "G-1234567890",
            "current_GTM_code": "GTM-12345678",
            "archived_UA_codes": {
                "UA-12345678-1": {
                    "first_seen": "20190101000000",
                    "last_seen": "20190101000000",
                },
            },
            "archived_GA_codes": {
                "G-1234567890": {
                    "first_seen": "20190101000000",
                    "last_seen": "20190101000000",
                }
            },
            "archived_GTM_codes": {
                "GTM-12345678": {
                    "first_seen": "20190101000000",
                    "last_seen": "20190101000000",
                },
        },

    """

    # Initialize dict for entry
    curr_entry = {url: {}}

    # Get html + current codes
    html = await get_html(session, url)
    print("Retrieving current codes for: ", url)
    if html:
        curr_entry[url]["current_UA_code"] = get_UA_code(html)
        curr_entry[url]["current_GA_code"] = get_GA_code(html)
        curr_entry[url]["current_GTM_code"] = get_GTM_code(html)
        curr_entry[url]["current_GTM_code"] = get_GTM_code(html)
        print("Finished gathering current codes for: ", url)

    # Get snapshots for Wayback Machine
    print("Retrieving archived codes for: ", url)
    archived_snapshots = await get_snapshot_timestamps(
        session=session,
        url=url,
        start_date=start_date,
        end_date=end_date,
        frequency=frequency,
        limit=limit,
    )

    # Get historic codes from archived snapshots, appending them to curr_entry
    archived_codes = await get_codes_from_snapshots(
        session=session, url=url, timestamps=archived_snapshots
    )
    curr_entry[url]["archived_UA_codes"] = archived_codes["UA_codes"]
    curr_entry[url]["archived_GA_codes"] = archived_codes["GA_codes"]
    curr_entry[url]["archived_GTM_codes"] = archived_codes["GTM_codes"]

    print("Finished retrieving archived codes for: ", url)

    return curr_entry


async def get_analytics_codes(
    session,
    urls,
    start_date="20121001000000",
    end_date=None,
    frequency=None,
    limit=None,
):
    """Takes array of urls and returns array of dictionaries with all found analytics codes for a given time range.

    Args:
        session (aiohttp.ClientSession)
        urls (array): Array of urls to scrape.
        start_date (str, optional): Start date for time range. Defaults to Oct 1, 2012, when UA codes were adopted.
        end_date (str, optional): End date for time range. Defaults to None.
        frequency (str, optional): Can limit snapshots to remove duplicates (1 per hr, day, month, etc). Defaults to None.
        limit (int, optional): Limit number of snapshots returned. Defaults to None.

    Returns:
        {
            "someurl.com": {
                "current_UA_code": "UA-12345678-1",
                "current_GA_code": "G-1234567890",
                "current_GTM_code": "GTM-12345678",
                "archived_UA_codes": {
                    "UA-12345678-1": {
                        "first_seen": "20190101000000",
                        "last_seen": "20200101000000",
                    }
                    "UA-12345678-2": {
                        "first_seen": "20190101000000",
                        "last_seen": "20200101000000",
                    }
                },
                "archived_GA_codes": {
                    "G-1234567890": {
                        "first_seen": "20190101000000",
                        "last_seen": "20200101000000",
                    }
                },
                "archived_GTM_codes": {
                    "GTM-12345678": {
                        "first_seen": "20190101000000",
                        "last_seen": "20200101000000",
                    }
            },
            "someotherurl.com": {...},
        }
    """

    # Comprehension to create list of tasks for asyncio.gather()

    tasks = [
        process_url(
            session=session,
            url=url,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
            limit=limit,
        )
        for url in urls
    ]

    # Process urls concurrently and return results
    results = await asyncio.gather(*tasks)
    return results