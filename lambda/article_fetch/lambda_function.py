import json
import logging
import os
import feedparser
import boto3

# --------------------------
# Logging Setup
# --------------------------
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# --------------------------
# Constants & S3 Setup
# --------------------------
FEED_CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'feeds', 'feed_sources.json'))
S3_BUCKET = os.environ.get('GOPHER_BUCKET')  # Set this in Lambda config
s3 = boto3.client('s3')


# --------------------------
# Load RSS Feed URLs
# --------------------------
def load_feed_sources():
    try:
        with open(FEED_CONFIG_PATH, 'r') as f:
            config = json.load(f)
            return config.get('quantum_feeds', [])
    except Exception as e:
        logger.error(f"Failed to load feed_sources.json: {e}")
        return []


# --------------------------
# Fetch and Parse Articles
# --------------------------
def fetch_articles(feed_url, max_items=5):
    try:
        feed = feedparser.parse(feed_url)
        articles = []
        for entry in feed.entries[:max_items]:
            articles.append({
                "title": entry.get("title", "No Title"),
                "link": entry.get("link", "No Link"),
                "published": entry.get("published", "No Date"),
                "summary": entry.get("summary", "No Summary")
            })
        return articles
    except Exception as e:
        logger.warning(f"Error parsing feed {feed_url}: {e}")
        return []


# --------------------------
# Format Articles for Gopher
# --------------------------
def format_articles(feed_name, articles):
    header = f"===== {feed_name} =====\n\n"
    body = ""
    for a in articles:
        body += (
            f"Title: {a['title']}\n"
            f"Date: {a['published']}\n"
            f"Link: {a['link']}\n"
            f"Summary: {a['summary']}\n"
            f"{'-'*40}\n"
        )
    return header + body


# --------------------------
# Save to S3
# --------------------------
def save_to_s3(filename, content):
    try:
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=filename,
            Body=content.encode('utf-8'),
            ContentType='text/plain'
        )
        logger.info(f"Uploaded {filename} to S3.")
    except Exception as e:
        logger.error(f"Failed to upload {filename}: {e}")


# --------------------------
# Lambda Entry Point
# --------------------------
def lambda_handler(event, context):
    feed_sources = load_feed_sources()
    if not feed_sources:
        logger.warning("No feeds found in feed_sources.json.")
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "No feed sources configured."})
        }

    for feed in feed_sources:
        logger.info(f"Fetching feed: {feed['name']}")
        articles = fetch_articles(feed['url'])
        if not articles:
            continue

        formatted_text = format_articles(feed['name'], articles)
        filename = f"{feed['name'].replace(' ', '_').lower()}.txt"
        save_to_s3(filename, formatted_text)

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Feeds processed and saved to S3."})
    }
