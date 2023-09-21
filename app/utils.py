import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re

# Semaphore to limit number of concurrent requests (10-15 appears to work fine. 20+ causes 443 error from web.archive.org)
sem = asyncio.Semaphore(15)

# Default headers for requests
DEFAULT_HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

# Collapse options for CDX api
COLLAPSE_OPTIONS = {
    "hour": "10",
    "day": "8",
    "month": "6",
    "year": "4",
}


def get_UA_code(html):
    """Returns UA codes (w/o duplicates) from given html, or None if not found.

    Args:
        html (str): Raw html.

    Returns:
        ["UA-12345678-1", "UA-12345678-2", ...]
    """

    # Regex pattern to find UA codes
    pattern = re.compile("UA-\d[^\"|']*")

    # Find all UA codes in html or return None
    try:
        UA_codes = pattern.findall(html)
    except Exception as e:
        print(e)
        return None

    # Remove duplicates and return
    return list(set(UA_codes))


def get_GA_code(html):
    """Returns GA codes (w/o duplicates) from given html, or None if not found.

    Args:
        html (str): Raw html.

    Returns:
        ["G-1234567890", "G-1234567891", ...]
    """

    # Regex pattern to find GA codes
    pattern = re.compile(r"G-[A-Za-z0-9]{10}")

    # Find all GA codes in html or return None
    try:
        GA_codes = pattern.findall(html)
    except Exception as e:
        print(e)
        return None

    # Remove duplicates and return
    return list(set(GA_codes))


def get_page_title(html):
    """Returns page title from given html, or None if not found."""

    # Get soup object from html
    soup = BeautifulSoup(html, "html.parser")

    # Find title or return None
    try:
        title = soup.title.string
    except Exception as e:
        print(e)
        return None

    return title


async def get_snapshot_timestamps(
    session,
    url,
    start_date,
    end_date,
    frequency,
    limit,
):
    """Takes a url and returns an array of snapshot timestamps for a given time range.

    Args:
        session (aiohttp.ClientSession)
        url (str)
        start_date (str, optional): Start date for time range. Defaults to Oct 1, 2012, when UA codes were adopted.
        end_date (str, optional): End date for time range.
        frequency (str, optional): Can limit snapshots to remove duplicates (1 per hr, day, week, etc).
        limit (int, optional): Limit number of snapshots returned.

    Returns:
        Array of timestamps:
            ["20190101000000", "20190102000000", ...]

    NOTE: The CDX params are a bit finnicky. It may be best to return a larger number of timestamps and then filter out the
    ones we don't need. That would lead to longer load times, however. Main issues include:

    - 'frequency' often breaks with other params. It is most reliable when paired with an exact limit (if getting years
    since 2012, add a limit of 11 results)
    - 'limit' breaks with frequency and start date if inverted to get most recent snapshots first.
    """

    # Default params get snapshots from url domain w/ 200 status codes only.
    cdx_url = f"http://web.archive.org/cdx/search/cdx?url={url}&matchType=domain&filter=statuscode:200&output=JSON"

    # Add correct params to cdx_url
    if frequency:
        cdx_url += f"&collapse=timestamp:{frequency}"

    if limit:
        cdx_url += f"&limit={limit}"

    if start_date:
        cdx_url += f"&from={start_date}"

    if start_date and end_date:
        cdx_url += f"&to={end_date}"

    print("CDX url= ", cdx_url)

    # Regex pattern to find 14-digit timestamps
    pattern = re.compile(r"\d{14}")

    # Use session to get timestamps
    async with session.get(cdx_url, headers=DEFAULT_HEADERS) as response:
        timestamps = pattern.findall(await response.text())

    print("TIMESTAMPS", timestamps)

    # Return sorted timestamps
    return sorted(timestamps)


async def get_codes_from_snapshots(session, url, timestamps):
    """Returns an array of UA/GA codes for a given url using the Archive.org Wayback Machine.

    Args:
        session (aiohttp.ClientSession)
        url (str)
        timestamps (list): List of timestamps to get codes from.

    Returns:
        {
            "UA_codes": {
                "UA-12345678-1": {
                    "first_seen": "20190101000000",
                    "last_seen": "20190101000000"
                },
            "GA_codes": {
                "G-1234567890": {
                    "first_seen": "20190101000000",
                    "last_seen": "20190101000000"
                    },
                },
        }
    """

    # Build base url template for wayback machine
    base_url = "https://web.archive.org/web/{timestamp}/" + url

    # Initialize results
    results = {
        "UA_codes": {},
        "GA_codes": {},
    }

    # Get codes from each timestamp with asyncio.gather().
    tasks = [
        get_codes_from_single_timestamp(session, base_url, timestamp, results)
        for timestamp in timestamps
    ]
    await asyncio.gather(*tasks)
    return results


async def get_codes_from_single_timestamp(session, base_url, timestamp, results):
    """Returns UA/GA codes from a single archive.org snapshot and adds it to the results dictionary.

    Args:
        session (aiohttp.ClientSession)
        base_url (str): Base url for archive.org snapshot.
        timestamp (str): 14-digit timestamp.
        results (dict): Dictionary to add codes to (inherited from get_codes_from_snapshots()).
    """

    # Use semaphore to limit number of concurrent requests
    async with sem:
        async with session.get(
            base_url.format(timestamp=timestamp), headers=DEFAULT_HEADERS
        ) as response:
            try:
                html = await response.text()

                print("GETTING CODES FOR", base_url.format(timestamp=timestamp))

                if html:
                    # Get UA/GA codes from html
                    UA_codes = get_UA_code(html)
                    GA_codes = get_GA_code(html)

                    # above functions return lists, so iterate thru codes and update
                    # results dict
                    for code in UA_codes:
                        if code not in results["UA_codes"]:
                            results["UA_codes"][code] = {}
                            results["UA_codes"][code]["first_seen"] = timestamp
                            results["UA_codes"][code]["last_seen"] = timestamp

                        if code in results["UA_codes"]:
                            results["UA_codes"][code]["last_seen"] = timestamp

                    for code in GA_codes:
                        if code not in results["GA_codes"]:
                            results["GA_codes"][code] = {}
                            results["GA_codes"][code]["first_seen"] = timestamp
                            results["GA_codes"][code]["last_seen"] = timestamp

                        if code in results["GA_codes"]:
                            results["GA_codes"][code]["last_seen"] = timestamp

            except Exception as e:
                print("ERROR in ASYNC ARCHIVE CODES", e)
                return None

        print("FINISH CODES FOR", base_url.format(timestamp=timestamp))
