import requests
from datetime import datetime, timedelta, UTC
API_KEY = "f7b0035f08c54269ba5a1dc67f3f8053"
now = datetime.now(UTC)

# Rolling 24h window
yesterday = now - timedelta(days=1)

from_date = yesterday.isoformat(timespec="seconds")
to_date = now.isoformat(timespec="seconds")
# Build request
url = (
    f"https://newsapi.org/v2/everything?"
    f"q=*&from={from_date}&to={to_date}&"
    f"language=en&sortBy=popularity&pageSize=10&apiKey={API_KEY}"
)

response = requests.get(url).json()


for i, article in enumerate(response.get("articles", []), start=1):
    print(f"{i}. {article['title']} ({article['source']['name']})")
    print(article["url"])
    print()
