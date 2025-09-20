import requests
from datetime import datetime, timedelta, UTC
import json
from newsapi import NewsApiClient

newsapi = NewsApiClient(api_key="9d702e3dd4c845fb821fd11840eb3f6a")
#dates
now = datetime.now(UTC)
yesterday = now - timedelta(days=1)

from_date = yesterday.isoformat(timespec="seconds")
to_date = now.isoformat(timespec="seconds")


#collect articles with keywords
def fetch_specific(portfolio_keywords):
    content = []
    for keyword in portfolio_keywords:
        top_headlines = newsapi.get_everything(q=keyword,
                                               language='en')

        for source in top_headlines.get("articles", []):
            title = source["title"]
            link = source["url"]

            full_text = source.get("content") or ""
            content.append((title, full_text, link))

            print(source["title"])
            print(source["url"])
            print()
    with open("content.json", 'w') as f:
        json.dump(content, f)

portfolio_keywords = ["bitcoin", "china"]
fetch_specific(portfolio_keywords)
