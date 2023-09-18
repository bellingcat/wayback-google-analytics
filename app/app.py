from bs4 import BeautifulSoup
import re
import requests

DEFAULT_HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

COLLAPSE_OPTIONS = {
    "hour": "10",
    "day": "8",
    "month": "6",
    "year": "4",
}

# NOTE: All of these are proof of concept tests and are WIP.


def get_analytics_codes(
    urls,
    start_date="20121001000000",
    end_date=None,
    frequency=None,
    limit=None,
):
    """Takes array of urls and returns array of dictionaries with all found analytics codes for a given time range.
    If no time range is given, returns all analytics codes for each url.

    Args:
        urls (array): Array of urls to scrape.
        start_date (str, optional): Start date for time range. Defaults to Oct 1, 2012, when UA codes were adopted.
        end_date (str, optional): End date for time range. Defaults to None.
        frequency (str, optional): Can limit snapshots to remove duplicates (1 per hr, day, month, etc). Defaults to None.
        limit (int, optional): Limit number of snapshots returned. Defaults to None.
        direction (str, optional): Determines whether to start looking for UA codes from earliest snapshot or most recent. Defaults to "asc".

    Returns:
        {
            "someurl.com": {
                "current_UA_code": "UA-12345678-1",
                "current_GA_code": "G-1234567890",
                "archived_UA_codes": {
                    "UA-12345678-1": ["20190101000000", "20190102000000", ...],
                    "UA-12345678-2": ["20190101000000", "20190102000000", ...],
                },
                "archived_GA_codes": {
                    "G-1234567890": ["20190101000000", "20190102000000", ...],
                },
            }
        }

    TODO: Currently doesn't include GTM-ids.
    """

    # initialize results array
    results = []

    # Get data for each url:
    for url in urls:
        # add step to format URLs with a given scheme if not already present???
        curr_entry = {url: {}}
        html = get_html(url)
        if html:
            curr_entry["current_UA_code"] = get_UA_code(html)
            curr_entry["current_GA_code"] = get_GA_code(html)
            curr_entry["title"] = get_page_title(html)

        # get all archived UA_codes and GA codes

        # get snapshot timestamps
        snapshot_timestamps = get_snapshot_timestamps(
            url=url,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
            limit=limit,
        )

        # visit each snapshot to get codes
        archived_codes = get_codes_from_snapshots(url=url, timestamps=snapshot_timestamps)
        curr_entry["archived_UA_codes"] = archived_codes["UA_codes"]
        curr_entry["archived_GA_codes"] = archived_codes["GA_codes"]

        results.append(curr_entry)

    return results


def get_snapshot_timestamps(
    url,
    start_date="20121001000000",
    end_date=None,
    frequency=None,
    limit=None,
):
    """Takes a url and returns an array of snapshot timestamps for a given time range.

    Args:
        url (str)
        start_date (str, optional): Start date for time range. Defaults to Oct 1, 2012, when UA codes were adopted.
        end_date (str, optional): End date for time range. Defaults to None.
        frequency (str, optional): Can limit snapshots to remove duplicates (1 per hr, day, week, etc). Defaults to None.
        limit (int, optional): Limit number of snapshots returned. Defaults to None.
        direction (str, optional): Determines whether to start looking for UA codes from earliest snapshot or most recent. Defaults to "asc".

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

    # Get snapshots for each url
    response = requests.get(
        url=cdx_url,
        headers=DEFAULT_HEADERS,
    )
    timestamps = pattern.findall(response.text)

    # Return sorted timestamps
    return sorted(timestamps)


def get_codes_from_snapshots(url, timestamps):
    """Takes a url and array of snapshot timestamps and returns a dictionary of UA/GA codes.

    Args:
        url (str)
        timestamps (array): Array of snapshot timestamps.

    Returns:
        {
            "UA_codes": {
                "UA-12345678-1": {
                    "first_seen": "20190101000000",
                    "last_seen": "20190102000000",
                },
            },
            "GA_codes: {
                "G-1234567890": {
                    "first_seen": "20190101000000",
                    "last_seen": "20190102000000",
                },
            },
        }
    """

    # build base url template for wayback machine
    base_url = "https://web.archive.org/web/{timestamp}/" + url

    # initialize results dictionary
    results = {
        "UA_codes": {},
        "GA_codes": {},
    }

    # get codes from each snapshot
    for timestamp in timestamps:
        # format url and get raw html
        curr_url = base_url.format(timestamp=timestamp)
        html = get_html(curr_url)

        if html:
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

    return results


def get_html(url):
    """Returns raw html from given url."""

    try:
        print(url)
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=60)
    except Exception as e:
        print(e)
        return None

    html = response.text
    return html


def get_UA_code(html):
    """Returns UA codes (w/o duplicates) from given html, or None if not found."""

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
    """Returns GA codes (w/o duplicates) from given html, or None if not found."""

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
