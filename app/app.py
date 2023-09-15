from bs4 import BeautifulSoup
import re
import requests

DEFAULT_HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

# NOTE: All of these are proof of concept tests and are WIP.


def scrape_websites(urls):
    """Takes array of urls and scrapes each webpage for GA and UA codes.

    Returns:
        Array of dictionaries for each url:
            {
                "title": "Page Title",
                "url": "https://www.example.com",
                "UA_codes": ["UA-12345678-1", "UA-12345678-2"], # duplicates removed
                "GA_codes": ["G-1234567890"], # duplicates removed
                "html": "<html>...</html>" # optional
            }

    """

    results = []
    for url in urls:
        html = get_html(url)
        if html:
            UA_codes = get_UA_code(html)
            GA_codes = get_GA_code(html)
            title = get_page_title(html)
            results.append(
                {
                    "title": title,
                    "url": url,
                    "UA_codes": UA_codes,
                    "GA_codes": GA_codes,
                    # "html": html,
                }
            )

    return results


def get_html(url):
    """Returns raw html from given url."""
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=10)
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


def find_archived_urls(urls):
    """Takes array of urls and returns array of archived snapshots from Internet Archive's
    CDX API.
    """

    results = []
    for url in urls:
        response = requests.get(
            url=f"http://web.archive.org/cdx/search/cdx?url={url}&output=JSON",
            headers=DEFAULT_HEADERS,
        )
        results.append(response)

    return results
