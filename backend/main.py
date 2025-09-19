import os
import asyncio
from openai import AsyncOpenAI
import time
import json
import requests



CONCURRENT_REQUESTS = 30


# Define an async function to process a single article
async def process_article(client: AsyncOpenAI, article_content: str, semaphore: asyncio.Semaphore):
    """Sends a single article to Groq and returns the summary."""
    prompt = f"Summarize the following news article in three bullet points:\n\n{article_content}"

    # The 'async with' statement waits for a slot to open in the semaphore.
    async with semaphore:
        try:
            print(f"Processing article...")
            chat_completion = await client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
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
    articles_to_process = [
        "ZURICH – The Swiss National Bank has hinted at new monetary policies...",
        "GENEVA – A breakthrough in quantum computing was announced by researchers...",
        "BERN – New regulations are set to impact the Swiss financial technology sector...",
        # ... imagine this list has 500 articles
    ] * 50 # Let's simulate 150 articles for this demo

    print(f"Starting processing for {len(articles_to_process)} articles...")
    start_time = time.time()

    # Create the asynchronous client
    client = AsyncOpenAI(api_key=os.getenv('GROQ_API_KEY'), base_url="https://api.groq.com/openai/v1")
    
    # Create the semaphore
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

    # Create a list of tasks to run concurrently
    tasks = [process_article(client, article, semaphore) for article in articles_to_process]
    
    # Run all tasks and wait for them to complete
    results = await asyncio.gather(*tasks)

    end_time = time.time()

    # Filter out any failed results (which we set to None)
    successful_results = [res for res in results if res is not None]
    
    print("-" * 50)
    print(f"Successfully processed {len(successful_results)} out of {len(articles_to_process)} articles.")
    print(f"Total time taken: {end_time - start_time:.2f} seconds.")
    print("-" * 50)
    with open('data.json', 'w') as f:
        json.dump(successful_results, f)

    # print("Example summary:", successful_results[0] if successful_results else "No results.")

if __name__ == "__main__":
    asyncio.run(main())
