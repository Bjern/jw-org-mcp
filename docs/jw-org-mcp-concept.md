# JW.Org MCP Tool

## Overview

The JW.Org MCP Tool is a Model Context Protocol (MCP)-compatible service designed to interface with jw.org in a controlled, reliable, and verifiable way.
Since large language models (LLMs) cannot always guarantee that scriptural or doctrinal information originates exclusively from jw.org, this MCP tool enforces source integrity by retrieving and serving only content directly from jw.org.

This ensures that any application, AI agent, or desktop tool integrating through the MCP ecosystem can confidently provide **accurate, verifiable**, and **official** information from jw.org — free from external noise or hallucinations.

## Core Features

- **Trusted Source Enforcement**: Fetches data strictly from jw.org domains, ensuring doctrinal accuracy and preventing external contamination.
- **Optimized Performance**: Lightweight requests (no JavaScript or image rendering) with Brotli compression for faster response times and reduced bandwidth usage.
- **Structured Output**: Normalizes jw.org content into machine-friendly formats (e.g., clean text, structured JSON, or Markdown summaries).
- **Flexible Query Modes**: 
  Supports multiple query methods:
  - Topic search (e.g., “Jehovah’s love”)
  - Article lookup (by URL)
  - Publication or magazine filtering (e.g., Watchtower, Awake!)
  - Scripture reference search
- **Caching Layer (optional)**: Local or temporary caching for repeated queries to minimize redundant network calls.

## How to search
(The MCP endpoint will need to follow these instructions to get results, ultimately this can be broken up into a service)

Instructions on how to use the search with examples. Let use the example where a user requests from the LLM tool 
"what does the bible say about peace and security?". Since the entire website features what the bible says it makes no sense
to search this. The target search subject would be "peace and security", and the answer "what does the bible say" should be 
determined from the results. It's important to understand this because these would be parameters in the MCP tool. A good parameter
explanation will help the LLM to decide what to use. For example a `subject_search` param. The LLM should also be able to determine
from the results if it's finding the right answers. An additional parameter would be the search type. See the table below
detailing the different types of searches and notes on the response structure it returns.

Next is the flow for the MCP server to get ALL results in the example provided:
- Make a request to the url https://www.jw.org/en/ (One time only, no media is required)
- One of the resources will be a CDN, for example https://b.jw-cdn.org/ This may change so find it using the pattern: ends with `.jw-cdn.org`
- Using the CDN as a base url get the auth token, for eg:  https://b.jw-cdn.org/tokens/jworg.jwt Which returns a JWT token
- Keeping that token, all subsequent requests will need to be passed that token.
- Making a search for the expression "peace and security" in the browser will redirect to https://www.jw.org/en/search/?q=peace+and+security but this information is derived from the CDN https://b.jw-cdn.org/apis/search/results/E/all?q=peace+and+security
  - https://b.jw-cdn.org/ = The CDN base url
  - apis/search/results/ = A standard url for search results
  - E/ = The language
  - all?q=peace+and+security = Searching all articles for the search term

