import os
import asyncio
from openai import AsyncOpenAI
import time
import json
import requests



CONCURRENT_REQUESTS = 30
portfolios = "Equities: USA, Europe, Japan, Switzerland, UK, Emerging Markets; Bonds: Global Government, Global Corporate bonds; Gold, FX: USD, EUR, CHF, JPY"


# Define an async function to process a single article
async def process_article(client: AsyncOpenAI, article_content: str, portfolios: str, semaphore: asyncio.Semaphore):
    """Sends a single article to Groq and returns the summary."""
    prompt = f"""Your task is to determine if a news article is relevant for potential investments in
    {portfolios}. Analyze the provided news article and respond in JSON format with two fields:
    1.  "is_relevant": A boolean value (true or false).
    2.  "reason": A brief, one-sentence explanation for your decision.
    :\n\n{article_content}
    """
    role = f"You are a Financial Analyst which monitors financial markets for news that can impact client portfolios."
    # The 'async with' statement waits for a slot to open in the semaphore.
    async with semaphore:
        try:
            print(f"Processing article...")
            chat_completion = await client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": role}, {"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.5
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"An error occurred: {e}")
            return None # Return None on failure

async def main():
    """Main function to run the concurrent processing."""
    
    # In a real application, you would fetch these from a news API or database
    articles_to_process = json.load(open("backend/content.json"))

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
    with open('relevant_articles.json', 'w') as f:
        json.dump(successful_results, f)

    # print("Example summary:", successful_results[0] if successful_results else "No results.")

if __name__ == "__main__":
    asyncio.run(main())
