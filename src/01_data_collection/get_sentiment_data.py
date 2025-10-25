import configparser
import os
import praw
from newsapi import NewsApiClient
import pandas as pd
from tqdm import tqdm # Import tqdm
import time # Import time for potential delays
import prawcore 
# Ensure the data/raw directory exists
os.makedirs("data/raw", exist_ok=True)

# --- Load API Keys ---
config = configparser.ConfigParser()
try:
    config.read('config/secrets.ini')
    if not config.sections():
         raise FileNotFoundError("secrets.ini not found or empty.")

    NEWS_API_KEY = config['DEFAULT']['NEWS_API_KEY']
    REDDIT_CLIENT_ID = config['REDDIT']['CLIENT_ID']
    REDDIT_CLIENT_SECRET = config['REDDIT']['CLIENT_SECRET']
    REDDIT_USER_AGENT = config['REDDIT']['USER_AGENT']
except (FileNotFoundError, KeyError) as e:
    print(f"Error reading configuration: {e}")
    print("Please ensure config/secrets.ini exists and contains the necessary keys.")
    exit() # Exit if keys are missing

def fetch_reddit_data():
    """Fetches posts from r/Bitcoin and r/CryptoCurrency."""
    print("Fetching Reddit data...")
    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT,
            read_only=True # Good practice if you're only reading
        )

        posts_list = []
        subreddits = ["Bitcoin", "CryptoCurrency"]
        limit_per_sub = 200 # Increase limit if needed, be mindful of API rates

        for sub_name in subreddits:
            print(f"Scraping r/{sub_name}...")
            subreddit = reddit.subreddit(sub_name)
            # Use tqdm for progress bar over posts
            for post in tqdm(subreddit.hot(limit=limit_per_sub), total=limit_per_sub, desc=f"r/{sub_name}"):
                posts_list.append({
                    "source": f"reddit_{sub_name}",
                    "id": post.id,
                    "title": post.title,
                    "text": post.selftext,
                    "score": post.score,
                    "url": post.url,
                    "created_utc": post.created_utc
                })
            time.sleep(1) # Small delay between subreddits

        df = pd.DataFrame(posts_list)
        df['created_datetime'] = pd.to_datetime(df['created_utc'], unit='s')
        df.to_csv("data/raw/reddit_posts.csv", index=False)
        print(f"Saved Reddit data: {len(df)} posts")

    except prawcore.exceptions.ResponseException as e: # Catch the specific 401 error
        print(f"PRAW Response Error: {e}. Check Reddit API credentials in secrets.ini.")
    except praw.exceptions.PRAWException as e: # Catch other PRAW errors
        print(f"PRAW Error: {e}.")

def fetch_news_data():
    """Fetches Bitcoin news from NewsAPI."""
    print("Fetching NewsAPI data...")
    try:
        newsapi = NewsApiClient(api_key=NEWS_API_KEY)

        # Get all articles about "bitcoin" or "crypto"
        # NewsAPI free tier limits history and total results. Fetch recent pages.
        page_size = 100 # Max for free tier
        print("Fetching news articles...")
        all_articles_data = newsapi.get_everything(
            q="bitcoin OR cryptocurrency",
            language='en',
            sort_by='publishedAt',
            page_size=page_size
        )

        articles_list = []
        # Use tqdm for processing articles
        if all_articles_data['status'] == 'ok':
            print(f"Total news results available: {all_articles_data['totalResults']}")
            for article in tqdm(all_articles_data['articles'], desc="Processing news"):
                articles_list.append({
                    "source": article['source']['name'],
                    "title": article['title'],
                    "description": article['description'],
                    "url": article['url'],
                    "published_at": article['publishedAt']
                })

            df = pd.DataFrame(articles_list)
            df.to_csv("data/raw/news_articles.csv", index=False)
            print(f"Saved NewsAPI data: {len(df)} articles")
        else:
             print(f"NewsAPI Error: {all_articles_data.get('message', 'Unknown error')}")

    except Exception as e:
        print(f"An unexpected error occurred with NewsAPI fetch: {e}")

if __name__ == "__main__":
    fetch_reddit_data()
    fetch_news_data()
