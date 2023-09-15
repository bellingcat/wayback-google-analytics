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
        html: raw bs4 html response
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
        html: raw bs4 html response
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

- How far back should we go? Some websites might have hundreds of previous snapshots. Should there be settings for a deep dive to all the oldest versions? 
- Is there a better way for the results to be shown? Something like

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
