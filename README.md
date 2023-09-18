# Overview

This is a collection of WIP, proof-of-concept scripts for a small tool that gathers current and historic
Google analytics data (UA and GA codes) from a collection of website urls. UA codes are a particularly
useful data point for OSINT investigators (see: [https://www.bellingcat.com/resources/how-tos/2015/07/23/unveiling-hidden-connections-with-google-analytics-ids/]), but they're being phased out in Google's GA4.

Luckily, the Internet Archive's Wayback Machine allows us to look back and find older codes. This tool finds
Wayback snapshots using the CDX API and then returns a dictionary of current and previous codes. The output looks
like:

```json
    {
        "someurl.com": {
            "current_UA_code": "",
            "current_GA_code": "G-1234567890",
            "archived_UA_codes": {
                "UA-12345678-1": ["20190101000000", "20190102000000", ...],
                "UA-12345678-2": ["20190101000000", "20190102000000", ...],
            },
            "archived_GA_codes": {
                "G-1234567890": ["20190101000000", "20190102000000", ...],
            },
        },
        ...
    }

```

For more info about UA-codes and what the GA-4 rollout means for OSINT: [https://digitalinvestigations.substack.com/p/what-the-rollout-of-google-analytics]