Here are the requests headers that were used in the example:
```
GET /apis/search/results/E/all?q=peace+and+security HTTP/2
Host: b.jw-cdn.org
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0
Accept: application/json; charset=utf-8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br, zstd
Referer: https://www.jw.org/
X-Client-ID: bddc616d-a519-4077-a0c2-307ecaac961c
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InJRdmlDaV9yalVRc3lQVWhPRUxHaHpuU0F3aDFnb3NlY1lHOHVwVEUzbU0ifQ.eyJqdGkiOiI4MmFjMWM4Yi1hNWU3LTQ0YjYtYmNiOS1lN2Y1MmRkMjNmODQiLCJzdWIiOiJ3d3cuancub3JnLXB1YmxpYyIsImlzcyI6Imp3b3JnOmF1dGg6cHJkIiwiaWF0IjoxNzYwMzY0MDI5LCJuYmYiOjE3NjAzNjQwMjksImV4cCI6MTc2MDk2ODgyOSwicG1hcGkiOnsiYXVkaWVuY2VzIjpbImdlbmVyYWwtcHVibGljIl0sInN0YXRlcyI6WyJwcm9kdWN0aW9uIl19LCJhdWQiOlsiTXVsdGlTaXRlU2VhcmNoOnByZCIsIkpXQk1lZGlhdG9yOnByZCIsIkFsZXJ0czpwcmQiLCJPbW5pU2VhcmNoOnByZCIsImRhbXM6cHViLW1lZGlhLWFwaTpwcmQiXSwicGVybXMiOnsib21uaS1zZWFyY2giOnsic2l0ZXMiOlsiancub3JnOnByZCIsIndvbDpwcmQiXSwiZmlsdGVycyI6WyJhbGwiLCJwdWJsaWNhdGlvbnMiLCJ2aWRlb3MiLCJhdWRpbyIsImJpYmxlIiwiaW5kZXhlcyJdLCJ0YWdzIjp7ImV4Y2x1ZGVkIjpbIlNlYXJjaEV4Y2x1ZGUiLCJXV1dFeGNsdWRlIl19fSwic2VhcmNoIjp7ImZhY2V0cyI6W3sibmFtZSI6InR5cGUiLCJmaWVsZCI6InRhZ3MiLCJ2YWx1ZXMiOlsidHlwZTp2aWRlbyJdfV19fX0.XTpuSPE1JJVD854M0H9HN-sjJYvQevVleSoilvW5Yz_UCbroHE6ZkZVFjvTAHmFsLXCuLyO6B7PfPyelxr5JF4guS9EN3JsABHVKI6bBVmJ8-8LS7VyPhXsL9_VcClPwHQEJMfCIXv7BjURgTknFbH37NXUEJ-F5fhmOBLYhT025eTx1lz47UPAJmyXkwslZcWiJ-8Jx5KXNkSSKaoahb2vttEWcK1zYftQLYiITiXtDgg-p6YZEiByykdFAoeqo_BBlbmTgvHoJx5etM-SeG0SE8FmEOpLlMj3plbx0u6Lmd2BHnkDC32Y4h5ceMOJuS61zKPX6csEx0u7XE0KJBQ
Origin: https://www.jw.org
Connection: keep-alive
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: cross-site
Priority: u=4
```

This returns the JSON response below (Long!):
The information being searched for can be found in the `results` array. For each result, there is a type. If the type 
is `group` then these are articles found in the search. There will be a nested `results` array (results[0].results) in each type of `group`. This contains
a `subtype` of `article` (results[0].results[0].subtype='article'). Extract the `title` (results[0].results[0].title) and `snippet` (results[0].results[0].snippet) 
for the LLM to decide which fits the best, or present this to the user as options.

To get the information for digest there is a `links` object which uses the finder url for eg: https://wol.jw.org/wol/finder. 
Using the article link will redirect for eg: https://wol.jw.org/en/wol/d/r1/lp-e/1985720?q=peace+and+security&p=doc . On this web
page there will be an HTML tag something like `<article id="article" class="article...` This is the article content. Nested
within this article will be a paragraph tag like `<p id="p1" data-pid="1"...`. The id's increment for each paragraph, but you will need
all of these paragraphs. The text is contained within. A highlighting may be in place found in span tags, this can be ignored.

