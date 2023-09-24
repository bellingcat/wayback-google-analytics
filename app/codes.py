import re

def get_UA_code(html):
    """Returns UA codes (w/o duplicates) from given html, or None if not found.

    Args:
        html (str): Raw html.

    Returns:
        ["UA-12345678-1", "UA-12345678-2", ...]
    """

    # Regex pattern to find UA codes
    pattern = re.compile(r"UA-[a-zA-Z0-9-]{5,15}")

    # Find all UA codes in html
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
    pattern = re.compile(r"G-[a-zA-Z0-9-]{5,15}")

    # Find all GA codes in html or return None
    try:
        GA_codes = pattern.findall(html)
    except Exception as e:
        print(e)
        return None

    # Remove duplicates and return
    return list(set(GA_codes))


def get_GTM_code(html):
    """Returns GTM codes (w/o duplicates) from given html, or None if not found.
    Args:
        html (str): Raw html.
    Returns:
        ["GTM-1234567890", "GTM-1234567891", ...]
    """

    # This pattern
    pattern = re.compile(r"GTM-[A-Za-z0-9]{1,}")

    # Find all GTM codes in html or return None
    try:
        GTM_codes = pattern.findall(html)
    except Exception as e:
        print(e)
        return None

    # Remove duplicates and return
    return list(set(GTM_codes))