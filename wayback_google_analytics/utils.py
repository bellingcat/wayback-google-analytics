from datetime import datetime
from dateutil.relativedelta import relativedelta

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
    """Returns an appropriate limit for a given frequency to be used w/ the CDX api.

    Args:
        frequency (str): Frequency (hourly, daily, monthly, yearly)
        start_date (str): 14-digit timestamp for starting point
        end_date (str): 14-digit timestamp for end of range

    Returns:
        int: Limit for CDX api
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


def validate_dates(start_date, end_date):
    """Returns True if start_date is before end_date, False otherwise.

    Args:
        start_date (str): Date (dd:mm:YY:HH:MM) for starting point
        end_date (str): Date (dd:mm:YY:HH:MM) for end of range

    Returns:
        bool: True if start_date is before end_date, False otherwise.
    """

    # Get start and end dates as datetime objects
    try:
        start_date = datetime.strptime(start_date, "%d/%m/%Y:%H:%M")
    except ValueError:
        start_date = datetime.strptime(start_date, "%d/%m/%Y")

    try:
        end_date = datetime.strptime(end_date, "%d/%m/%Y:%H:%M")
    except ValueError:
        end_date = datetime.strptime(end_date, "%d/%m/%Y")

    # Return True if start_date is before end_date
    if start_date < end_date:
        return True

    # Return False if start_date is after end_date
    return False


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

def generate_semaphore(url_list, limit):
    """Generates appropriate semaphore given a list of urls and a limit."""

    url_count = len(url_list)

    operations = url_count * limit

    if operations <= 100:
        return 10

    if operations <= 1000:
        return 5

    if operations <= 10000:
        return 1