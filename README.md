# Phase 1:

## Scrape websites for their google analytics codes

- Function should take array of urls
- Should iterate over them and scrape their html (bs4) and then find their google analytics code. Should take that analytics code and put it into a dictionary that looks like this.

```
[
    {
        title: "Webpage title",
        url: "www.webpage.com",
        UA-code: UA-XXXXXXX (NULL if non-existent)
        GA-code: GA-XXXXXXX (NULL if non-existent)
    }
]
```

### BIG QUESTIONS FOR PHASE 1:
- Do I need a setting to determine whether or not we should get archival data on the first pass?

# Phase 2:

## Use wayback machine API to get older versions and use their data.

- After the initial run-through, we circle back to look for older websites that may contain that UA code.
- Function iterates over earlier dictionaries. If we don't have a UA code, we should use the wayback machine starting from most recent to least recent until we find a UA code.
- Dictionary should be updated to look like this

```
[
    {
        title: "Webpage title",
        url: "www.webpage.com",
        UA-code: UA-XXXXXXX (NULL if non-existent)
        GA-code: GA-XXXXXXX (NULL if non-existent)
        archived_urls: {
            [
                url1, url2, etc...
            ]
        }
        archived_ua_codes: {
            [
                {
                    UA-code: UA-XXXXXX,
                    date: 11/11/11,
                    url: ...
                }
            ]
        }
    }
]
```

### BIG QUESTIONS FOR PHASE 2

- A codes rolled out in 2012 and were discontinued in 2023. Time range should start in 2012, but we can continue til today due to presence of legacy codes.
- Wayback CDX API does a good job of responding quickly to calls, but some have 100s of snapshots. What is a good way to scrape and get codes w/o having to overload the CDX API with needless calls?
    - Maybe an interval? Find nearest snapshot to each 6 month/1 year increment?
    - How often do UA codes change?
- Result format may need to update to something w/ more details about each UA code provided there's more.

```
{
    result:
        {
            url1: {
                UA-XXXXXX: {
                    last_used: date,
                    first_used: date
                }
                UA-YYYYYY: 1
            }
        }
}
```