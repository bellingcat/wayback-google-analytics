# Overview

OSINT Google Analytics is a lightweight tool that gathers current and historic
Google analytics data (UA, GA and GTM codes) from a collection of website urls. UA codes are a particularly
useful data point for OSINT investigators, but they're being phased out in Google's GA4.

Luckily, the Internet Archive's Wayback Machine allows us to look back and find older codes. This tool finds
Wayback snapshots using the CDX API and then returns a dictionary of current and previous codes. The results can be returned as text in a json or txt file, or returned as a csv or xlsx database for archival purposes.

The raw output looks something like this:

```json
        "someurl.com": {
            "current_UA_code": "UA-12345678-1",
            "current_GA_code": "G-1234567890",
            "current_GTM_code": "GTM-12345678",
            "archived_UA_codes": {
                "UA-12345678-1": {
                    "first_seen": "01/01/2019(12:30)",
                    "last_seen": "03/10/2020(00:00)",
                },
            },
            "archived_GA_codes": {
                "G-1234567890": {
                    "first_seen": "01/01/2019(12:30)",
                    "last_seen": "01/01/2019(12:30)",
                }
            },
            "archived_GTM_codes": {
                "GTM-12345678": {
                    "first_seen": "01/01/2019(12:30)",
                    "last_seen": "01/01/2019(12:30)",
                },
        },
    }
```

# Installation

#### Install from source

1. Clone repo:

```terminal
git clone git@github.com:jclark1913/osint-google-analytics.git
```

2. Navigate to root, create a venv and install requirements.txt:

```terminal
cd osint-google-analytics
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Get a high-level overview:

```terminal
python main.py -help
```

# Usage

1. Enter a list of urls manually through the command line using `--urls` or from a given file using `--input_file`.

2. Specify your output format (.csv, .txt, .xlsx or .csv) using `--output`.

3. Add any of the following options:

Options list (run `python main.py -h` to see in terminal):

```terminal
options:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input_file INPUT_FILE
                        Enter a file path to a list of urls in a readable file
                        type (e.g. .txt, .csv, .md)
  -u URLS [URLS ...], --urls URLS [URLS ...]
                        Enter a list of urls separated by spaces to get their
                        UA/GA codes (e.g. --urls https://www.google.com
                        https://www.facebook.com)
  -o {csv,txt,json,xlsx}, --output {csv,txt,json,xlsx}
                        Enter an output type to write results to file.
                        Defaults to json.
  -s START_DATE, --start_date START_DATE
                        Start date for time range (dd/mm/YYYY:HH:MM) Defaults
                        to 01/10/2012:00:00, when UA codes were adopted.
  -e END_DATE, --end_date END_DATE
                        End date for time range (dd/mm/YYYY:HH:MM). Defaults
                        to None.
  -f {yearly,monthly,daily,hourly}, --frequency {yearly,monthly,daily,hourly}
                        Can limit snapshots to remove duplicates (1 per hr,
                        day, month, etc). Defaults to None.
  -l LIMIT, --limit LIMIT
                        Limits number of snapshots returned. Defaults to -100
                        (most recent 100 snapshots).

```

Examples:

To get current codes for two websites and archived codes between Oct 1, 2012 and Oct 25, 2012:
`python main.py --urls https://someurl.com https://otherurl.org --output json --start_date 01/10/2012 --end_date 25/10/2012 --frequency hourly`

To get current codes for a list of websites (from a file) from January 1, 2012 to the present day, checking for snapshots monthly and returning it as an excel spreadsheet:
`python main.py --input_file path/to/file.txt --output xlsx --start_date 01/01/2012`

To check a single website for its current codes plus codes from the last 2,000 archive.org snapshots:
`python main.py --urls https://someurl.com --limit -2000`

# Contact

-- <a href="https://github.com/jclark1913">Github</a>
-- <a href="https://twitter.com/JustinClarkJO">Twitter</a>
-- <a href="https://www.linkedin.com/in/justin-w-clark/">Linkedin</a>

Or email me at jclarksummit@gmail.com

# Further Reading

- For more info about analytics codes and what the GA-4 rollout means for OSINT: [https://digitalinvestigations.substack.com/p/what-the-rollout-of-google-analytics]

- For an example investigation usings analytics codes: [https://www.bellingcat.com/resources/how-tos/2015/07/23/unveiling-hidden-connections-with-google-analytics-ids/]