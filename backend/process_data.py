import os
import asyncio
from openai import AsyncOpenAI
import time
import json
import requests
import ast



CONCURRENT_REQUESTS = 5
portfolios = "Equities: USA, Europe, Asia, Emerging Markets; Bonds: Global Government, Global Corporate bonds; Gold, FX: USD, EUR, CHF, JPY; Cryptocurrencies" 

    
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

async def main():
    """Main function to run the concurrent processing."""
    
    # In a real application, you would fetch these from a news API or database
    articles_to_process_json = json.load(open("content.json"))
    articles_to_process = [f"Title: {title}\nContent: {content}" for title, content, url in articles_to_process_json if content]
    urls = [f"URL: {url}" for title, content, url in articles_to_process_json if content]

    print(f"Starting processing for {len(articles_to_process)} articles...")
    start_time = time.time()

    # Create the asynchronous client
    client = AsyncOpenAI(api_key=os.getenv('GROQ_API_KEY'), base_url="https://api.groq.com/openai/v1")
    
    # Create the semaphore
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

    # Create a list of tasks to run concurrently
    tasks = [process_article(client, article, portfolios, semaphore) for article in articles_to_process]
    
    # Run all tasks and wait for them to complete
    results = await asyncio.gather(*tasks)

    end_time = time.time()

    # Filter out any failed results (which we set to None)
    successful_results = [res for res in results if res is not None]
    
    print("-" * 50)
    print(f"Successfully processed {len(successful_results)} out of {len(articles_to_process)} articles.")
    print(f"Total time taken: {end_time - start_time:.2f} seconds.")
    print("-" * 50)

    successful_results = [result[result.find('{'):result.rfind('}')+1].replace('```json', '').replace('```', '') for result in successful_results]
    
   
    with open('relevant_articles.json', 'w') as f:
        json.dump(successful_results, f)

    # print("Example summary:", successful_results[0] if successful_results else "No results.")
    
if __name__ == "__main__":
    import sys
    asyncio.run(main())
    successful_results = json.load(open('relevant_articles.json'))
    articles_to_process_json = json.load(open("content.json"))
    for (article, result) in zip(articles_to_process_json, successful_results):
        title = article[0]
        verdict = ast.literal_eval(result)['is_relevant']
        print(f"Title: {title}\nVerdict: {verdict}\n{'-'*80}\n")