#### Response returned for `all`
```json
{
  "layout": [
    "flat"
  ],
  "results": [
    {
      "type": "group",
      "links": [],
      "layout": [
        "flat"
      ],
      "results": [
        {
          "type": "item",
          "subtype": "article",
          "links": {
            "wol": "https://wol.jw.org/wol/finder?wtlocale=E&docid=1985720&q=peace+and+security&p=doc&srcid=sch&srctype=jwo"
          },
          "lank": "pa-1985720",
          "context": "The Watchtower (1985)",
          "title": "Peace and Security—The Hope",
          "snippet": "<strong>Peace</strong> and <strong>Security</strong>—The Hope\n“The General Assembly of the United Nations unanimously declared 1986 as the International Year of <strong>Peace</strong>. The Year will be solemnly proclaimed on 24 October 1985, the fortieth anniversary of the United Nations.”",
          "image": {
            "type": "sqs"
          },
          "insight": {
            "rank": 1,
            "lank": "pa-1985720",
            "group": {
              "rank": 1,
              "key": "all"
            }
          }
        },
        {
          "type": "item",
          "subtype": "article",
          "links": {
            "wol": "https://wol.jw.org/wol/finder?wtlocale=E&docid=1985760&q=peace+and+security&p=doc&srcid=sch&srctype=jwo"
          },
          "lank": "pa-1985760",
          "context": "The Watchtower (1985)",
          "title": "Peace and Security—The Need",
          "snippet": "<strong>Peace</strong> and <strong>Security</strong>—The Need",
          "image": {
            "type": "sqs"
          },
          "insight": {
            "rank": 2,
            "lank": "pa-1985760",
            "group": {
              "rank": 1,
              "key": "all"
            }
          }
        }
      ]
    },
    {
      "type": "group",
      "label": "Index Subjects",
      "links": [
        {
          "type": "more",
          "label": "See All",
          "link": "/results/E/indexes?sort=rel&q=peace%20and%20security"
        }
      ],
      "layout": [
        "linkGroup"
      ],
      "results": [
        {
          "type": "item",
          "subtype": "index",
          "links": {
            "wol": "https://wol.jw.org/wol/finder?wtlocale=E&docid=1200275943&q=peace+and+security&p=doc&srcid=sch&srctype=jwo"
          },
          "lank": "pa-1200275943",
          "context": "Watch Tower Publications Index 1986-2026",
          "title": "True Peace and Security—From What Source? (Book) (dx86-26)",
          "snippet": "TRUE <strong>PEACE</strong> AND <strong>SECURITY</strong>—FROM WHAT SOURCE? (Book)\n(See also Watch Tower Publications)\nEthiopia: yb92 131\nexperiences:\nSouth Africa: g88 1/22 27; g86 1/22 21-22\nThailand: yb91 242",
          "image": {
            "type": "sqs"
          },
          "insight": {
            "rank": 1,
            "lank": "pa-1200275943",
            "group": {
              "rank": 2,
              "key": "indexes"
            }
          }
        },
        {
          "type": "item",
          "subtype": "index",
          "links": {
            "wol": "https://wol.jw.org/wol/finder?wtlocale=E&docid=1200275944&q=peace+and+security&p=doc&srcid=sch&srctype=jwo"
          },
          "lank": "pa-1200275944",
          "context": "Watch Tower Publications Index 1986-2026",
          "title": "True Peace and Security—How Can You Find It? (Book)",
          "snippet": "TRUE <strong>PEACE</strong> AND <strong>SECURITY</strong>—HOW CAN YOU FIND IT? (Book)\n(See also Watch Tower Publications)\nannouncement: km 2/86 3\nuse in field ministry:\nhouse to house: km 1/96 8; km 1/95 8; km 6/89 1\nreturn visits: km 1/96 8; km 1/95 8",
          "image": {
            "type": "sqs"
          },
          "insight": {
            "rank": 2,
            "lank": "pa-1200275944",
            "group": {
              "rank": 2,
              "key": "indexes"
            }
          }
        },
        {
          "type": "item",
          "subtype": "index",
          "links": {
            "wol": "https://wol.jw.org/wol/finder?wtlocale=E&docid=1200027991&q=peace+and+security&p=doc&srcid=sch&srctype=jwo"
          },
          "lank": "pa-1200027991",
          "context": "Watch Tower Publications Index 1930-1985",
          "title": "True Peace and Security—From What Source? (Book) (dx30-85)",
          "snippet": "TRUE <strong>PEACE</strong> AND <strong>SECURITY</strong>—FROM WHAT SOURCE? (Book)\nexperiences with: w79 10/15 26; w76 716\nprinting: w74 700\nrelease: yb75 251",
          "image": {
            "type": "sqs"
          },
          "insight": {
            "rank": 3,
            "lank": "pa-1200027991",
            "group": {
              "rank": 2,
              "key": "indexes"
            }
          }
        },
        {
          "type": "item",
          "subtype": "index",
          "links": {
            "wol": "https://wol.jw.org/wol/finder?wtlocale=E&docid=1200273335&q=peace+and+security&p=doc&srcid=sch&srctype=jwo"
          },
          "lank": "pa-1200273335",
          "context": "Watch Tower Publications Index 1986-2026",
          "title": "Labor Pains",
          "snippet": "LABOR PAINS\n(See also Childbirth)\nchildbirth: it-2 186-187\njudgment against Eve: it-2 186-187\nsymbolic: it-2 187-188, 675-676\nafter “<strong>peace</strong> and <strong>security</strong>” (1Th 5:3): it-2 187; w13 1/1 7\napostles’ grief at Jesus’ death: it-2 187\nwoman of Revelation 12: it-2 187, 675-676; re 178",
          "image": {
            "type": "sqs"
          },
          "insight": {
            "rank": 4,
            "lank": "pa-1200273335",
            "group": {
              "rank": 2,
              "key": "indexes"
            }
          }
        },
        {
          "type": "item",
          "subtype": "index",
          "links": {
            "wol": "https://wol.jw.org/wol/finder?wtlocale=E&docid=1200270312&q=peace+and+security&p=doc&srcid=sch&srctype=jwo"
          },
          "lank": "pa-1200270312",
          "context": "Watch Tower Publications Index 1986-2026",
          "title": "Amharic (Language)",
          "snippet": "<strong>Peace</strong> and <strong>Security</strong>—From What Source?: yb92 131\nbook Your Youth—Getting the Best Out Of It: w94 8/15 24\nbrochure Jehovah’s Witnesses—Unitedly Doing God’s Will Worldwide: w94 8/15 24",
          "image": {
            "type": "sqs"
          },
          "insight": {
            "rank": 5,
            "lank": "pa-1200270312",
            "group": {
              "rank": 2,
              "key": "indexes"
            }
          }
        },
        {
          "type": "item",
          "subtype": "index",
          "links": {
            "wol": "https://wol.jw.org/wol/finder?wtlocale=E&docid=1200275145&q=peace+and+security&p=doc&srcid=sch&srctype=jwo"
          },
          "lank": "pa-1200275145",
          "context": "Watch Tower Publications Index 1986-2026",
          "title": "Security",
          "snippet": "<strong>SECURITY</strong>\n(See also <strong>Peace</strong>; Privacy; Safety; Surety)\nairports:\nbaby passed through X-ray device: g88 7/22 30\n<strong>security</strong> checks: g 5/13 3; g02 12/8 5-7, 11-12; g89 9/22 28; g87 1/8 11\nBabylon the Great’s lack of: ws 30-32\nbasis for: it-2 706; w14 4/15 18; w02 4/15 7-8; g98 10/8 7-10; tp 175-180, 182-186; ws 6-7, 9-12",
          "image": {
            "type": "sqs"
          },
          "insight": {
            "rank": 6,
            "lank": "pa-1200275145",
            "group": {
              "rank": 2,
              "key": "indexes"
            }
          }
        }
      ]
    },
    {
      "type": "group",
      "links": [],
      "layout": [
        "flat"
      ],
      "results": [
        {
          "type": "item",
          "subtype": "article",
          "links": {
            "wol": "https://wol.jw.org/wol/finder?wtlocale=E&docid=1978242&q=peace+and+security&p=doc&srcid=sch&srctype=jwo"
          },
          "lank": "pa-1978242",
          "context": "The Watchtower (1978)",
          "title": "Peace and Security",
          "snippet": "<strong>Peace</strong> and <strong>Security</strong>\nWhen will it come?\nFrom what source?\nWhat will it mean for mankind?\n“[God] is making wars to cease to the extremity of the earth. The bow he breaks apart and does cut the spear in pieces; the [war] wagons he burns in the fire.”—Ps. 46:9.",
          "image": {
            "type": "sqs"
          },
          "insight": {
            "rank": 1,
            "lank": "pa-1978242",
            "group": {
              "rank": 3,
              "key": "all"
            }
          }
        },
        {
          "type": "item",
          "subtype": "article",
          "links": {
            "wol": "https://wol.jw.org/wol/finder?wtlocale=E&docid=1991641&q=peace+and+security&p=doc&srcid=sch&srctype=jwo"
          },
          "lank": "pa-1991641",
          "context": "The Watchtower (1991)",
          "title": "The Bible’s View of Peace and Security",
          "snippet": "The Bible’s View of <strong>Peace</strong> and <strong>Security</strong>\nMany people take at face value the apparent trend toward greater world unity and the <strong>peace</strong> and <strong>security</strong> that this might bring. They hope that such a movement will lead to a better world. But the Bible indicates that more is involved than meets the eye.",
          "image": {
            "type": "sqs"
          },
          "insight": {
            "rank": 2,
            "lank": "pa-1991641",
            "group": {
              "rank": 3,
              "key": "all"
            }
          }
        },
        {
          "type": "item",
          "subtype": "article",
          "links": {
            "wol": "https://wol.jw.org/wol/finder?wtlocale=E&docid=201986083&q=peace+and+security&p=doc&srcid=sch&srctype=jwo"
          },
          "lank": "pa-201986083",
          "context": "Kingdom Ministry—1986",
          "title": "True Peace and Security",
          "snippet": "True <strong>Peace</strong> and <strong>Security</strong>",
          "image": {
            "type": "sqs"
          },
          "insight": {
            "rank": 3,
            "lank": "pa-201986083",
            "group": {
              "rank": 3,
              "key": "all"
            }
          }
        },
        {
          "type": "item",
          "subtype": "article",
          "links": {
            "wol": "https://wol.jw.org/wol/finder?wtlocale=E&docid=1985761&q=peace+and+security&p=doc&srcid=sch&srctype=jwo"
          },
          "lank": "pa-1985761",
          "context": "The Watchtower (1985)",
          "title": "Peace and Security—Through God’s Kingdom",
          "snippet": "<strong>Peace</strong> and <strong>Security</strong>—Through God’s Kingdom\n“THE Purposes of the United Nations are: 1. To maintain international <strong>peace</strong> and <strong>security</strong>.”—Charter of the United Nations.",
          "image": {
            "type": "sqs"
          },
          "insight": {
            "rank": 6,
            "lank": "pa-1985761",
            "group": {
              "rank": 3,
              "key": "all"
            }
          }
        }
      ]
    },
    {
      "type": "group",
      "label": "Videos",
      "links": [
        {
          "type": "more",
          "label": "See All",
          "link": "/results/E/videos?sort=rel&q=peace%20and%20security"
        }
      ],
      "layout": [
        "carousel",
        "videos"
      ],
      "results": [
        {
          "type": "item",
          "subtype": "video",
          "links": {
            "jw.org": "https://www.jw.org/open?docid=1011214&item=pub-jwb-086_9_VIDEO&wtlocale=E&appLanguage=E&prefer=content"
          },
          "lank": "pub-jwb-086_9_VIDEO",
          "title": "Leonard Myers: Remain Watchful for “Peace and Security!” (1 Thess. 5:3)",
          "image": {
            "type": "lss",
            "url": "https://assetsnffrgf-a.akamaihd.net/assets/m/jwb-086/univ/art/jwb-086_univ_lss_09_lg.jpg"
          },
          "duration": "9:57",
          "insight": {
            "rank": 1,
            "lank": "pub-jwb-086_9_VIDEO",
            "group": {
              "rank": 4,
              "key": "videos"
            }
          }
        },
        {
          "type": "item",
          "subtype": "video",
          "links": {
            "jw.org": "https://www.jw.org/open?docid=1011214&item=pub-jwbvod24_19_VIDEO&wtlocale=E&appLanguage=E&prefer=content"
          },
          "lank": "pub-jwbvod24_19_VIDEO",
          "title": "Gary Breaux: Protect Yourself From Misinformation (Dan. 11:27)",
          "image": {
            "type": "lss",
            "url": "https://cms-imgp.jw-cdn.org/img/p/jwbvod24/univ/art/jwbvod24_univ_lss_19_lg.jpg"
          },
          "duration": "9:08",
          "insight": {
            "rank": 2,
            "lank": "pub-jwbvod24_19_VIDEO",
            "group": {
              "rank": 4,
              "key": "videos"
            }
          }
        },
        {
          "type": "item",
          "subtype": "video",
          "links": {
            "jw.org": "https://www.jw.org/open?docid=1011214&item=pub-jwb-092_14_VIDEO&wtlocale=E&appLanguage=E&prefer=content"
          },
          "lank": "pub-jwb-092_14_VIDEO",
          "title": "Kenneth Cook, Jr.: Avoid Deception, and Follow the Kingdom (Jer. 10:23)",
          "image": {
            "type": "lss",
            "url": "https://cms-imgp.jw-cdn.org/img/p/jwb-092/univ/art/jwb-092_univ_lss_14_lg.jpg"
          },
          "duration": "10:08",
          "insight": {
            "rank": 3,
            "lank": "pub-jwb-092_14_VIDEO",
            "group": {
              "rank": 4,
              "key": "videos"
            }
          }
        },
        {
          "type": "item",
          "subtype": "video",
          "links": {
            "jw.org": "https://www.jw.org/open?docid=1011214&item=pub-jwb-117_4_VIDEO&wtlocale=E&appLanguage=E&prefer=content"
          },
          "lank": "pub-jwb-117_4_VIDEO",
          "title": "Stay Spiritually Focused—Part 2",
          "image": {
            "type": "lss",
            "url": "https://cms-imgp.jw-cdn.org/img/p/jwb-117/univ/art/jwb-117_univ_lss_04_lg.jpg"
          },
          "duration": "5:14",
          "insight": {
            "rank": 4,
            "lank": "pub-jwb-117_4_VIDEO",
            "group": {
              "rank": 4,
              "key": "videos"
            }
          }
        },
        {
          "type": "item",
          "subtype": "video",
          "links": {
            "jw.org": "https://www.jw.org/open?docid=1011214&item=pub-jwbcov22_10_VIDEO&wtlocale=E&appLanguage=E&prefer=content"
          },
          "lank": "pub-jwbcov22_10_VIDEO",
          "title": "Do Not Be Misled by Imitation Peace!—Thea van Leeuwen",
          "image": {
            "type": "lss",
            "url": "https://cms-imgp.jw-cdn.org/img/p/jwbcov22/univ/art/jwbcov22_univ_lss_10_lg.jpg"
          },
          "duration": "3:11",
          "insight": {
            "rank": 5,
            "lank": "pub-jwbcov22_10_VIDEO",
            "group": {
              "rank": 4,
              "key": "videos"
            }
          }
        },
        {
          "type": "item",
          "subtype": "video",
          "links": {
            "jw.org": "https://www.jw.org/open?docid=1102019372&prefer=lang&wtlocale=E"
          },
          "lank": "pub-thv_11_VIDEO",
          "title": "Study 11—Enthusiasm",
          "image": {
            "type": "lss",
            "url": "https://cms-imgp.jw-cdn.org/img/p/1102019372/univ/art/1102019372_univ_lss_lg.jpg"
          },
          "duration": "5:04",
          "insight": {
            "rank": 6,
            "lank": "pub-thv_11_VIDEO",
            "group": {
              "rank": 4,
              "key": "videos"
            }
          }
        },
        {
          "type": "item",
          "subtype": "video",
          "links": {
            "jw.org": "https://www.jw.org/open?docid=1011214&item=pub-jwb-098_10_VIDEO&wtlocale=E&appLanguage=E&prefer=content"
          },
          "lank": "pub-jwb-098_10_VIDEO",
          "title": "Samuel F. Herd: Any Day Now",
          "image": {
            "type": "lss",
            "url": "https://cms-imgp.jw-cdn.org/img/p/jwb-098/univ/art/jwb-098_univ_lss_10_lg.jpg"
          },
          "duration": "14:59",
          "insight": {
            "rank": 7,
            "lank": "pub-jwb-098_10_VIDEO",
            "group": {
              "rank": 4,
              "key": "videos"
            }
          }
        },
        {
          "type": "item",
          "subtype": "video",
          "links": {
            "jw.org": "https://www.jw.org/open?docid=1011214&item=pub-co-r22_117_VIDEO&wtlocale=E&appLanguage=E&prefer=content"
          },
          "lank": "pub-co-r22_117_VIDEO",
          "title": "Anthony Morris: Do Not Be Misled by Imitation Peace!",
          "image": {
            "type": "lss",
            "url": "https://assetsnffrgf-a.akamaihd.net/assets/m/co-r22/univ/art/CO-r22_univ_lss_117_lg.jpg"
          },
          "duration": "30:53",
          "insight": {
            "rank": 8,
            "lank": "pub-co-r22_117_VIDEO",
            "group": {
              "rank": 4,
              "key": "videos"
            }
          }
        },
        {
          "type": "item",
          "subtype": "video",
          "links": {
            "jw.org": "https://www.jw.org/open?docid=1011214&item=pub-jwb_201901_3_VIDEO&wtlocale=E&appLanguage=E&prefer=content"
          },
          "lank": "pub-jwb_201901_3_VIDEO",
          "title": "Annual Meeting 2018—Talks and Announcements",
          "image": {
            "type": "lss",
            "url": "https://assetsnffrgf-a.akamaihd.net/assets/m/jwb/univ/201901/art/jwb_univ_201901_lss_03_lg.jpg"
          },
          "duration": "1:05:28",
          "insight": {
            "rank": 9,
            "lank": "pub-jwb_201901_3_VIDEO",
            "group": {
              "rank": 4,
              "key": "videos"
            }
          }
        }
      ]
    },
    {
      "type": "group",
      "label": "Publications",
      "links": [
        {
          "type": "more",
          "label": "See All",
          "link": "/results/E/publications?sort=rel&q=peace%20and%20security"
        }
      ],
      "layout": [
        "carousel",
        "publications"
      ],
      "results": [
        {
          "type": "item",
          "subtype": "publication",
          "links": {
            "jw.org": "https://www.jw.org/open?pub=tp73&prefer=lang&wtlocale=E",
            "wol": "https://wol.jw.org/wol/finder?wtlocale=E&pub=tp73&year=1973&q=peace+and+security&p=doc&srcid=sch&srctype=jwo"
          },
          "lank": "pub-tp73",
          "context": "BOOKS",
          "title": "True Peace and Security—From What Source?",
          "image": {
            "type": "cvr",
            "url": "https://cms-imgp.jw-cdn.org/img/p/tp73/univ/pt/tp73_univ_lg.jpg"
          },
          "insight": {
            "rank": 1,
            "lank": "pub-tp73",
            "group": {
              "rank": 6,
              "key": "publications"
            }
          }
        },
        {
          "type": "item",
          "subtype": "publication",
          "links": {
            "jw.org": "https://www.jw.org/open?pub=tp&prefer=lang&wtlocale=E",
            "wol": "https://wol.jw.org/wol/finder?wtlocale=E&pub=tp&year=1986&q=peace+and+security&p=doc&srcid=sch&srctype=jwo"
          },
          "lank": "pub-tp",
          "context": "BOOKS",
          "title": "True Peace and Security—How Can You Find It?",
          "image": {
            "type": "cvr",
            "url": "https://cms-imgp.jw-cdn.org/img/p/tp/univ/pt/tp_univ_lg.jpg"
          },
          "insight": {
            "rank": 2,
            "lank": "pub-tp",
            "group": {
              "rank": 6,
              "key": "publications"
            }
          }
        }
      ]
    }
  ],
  "messages": [],
  "insight": {
    "query": "peace and security",
    "filter": "all",
    "sort": "rel",
    "offset": 0,
    "page": 1,
    "total": {
      "value": 10000,
      "relation": "gte"
    }
  },
  "pagination": {
    "label": "Showing 1 - 36 of 10,000+",
    "links": [
      {
        "type": "first",
        "label": "1",
        "link": "/results/E/all?sort=rel&offset=0&limit=36&q=peace%20and%20security",
        "selected": true
      },
      {
        "type": "page",
        "label": "2",
        "link": "/results/E/all?sort=rel&offset=36&limit=36&q=peace%20and%20security"
      },
      {
        "type": "page",
        "label": "3",
        "link": "/results/E/all?sort=rel&offset=72&limit=36&q=peace%20and%20security"
      },
      {
        "type": "page",
        "label": "4",
        "link": "/results/E/all?sort=rel&offset=108&limit=36&q=peace%20and%20security"
      },
      {
        "type": "page",
        "label": "5",
        "link": "/results/E/all?sort=rel&offset=144&limit=36&q=peace%20and%20security"
      },
      {
        "type": "spacer"
      },
      {
        "type": "last",
        "label": "278",
        "link": "/results/E/all?sort=rel&offset=9972&limit=36&q=peace%20and%20security"
      },
      {
        "type": "next",
        "label": ">",
        "link": "/results/E/all?sort=rel&offset=36&limit=36&q=peace%20and%20security"
      }
    ]
  },
  "filters": [
    {
      "label": "All",
      "link": "/results/E/all?q=",
      "selected": true
    },
    {
      "label": "Publications",
      "link": "/results/E/publications?q="
    },
    {
      "label": "Videos",
      "link": "/results/E/videos?q="
    },
    {
      "label": "Music &amp; Dramas",
      "link": "/results/E/audio?q="
    },
    {
      "label": "Bible",
      "link": "/results/E/bible?q="
    }
  ],
  "sorts": [
    {
      "label": "Relevance",
      "link": "/results/E/all?sort=rel&q=",
      "selected": true
    },
    {
      "label": "Newest",
      "link": "/results/E/all?sort=newest&q="
    },
    {
      "label": "Oldest",
      "link": "/results/E/all?sort=oldest&q="
    }
  ]
}
```

