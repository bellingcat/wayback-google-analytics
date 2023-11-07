import aiohttp
import argparse
import asyncio

from wayback_google_analytics.utils import (
    get_limit_from_frequency,
    get_14_digit_timestamp,
    validate_dates,
    COLLAPSE_OPTIONS,
)

from wayback_google_analytics.scraper import (
    get_analytics_codes,
)

from wayback_google_analytics.output import (
    init_output,
    write_output,
)


async def main(args):
    """Main function. Runs get_analytics_codes() and prints results.

    Args:
        args: Command line arguments (argparse)

    Returns:
        None
    """

    # If input_file is provided, read urls from file path
    if args.input_file:
        try:
            with open(args.input_file, "r") as f:
                args.urls = f.read().splitlines()
        except FileNotFoundError:
            print("File not found. Please enter a valid file path.")
            return

    # Throws ValueError immediately if output type is incorrect or there is an issue writing to file
    if args.output:
        output_file = init_output(args.output)

    # Check if start_date is before end_date
    if args.start_date and args.end_date:
        if not validate_dates(args.start_date, args.end_date):
            raise ValueError("Start date must be before end date.")

    # Update dates to 14-digit format
    if args.start_date:
        args.start_date = get_14_digit_timestamp(args.start_date)

    if args.end_date:
        args.end_date = get_14_digit_timestamp(args.end_date)

    # Gets appropriate limit for given frequency & converts frequency to collapse option
    if args.frequency:
        args.limit = (
            get_limit_from_frequency(
                frequency=args.frequency,
                start_date=args.start_date,
                end_date=args.end_date,
            )
            + 1
        )
        args.frequency = COLLAPSE_OPTIONS[args.frequency]

    semaphore = asyncio.Semaphore(10)

    # Warn user if large request
    if abs(int(args.limit)) > 500 or len(args.urls) > 9:
        response = input(
            f"""Large requests can lead to being rate limited by archive.org.\n\n Current limit: {args.limit} (Recommended < 500) \n\n Current # of urls: {len(args.urls)} (Recommended < 10, unless limit < 50)

        Do you wish to proceed? (Yes/no)
                         """
        )
        if response.lower() not in ("yes", "y"):
            print("Request cancelled.")
            exit()

    try:
        async with semaphore:
            async with aiohttp.ClientSession() as session:
                results = await get_analytics_codes(
                    session=session,
                    urls=args.urls,
                    start_date=args.start_date,
                    end_date=args.end_date,
                    frequency=args.frequency,
                    limit=args.limit,
                    semaphore=semaphore,
                    skip_current=args.skip_current,
                )
                print(results)

        # handle printing the output
        if args.output:
            write_output(output_file, args.output, results)
    except aiohttp.ClientError as e:
        print(
            "Your request was rate limited. Wait 5 minutes and try again and consider reducing the limit and # of numbers."
        )


def setup_args():
    """Setup command line arguments. Returns args for use in main().

    CLI Args:
        --urls: List of urls to scrape
        --start_date: Start date for time range. Defaults to Oct 1, 2012, when UA codes were adopted.
        --end_date: End date for time range. Defaults to None.
        --frequency: Can limit snapshots to remove duplicates (1 per hr, day, month, etc). Defaults to None.
        --limit: Limit number of snapshots returned. Defaults to None.
        --skip_current: Add this flag to skip current UA/GA codes when getting archived codes.

    Returns:
        Command line arguments (argparse)
    """

    parser = argparse.ArgumentParser()

    # Argparse group to prevent user from entering both --input_file and --urls
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-i",
        "--input_file",
        default=None,
        help="Enter a file path to a list of urls in a readable file type (e.g. .txt, .csv, .md)",
    )
    group.add_argument(
        "-u",
        "--urls",
        nargs="+",
        help="Enter a list of urls separated by spaces to get their UA/GA codes (e.g. --urls https://www.google.com https://www.facebook.com)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="json",
        help="Enter an output type to write results to file. Defaults to json.",
        choices=["csv", "txt", "json", "xlsx"],
    )
    parser.add_argument(
        "-s",
        "--start_date",
        default="01/10/2012:00:00",
        help="Start date for time range (dd/mm/YYYY:HH:MM) Defaults to 01/10/2012:00:00, when UA codes were adopted.",
    )
    parser.add_argument(
        "-e",
        "--end_date",
        default=None,
        help="End date for time range (dd/mm/YYYY:HH:MM). Defaults to None.",
    )
    parser.add_argument(
        "-f",
        "--frequency",
        default=None,
        help="Can limit snapshots to remove duplicates (1 per hr, day, month, etc). Defaults to None.",
        choices=["yearly", "monthly", "daily", "hourly"],
    )
    parser.add_argument(
        "-l",
        "--limit",
        default=-100,
        help="Limits number of snapshots returned. Defaults to -100 (most recent 100 snapshots).",
    )
    parser.add_argument(
        "-sc",
        "--skip_current",
        action="store_true",
        help="Add this flag to skip current UA/GA codes when getting archived codes.",
    )

    return parser.parse_args()


def main_entrypoint():
    args = setup_args()
    asyncio.run(main(args))


if __name__ == "__main__":
    main_entrypoint()
