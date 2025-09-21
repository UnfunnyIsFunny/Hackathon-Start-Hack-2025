from datetime import datetime, timedelta, UTC
import json
from newsapi import NewsApiClient
import time
import os
import sys
sys.path.append('....')
from ....models import Portfolio
import string
import requests
from sec_api import QueryApi,RenderApi
import trafilatura

dirname = os.path.dirname(__file__)
KEYWORDS_FILE = os.path.join(dirname, '../data_transfer/keywords.json')
CONTENT_FILE = os.path.join(dirname, '../data_transfer/content.json') 
FILINGS_FILE = os.path.join(dirname, '../data_transfer/filings.json')

newsapi = NewsApiClient(api_key="7518dca56f314bef898357616ee86dc2")

def load_keywords():
    keywords = []
    for p in Portfolio.objects.all():
        keywords.extend([w.strip(string.punctuation) for w in p.assets.split() if w.strip(string.punctuation).isalnum()])
    return keywords


def fetch_specific():

    content = []
    keywords = load_keywords()      
    now = datetime.now(UTC)
    yesterday = now - timedelta(days=1)

    from_date = yesterday.strftime("%Y-%m-%d")
    to_date = now.strftime("%Y-%m-%d")
    print(keywords)
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
    
def fetch_sec_filings():
    api = "bba9312593e9ddba5774fa1cef849567d28833bb07d900cd0a9d2ad5b37c4c91"
    queryApi = QueryApi(api_key=api)
    renderApi = RenderApi(api_key=api)
    query = {
    "query": "formType:\"8-K\" AND items:\"9.01\"",
    "from": "0",
    "size": "10",
    "sort": [{ "filedAt": { "order": "desc" } }]
    }

    filings = queryApi.get_filings(query)

    formatted_filings = []
    for filing in filings.get('filings', []):
        formatted_filings.append({
            'companyName': filing.get('companyName'),
            'date': filing.get('filedAt'),
            'documentUrl': filing.get('linkToHtml'),
            'content' : trafilatura.extract(renderApi.get_file(url=filing.get('linkToHtml')).encode('utf-8'), include_comments=False, include_tables=False)
        })

    with open(FILINGS_FILE, 'w') as f:
        json.dump(formatted_filings, f)



fetch_sec_filings()