import os
# Must be after dirname is defined

import os
import asyncio
from openai import AsyncOpenAI
import time
import json
import requests
import ast
import sys
sys.path.append('....')
from ....models import Article

from asgiref.sync import sync_to_async
dirname = os.path.dirname(__file__)

RESULTS_FILE = os.path.join(dirname, '../data_transfer/relevant_articles.json')
CONTENT_FILE = os.path.join(dirname, '../data_transfer/content.json')
FILINGS_FILE = os.path.join(dirname, '../data_transfer/filings.json')

async def process_filing(client, filing_content, semaphore):
    prompt = f"""You are a financial analyst. Analyze the following SEC filing and respond in JSON with:
    1. "is_significant": true/false if the filing contains material information for investors.
    2. "summary": One-sentence summary of the most important info for investors.
    Filing:
    {filing_content}
    """
    role = "You are a financial analyst reviewing SEC filings for material events."
    async with semaphore:
        try:
            chat_completion = await client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": role}, {"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Filing error: {e}")
            return None

# --- Rate limiting config ---
TOKENS_PER_MINUTE = 6000
TOKENS_PER_REQUEST = 300  # Adjust this estimate as needed
CONCURRENT_REQUESTS = 1  # To ensure serial processing for rate limiting
max_requests_per_minute = TOKENS_PER_MINUTE // TOKENS_PER_REQUEST
delay_between_requests = 60 / max_requests_per_minute

    
# Define an async function to process a single article
async def process_article(client: AsyncOpenAI, article_content: str, portfolios: str, semaphore: asyncio.Semaphore):
    
    """Sends a single article to Groq and returns the summary."""
    prompt = f"""Your task is to determine if a news article is relevant for potential investments in
    {portfolios}. 
    Relevance includes not only financial performance but also significant operational events.
    Regular events like earnings reports or market trends should not be considered relevant unless they include unexpected information.
    Analyze the provided news article and respond in JSON format with two fields:
    1.  "is_relevant": ranges between "not relevant", "somewhat relevant", "relevant", "highly relevant".
    2.  "summary": A brief, objective summary of the article without any interpretations.
    :\n\n{article_content}
    """
    role = f"You are looking to invest in {portfolios}. You will be provided with news articles. Your task is to determine if the article is relevant for potential investments in these portfolios." 
    # The 'async with' statement waits for a slot to open in the semaphore.
    async with semaphore:
        try:
            print(f"Processing article...")
            chat_completion = await client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": role}, {"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.3
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"An error occurred: {e}")
            return None # Return None on failure

async def main(portfolio):
    """Main function to run the concurrent processing."""
    
    articles_to_process_json = json.load(open(CONTENT_FILE))
    articles_to_process = [f"Title: {title}\nContent: {content}" for title, content, url, date  in articles_to_process_json if content]
    urls = [f"URL: {url}" for title, content, url, date in articles_to_process_json if content]

    print(f"Starting processing for {len(articles_to_process)} articles...")
    start_time = time.time()

    # Create the asynchronous client
    client = AsyncOpenAI(api_key=os.getenv('GROQ_API_KEY'), base_url="https://api.groq.com/openai/v1")

    # Create the semaphore
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

    # --- Article processing (unchanged) ---
    results = []
    for i, article in enumerate(articles_to_process):
        if i > 0:
            await asyncio.sleep(delay_between_requests)
        result = await process_article(client, article, portfolio.assets, semaphore)
        results.append(result)

    end_time = time.time()

    # Filter out any failed results (which we set to None)
    successful_results = [res for res in results if res is not None]

    print("-" * 50)
    print(f"Successfully processed {len(successful_results)} out of {len(articles_to_process)} articles.")
    print(f"Total time taken: {end_time - start_time:.2f} seconds.")
    print("-" * 50)

    successful_results = [result[result.find('{'):result.rfind('}')+1].replace('```json', '').replace('```', '') for result in successful_results]

    with open(RESULTS_FILE, 'w') as f:
        json.dump(successful_results, f)
    for article, result in zip(articles_to_process_json, successful_results):
        title = article[0]
        content = ast.literal_eval(result)['summary']  
        url = article[2]
        date = article[3]
        verdict = ast.literal_eval(result)['is_relevant']  
        if verdict != "not relevant":
            # Prevent duplicate articles by name AND portfolio
            exists = await sync_to_async(Article.objects.filter(name=title, portfolio=str(portfolio)).exists)()
            if not exists:
                await sync_to_async(Article.objects.create)(
                    name=title,
                    content=content,
                    url=url,
                    portfolio=portfolio,
                    date=date,
                    verdict=verdict
                )

    # --- Filing processing ---
    if os.path.exists(FILINGS_FILE):
        with open(FILINGS_FILE) as f:
            filings = json.load(f)
        print(f"Starting processing for {len(filings)} filings...")
        for i, filing in enumerate(filings):
            if i > 0:
                await asyncio.sleep(delay_between_requests)
            filing_content = f"Company: {filing['companyName']}\nDate: {filing['date']}\nContent: {filing['content']}"
            result = await process_filing(client, filing_content, semaphore)
            # Parse LLM result
            try:
                llm_data = ast.literal_eval(result[result.find('{'):result.rfind('}')+1].replace('```json', '').replace('```', '')) if result else {}
            except Exception:
                llm_data = {}
            summary = llm_data.get('summary', '')
            verdict = str(llm_data.get('significance_score', ''))
            from ....models import Filing
            # Prevent duplicate filings by company and date
            date_val = None
            if 'date' in filing and filing['date']:
                try:
                    from django.utils.dateparse import parse_datetime
                    date_val = parse_datetime(filing['date'])
                except Exception:
                    pass
            exists = await sync_to_async(Filing.objects.filter(company=filing['companyName'], date=date_val).exists)() if date_val else False
            if not exists:
                filing_obj = Filing(
                    company=filing['companyName'],
                    content=summary,
                    url=filing['documentUrl'],
                    portfolio=str(portfolio),
                    verdict=verdict
                )
                if date_val:
                    filing_obj.date = date_val
                await sync_to_async(filing_obj.save)()
if __name__ == "__main__":
    import sys
    asyncio.run(main())
    successful_results = json.load(open(RESULTS_FILE))
    articles_to_process_json = json.load(open(CONTENT_FILE))
    for (article, result) in zip(articles_to_process_json, successful_results):
        title = article[0]
        verdict = ast.literal_eval(result)['is_relevant']
        print(f"Title: {title}\nVerdict: {verdict}\n{'-'*80}\n")
