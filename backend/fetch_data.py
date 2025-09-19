import requests
from datetime import datetime, timedelta, UTC
import json
API_KEY = "f7b0035f08c54269ba5a1dc67f3f8053"

# do a request for the top 10 popular news of the day
now = datetime.now(UTC)
yesterday = now - timedelta(days=1)

from_date = yesterday.isoformat(timespec="seconds")
to_date = now.isoformat(timespec="seconds")

url = (
    f"https://newsapi.org/v2/top-headlines?"
    f"language=en&pageSize=15&apiKey={API_KEY}"
)

response = requests.get(url).json()


for i, article in enumerate(response.get("articles", []), start=1):
    print(f"{i}. {article['title']} ({article['source']['name']})")
    print(article["url"])

    print()

#put it in a list of tuples (title, content, URL)
content = []
for article in response.get("articles", []):
    title = article["title"]
    link = article["url"]

    
    full_text = article.get("content")

    content.append((title, full_text, link))

with open("content.json", 'w') as f:
    json.dump(content, f)


#do specific request based on the portfolio
