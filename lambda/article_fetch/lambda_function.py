import json
import logging
import os
import feedparser

# --------------------------
# Logging setup
# --------------------------
# Configure the built-in logger to show INFO level and above
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# --------------------------
# Constants
# --------------------------
# Define the path to your RSS feed list (relative to this script)
FEED_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'feed_sources.json')


# --------------------------
# Load RSS Feed URLs from feed_sources.json
# --------------------------
def load_feed_sources():
    """
    Loads the list of feed URLs from feed_sources.json.
    Returns a list of feed metadata dictionaries.
    """
    try:
        with open(FEED_CONFIG_PATH, 'r') as f:
            config = json.load(f)
            return config.get('quantum_feeds', [])
    except Exception as e:
        logger.error(f"Failed to load feed_sources.json: {e}")
        return []  # Return an empty list if something goes wrong


# --------------------------
# Fetch articles from a given feed URL
# --------------------------
def fetch_articles(feed_url, max_items=5):
    """
    Parses a single RSS feed and extracts article metadata.
    
    Parameters:
        feed_url (str): The RSS feed URL.
        max_items (int): How many articles to fetch (default: 5).
    
    Returns:
        list: A list of dictionaries containing article info.
    """
    try:
        feed = feedparser.parse(feed_url)
        articles = []

        # Iterate through the feed's entries (limit to max_items)
        for entry in feed.entries[:max_items]:
            articles.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "summary": entry.get("summary", "")
            })

        return articles

    except Exception as e:
        logger.warning(f"Error fetching or parsing feed {feed_url}: {e}")
        return []  # Return empty list if an error occurs


# --------------------------
# Main Lambda Handler
# --------------------------
def lambda_handler(event, context):
    """
    AWS Lambda entry point. Loads feed sources, fetches articles from each,
    and returns a combined list as a JSON response.
    
    Parameters:
        event (dict): Input event data (ignored here).
        context (LambdaContext): Runtime information (also unused here).
    
    Returns:
        dict: HTTP-style response with a status code and JSON body.
    """
    # Step 1: Load feed sources from JSON config
    feed_sources = load_feed_sources()
    all_articles = []  # Will hold all collected articles

    # Step 2: Handle missing config or empty list
    if not feed_sources:
        logger.warning("No feeds found in feed_sources.json.")
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "No feed sources configured."})
        }

    # Step 3: Loop through all feeds and fetch articles
    for feed in feed_sources:
        logger.info(f"Fetching feed: {feed['name']}")

        articles = fetch_articles(feed['url'])

        # Add source name to each article so we know where it came from
        for arti