To search for different content type you can use:

| Filter       | Description                                             | Note                                                           |
|--------------|---------------------------------------------------------|----------------------------------------------------------------|
| all          | all content                                             | Contains results in results array layout.                      |
| videos       | video content speaking having the subject in discussion | Does not contain second results array, only title & link       |
| publications | only publications having articles with the subject      | Does not contain second results array, only title & link       |
| audio        | audio containing the subject                            | Does not contain second results array, only title & link       |
| bible        | Any scripture containing the subject                    | Does not contain second results array, has title and snippet   |

An example json response other than `all` filter looks like:
#### Response example structure returned for `videos`, `publications`, `audio` and `bible` filters
```json
{
  "layout": [
    "flat"
  ],
  "results": [
    {
      "type": "item",
      "subtype": "verse",
      "links": {
        "jw.org": "https://www.jw.org/open?pub=nwtsty&bible=52005003&wtlocale=E&prefer=lang"
      },
      "lank": "bv-52005003_nwtsty",
      "title": "1 Thessalonians&nbsp;5:3",
      "snippet": "Whenever it is that they are saying, “<strong>Peace</strong> and <strong>security</strong>!” then sudden destruction is to be instantly on them, just like birth pains on a pregnant woman, and they will by no means escape.",
      "image": {
        "type": "sqs"
      },
      "insight": {
        "rank": 1,
        "lank": "bv-52005003_nwtsty"
      }
    },
    {
      "type": "item",
      "subtype": "verse",
      "links": {
        "jw.org": "https://www.jw.org/open?pub=nwtsty&bible=38014011&wtlocale=E&prefer=lang"
      },
      "lank": "bv-38014011_nwtsty",
      "title": "Zechariah&nbsp;14:11",
      "snippet": "And people will inhabit her; and there will never again be a curse of destruction, and Jerusalem will be inhabited in <strong>security</strong>.",
      "image": {
        "type": "sqs"
      },
      "insight": {
        "rank": 35,
        "lank": "bv-38014011_nwtsty"
      }
    }
  ],
  "messages": [],
  "insight": {
    "query": "peace and security",
    "filter": "bible",
    "sort": "rel",
    "offset": 0,
    "page": 1,
    "total": {
      "value": 383,
      "relation": "eq"
    }
  },
  "pagination": {
    "label": "Showing 1 - 36 of 383",
    "links": [
      {
        "type": "first",
        "label": "1",
        "link": "/results/E/bible?sort=rel&offset=0&limit=36&q=peace%20and%20security",
        "selected": true
      },
      {
        "type": "page",
        "label": "2",
        "link": "/results/E/bible?sort=rel&offset=36&limit=36&q=peace%20and%20security"
      },
      {
        "type": "page",
        "label": "3",
        "link": "/results/E/bible?sort=rel&offset=72&limit=36&q=peace%20and%20security"
      },
      {
        "type": "page",
        "label": "4",
        "link": "/results/E/bible?sort=rel&offset=108&limit=36&q=peace%20and%20security"
      },
      {
        "type": "page",
        "label": "5",
        "link": "/results/E/bible?sort=rel&offset=144&limit=36&q=peace%20and%20security"
      },
      {
        "type": "spacer"
      },
      {
        "type": "last",
        "label": "11",
        "link": "/results/E/bible?sort=rel&offset=360&limit=36&q=peace%20and%20security"
      },
      {
        "type": "next",
        "label": ">",
        "link": "/results/E/bible?sort=rel&offset=36&limit=36&q=peace%20and%20security"
      }
    ]
  },
  "filters": [
    {
      "label": "All",
      "link": "/results/E/all?q="
    },
    {
      "label": "Publications",
      "link": "/results/E/publications?q="
    },
    {
      "label": "Videos",
      "link": "/results/E/videos?q="
    },
    {
      "label": "Music &amp; Dramas",
      "link": "/results/E/audio?q="
    },
    {
      "label": "Bible",
      "link": "/results/E/bible?q=",
      "selected": true
    }
  ],
  "sorts": [
    {
      "label": "Relevance",
      "link": "/results/E/bible?sort=rel&q=",
      "selected": true
    },
    {
      "label": "Bible Book",
      "link": "/results/E/bible?sort=book&q="
    }
  ]
}
```

