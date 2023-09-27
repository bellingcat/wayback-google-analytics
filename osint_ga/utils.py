import asyncio
import re

from datetime import datetime
from dateutil.relativedelta import relativedelta

from osint_ga.codes import get_UA_code, get_GA_code, get_GTM_code

# Semaphore to limit number of concurrent requests (10-15 appears to work fine. 20+ causes 443 error from web.archive.org)
sem = asyncio.Semaphore(10)

# Default headers for requests
DEFAULT_HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

# Collapse options for CDX api
COLLAPSE_OPTIONS = {
    "hourly": "10",
    "daily": "8",
    "monthly": "6",
    "yearly": "4",
}


def get_limit_from_frequency(frequency, start_date, end_date):
    """Returns an appropriate limit for a given frequency.

    Args:
        frequency (str): Frequency (hourly, daily, monthly, yearly)
        start_date (str): 14-digit timestamp for starting point
        end_date (str): 14-digit timestamp for end of range

    Returns:
        int: Limit
    """

    # Get start date as datetime object or raise error if not provided
    if not start_date:
        raise ValueError("To set a frequency you must provide a start date.")

    # Get end date as current date if not present
    if not end_date:
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(end_date, "%Y%m%d%H%M%S")

    # Get start and end dates as datetime objects
    start_date = datetime.strptime(start_date, "%Y%m%d%H%M%S")

    # Get delta between start and end dates
    delta = relativedelta(end_date, start_date)

    # Remove whitespace and convert frequency to lower case
    if frequency:
        frequency.strip().lower()

    if frequency == "yearly":
        return delta.years + 1

    if frequency == "monthly":
        return delta.years * 12 + delta.months + 1

    if frequency == "daily":
        total_days = (end_date - start_date).days
        return total_days + 1

    if frequency == "hourly":
        total_hours = (end_date - start_date).total_seconds() / 3600
        return int(total_hours + 1)

    # Raise error if frequency none of the above options
    raise ValueError(
        f"Invalid frequency: {frequency}. Please use hourly, daily, monthly, or yearly."
    )


def get_date_from_timestamp(timestamp):
    """Takes a 14-digit timestamp (YYYYmmddHHMMSS) and returns a date (dd/mm/YYYY:HH:MM).

    Args:
        timestamp (str): 14-digit timestamp (YYYYmmddHHMMSS)

    Returns:
        str: Date in format dd/mm/YYYY:HH:MM

    Example: 20121001000000 -> 01/10/2012:00:00
    """

    # convert timestamp to datetime object
    date = datetime.strptime(timestamp, "%Y%m%d%H%M%S")

    # convert datetime object to date
    return date.strftime("%d/%m/%Y:%H:%M")


def get_14_digit_timestamp(date):
    """Takes a date (dd/mm/YYYY:HH:MM) and converts it to a 14-digit timestamp (YYYYmmddHHMMSS).

    Args:
        date (str): Date in format dd/mm/YYYY:HH:MM

    Returns:
        str: 14-digit timestamp (YYYYmmddHHMMSS)

    Example: 01/10/2012:00:00 -> 20121001000000
    """

    # Convert date to datetime object
    try:
        date = datetime.strptime(date, "%d/%m/%Y:%H:%M")
    except ValueError:
        date = datetime.strptime(date, "%d/%m/%Y")

    # Convert datetime object to 14-digit timestamp
    return date.strftime("%Y%m%d%H%M%S")


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
    """

    # Default params get snapshots from url domain w/ 200 status codes only.
    cdx_url = f"http://web.archive.org/cdx/search/cdx?url={url}&matchType=domain&filter=statuscode:200&fl=timestamp&output=JSON"

    # Add correct params to cdx_url
    if frequency:
        cdx_url += f"&collapse=timestamp:{frequency}"

    if limit:
        cdx_url += f"&limit={limit}"

    if start_date:
        cdx_url += f"&from={start_date}"

    if end_date:
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
            "GTM_codes": {
                "GTM-1234567890": {
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
        "GTM_codes": {},
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
                    GTM_codes = get_GTM_code(html)

                    # above functions return lists, so iterate thru codes and update
                    # results dict
                    for code in UA_codes:
                        if code not in results["UA_codes"]:
                            results["UA_codes"][code] = {}
                            results["UA_codes"][code]["first_seen"] = get_date_from_timestamp(timestamp)
                            results["UA_codes"][code]["last_seen"] = get_date_from_timestamp(timestamp)

                        if code in results["UA_codes"]:
                            results["UA_codes"][code]["last_seen"] = get_date_from_timestamp(timestamp)

                    for code in GA_codes:
                        if code not in results["GA_codes"]:
                            results["GA_codes"][code] = {}
                            results["GA_codes"][code]["first_seen"] = get_date_from_timestamp(timestamp)
                            results["GA_codes"][code]["last_seen"] = get_date_from_timestamp(timestamp)

                        if code in results["GA_codes"]:
                            results["GA_codes"][code]["last_seen"] = get_date_from_timestamp(timestamp)

                    for code in GTM_codes:
                        if code not in results["GTM_codes"]:
                            results["GTM_codes"][code] = {}
                            results["GTM_codes"][code]["first_seen"] = get_date_from_timestamp(timestamp)
                            results["GTM_codes"][code]["last_seen"] = get_date_from_timestamp(timestamp)

                        if code in results["GTM_codes"]:
                            results["GTM_codes"][code]["last_seen"] = get_date_from_timestamp(timestamp)

            # TODO: Add better/clearer error handling here
            except Exception as e:
                print("ERROR in ASYNC ARCHIVE CODES", e)
                return None

        print("FINISH CODES FOR", base_url.format(timestamp=timestamp))
