import requests
from datetime import datetime, timedelta, UTC
API_KEY = "f7b0035f08c54269ba5a1dc67f3f8053"

# do a request for the top 10 popular news of the day
now = datetime.now(UTC)
yesterday = now - timedelta(days=1)

from_date = yesterday.isoformat(timespec="seconds")
to_date = now.isoformat(timespec="seconds")

url = (
    f"https://newsapi.org/v2/top-headlines?"
    f"language=en&pageSize=10&apiKey={API_KEY}"
)

response = requests.get(url).json()


for i, article in enumerate(response.get("articles", []), start=1):
    print(f"{i}. {article['title']} ({article['source']['name']})")
    print(article["url"])
    print("Snippet:", article.get("content"))

    print()

#do specific request based on the portfolio
