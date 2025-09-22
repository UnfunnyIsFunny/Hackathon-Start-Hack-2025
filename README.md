# Hackathon-Start-Hack-2025

This is the task we had to solve for the 2025 Start Hack Tour Hackathon in St.Gallen.
It involved creating a program with a web interface which fetches news articles, financial reports, etc.
It further determines their relevance for customer portfolios, nicely displaying relevant articles in web interface,
along with degree of relevance and a summary of the article.


## How to use
To run the application, first start the background service that fetches and processes data with 

´´´
  cd financeWebapp
  python manage.py run_fetch_server
  python manage.py run_server
´´´

Note that the API Keys within the application are all free.
