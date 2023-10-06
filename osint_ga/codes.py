from bs4 import BeautifulSoup
import re


def get_UA_code(html):
    """Returns UA codes (w/o duplicates) from given html, or None if not found.

    Args:
        html (str): Raw html.

    Returns:
        ["UA-12345678-1", "UA-12345678-2", ...]
    """

    # Only search for codes in script tags
    script_tags = BeautifulSoup(html, "html.parser").find_all("script")

    # Regex pattern to find UA codes
    pattern = re.compile(r"UA-[\d-]{5,15}")

    # Find all UA codes in html

    UA_codes = []
    for script in script_tags:
        curr_codes = pattern.findall(script.text)
        UA_codes += curr_codes


    # Remove duplicates and return
    return list(set(UA_codes))


def get_GA_code(html):
    """Returns GA codes (w/o duplicates) from given html, or None if not found.

    Args:
        html (str): Raw html.

    Returns:
        ["G-1234567890", "G-1234567891", ...]
    """

    # Only search for codes in script tags
    script_tags = BeautifulSoup(html, "html.parser").find_all("script")

    # Regex pattern to find GA codes
    pattern = re.compile(r"G-[\d-]{5,15}")

    # Find all GA codes in html or return None

    GA_codes = []
    for script in script_tags:
        curr_codes = pattern.findall(script.text)
        GA_codes += curr_codes

    # Remove duplicates and return
    return list(set(GA_codes))


def get_GTM_code(html):
    """Returns GTM codes (w/o duplicates) from given html, or None if not found.
    Args:
        html (str): Raw html.

    Returns:
        ["GTM-1234567890", "GTM-1234567891", ...]
    """

    # Only search for codes in script tags
    script_tags = BeautifulSoup(html, "html.parser").find_all("script")

    # This pattern
    pattern = re.compile(r"GTM-[\w-]{1,15}")

    # Find all GTM codes in html or return None

    GTM_codes = []
    for script in script_tags:
        curr_codes = pattern.findall(script.text)
        GTM_codes += curr_codes


    # Remove duplicates and return
    return list(set(GTM_codes))