## Technical Goals
| Goal                     | Description                                                                                       |
|--------------------------|---------------------------------------------------------------------------------------------------|
| **Reliability**          | Must always resolve data from jw.org, with graceful fallbacks if a page or endpoint is missing.   |
| **Transparency**         | Responses should include a reference URL and timestamp to verify authenticity.                    |
| **Maintainability**      | Clean, modular codebase with unit tests, type hints, and consistent style (PEP8).                 |
| **Extensibility**        | Designed so that additional jw.org sections (e.g., publications, videos) can be integrated later. |
| **Privacy & Compliance** | No persistent logging of queries or personally identifiable information.                          |


## Requirements
List of requirements or libraries and technology stack.

| Library / Tool                            | Purpose                                                |
|-------------------------------------------|--------------------------------------------------------|
| **[uv](https://github.com/astral-sh/uv)** | Package management and virtual environment setup       |
| **requests**                              | Core HTTP client for retrieving jw.org content         |
| **brotli**                                | Enables Brotli compression for efficient data transfer |
| **fastmcp**                               | Framework for building Model Context Protocol tools    |
| **pytest**                                | Unit testing framework                                 |
| **ruff**                                  | Linting and code style enforcement                     |

## Development Guidelines

- Use PEP8 and type hints (mypy compliance).
- Write unit tests for all major functions (minimum 80% coverage).
- Ensure no JavaScript execution — raw HTML requests only.
- Use async I/O for network calls if scaling beyond simple use.
- Include a health check endpoint for MCP readiness validation.