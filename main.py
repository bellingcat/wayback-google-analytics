import aiohttp
import asyncio
import argparse
from osint_ga.utils import (
    get_limit_from_frequency
)

from osint_ga.scraper import (
    get_analytics_codes,
    COLLAPSE_OPTIONS,
)

async def main(args):
    """Main function. Runs get_analytics_codes() and prints results.

    Args:
        args: Command line arguments (argparse)

    Returns:
        None
    """

    if args.frequency:
        args.limit = get_limit_from_frequency(
            frequency=args.frequency,
            start_date=args.start_date,
            end_date=args.end_date,
        ) + 1
        args.frequency = COLLAPSE_OPTIONS[args.frequency]

    async with aiohttp.ClientSession() as session:
        results = await get_analytics_codes(
            session=session,
            urls=args.urls,
            start_date=args.start_date,
            end_date=args.end_date,
            frequency=args.frequency,
            limit=args.limit,
        )
        print(results)


def setup_args():
    """Setup command line arguments. Returns args for use in main().

    CLI Args:
        --urls: List of urls to scrape
        --start_date: Start date for time range. Defaults to Oct 1, 2012, when UA codes were adopted.
        --end_date: End date for time range. Defaults to None.
        --frequency: Can limit snapshots to remove duplicates (1 per hr, day, month, etc). Defaults to None.
        --limit: Limit number of snapshots returned. Defaults to None.

    Returns:
        Command line arguments (argparse)
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--urls",
        nargs="+",
        required=True,
        help="Enter a list of urls separated by spaces to get their UA/GA codes (e.g. --urls https://www.google.com https://www.facebook.com)",
    )
    parser.add_argument(
        "--start_date",
        default="20121001000000",
        help="Start date for time range. Defaults to Oct 1, 2012, when UA codes were adopted.",
    )
    parser.add_argument(
        "--end_date",
        default=None,
        help="End date for time range. Defaults to None.",
    )
    parser.add_argument(
        "--frequency",
        default=None,
        help="Can limit snapshots to remove duplicates (1 per hr, day, month, etc). Defaults to None.",
    )
    parser.add_argument(
        "--limit",
        default=-100,
        help="Limits number of snapshots returned. Defaults to -100.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = setup_args()
    asyncio.run(main(args))
