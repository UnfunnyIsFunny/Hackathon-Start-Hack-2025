from datetime import datetime, timedelta, UTC
import json
from newsapi import NewsApiClient
import time
import os
dirname = os.path.dirname(__file__)
KEYWORDS_FILE = os.path.join(dirname, '../data_transfer/keywords.json')
CONTENT_FILE = os.path.join(dirname, '../data_transfer/content.json') 

newsapi = NewsApiClient(api_key="9d702e3dd4c845fb821fd11840eb3f6a")

def load_keywords():
    with open(KEYWORDS_FILE, "r") as f:
        return json.load(f)

#collect articles with keywords every hours
def fetch_specific():

    content = []
    while True:
        keywords = load_keywords()

        now = datetime.now(UTC)
        yesterday = now - timedelta(days=1)  # Fixed: days=1 not day=1

        from_date = yesterday.strftime("%Y-%m-%d")
        to_date = now.strftime("%Y-%m-%d")
        for keyword in keywords:
            top_headlines = newsapi.get_everything(q=keyword,
                                                    language='en',
                                                    page_size=5,
                                                    from_param=from_date,
                                                    to=to_date
                                                    )

            for source in top_headlines.get("articles", []):
                title = source["title"]
                link = source["url"]

                full_text = source.get("content") or ""
                date = source.get("publishedAt")
                content.append((title, full_text, link, date))

                print(source["title"])
                print(source["url"])
                print()
        with open(CONTENT_FILE, 'w') as f:
            json.dump(content, f)
        time.sleep(3600)

fetch_specific()
