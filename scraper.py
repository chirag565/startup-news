import feedparser
import json
import os
from datetime import datetime
from email.utils import parsedate_to_datetime

RSS_FEEDS = {
    "Entrackr": "https://entrackr.com/feed/",
    "Indian Startup News": "https://indianstartupnews.com/feed/rss2",
    "TICE News": "https://www.ticenews.com/feed",
    "Business Today": "https://www.businesstoday.in/rssfeeds/?id=225346",
    "People Matters": "https://www.peoplematters.in/rss",
    "NASSCOM": "https://nasscom.in/rss.xml",
    "Inc42": "https://inc42.com/feed/",
    "HackerRank Blog": "https://www.hackerrank.com/blog/feed/",
    "HR Economic Times": "https://hr.economictimes.indiatimes.com/rss/topstories",
    "HackerEarth Blog": "https://www.hackerearth.com/blog/feed/",
    "Mettl": "https://mettl.com/feed/"
}

NEWS_FILE = "news.json"
MAX_ARTICLES = 150

# Keyword matching for auto-categorization
CATEGORIES = {
    "Funding": ["fund", "raised", "million", "billion", "seed", "series a", "series b", "series c", "investment", "capital", "valuation"],
    "Layoffs": ["layoff", "fired", "job cut", "let go", "downsize", "restructur", "pink slip", "sack"],
    "Recruitment": ["hiring", "recruit", "talent", "jobs", "workforce", "appoint"],
    "Startup": ["startup", "founder", "unicorn", "co-founder", "incubat", "accelerat"],
    "IT Industry": ["software", "tech", "saas", "cybersecurity", "ai ", "artificial intelligence", "data center", "cloud"],
    "Business": ["revenue", "profit", "acquisition", "merger", "shares", "ipo", "market", "corporate", "economy", "nclt"]
}

def categorize_article(title, summary):
    """Scan title and summary to find the best matching category."""
    text = (title + " " + summary).lower()
    
    for cat_name, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in text:
                return cat_name
                
    return None # Returns None if irrelevant

def load_news():
    if os.path.exists(NEWS_FILE):
        try:
            with open(NEWS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("articles", [])
        except Exception:
            return []
    return []

def save_news(articles):
    data = {
        "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "articles": articles[:MAX_ARTICLES]
    }
    with open(NEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def parse_date(date_string):
    try:
        if not date_string:
            return datetime.now()
        return parsedate_to_datetime(date_string)
    except Exception:
        return datetime.now()

def fetch_latest_news():
    # Load existing so we don't fetch duplicates
    existing_articles = load_news()
    # We track seen_links so we don't process the same article twice
    seen_links = set()
    
    # Actually we should maintain a persistent list of seen links if we are dropping articles.
    # For now, we will read seen links from a file so we don't keep checking rejected articles.
    SEEN_FILE = "seen_links.json"
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            seen_links = set(json.load(f))
            
    new_articles = []
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Fetching news...")

    for site_name, feed_url in RSS_FEEDS.items():
        print(f"  -> Checking {site_name}...")
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                link = entry.get('link', '')
                if link and link not in seen_links:
                    seen_links.add(link) # Mark as seen whether we keep it or not
                    
                    title = entry.get('title', 'No Title')
                    summary = entry.get('summary', '')
                    category = categorize_article(title, summary)
                    
                    if category: # Only save if it matches our strict categories
                        published = entry.get('published', '')
                        date_obj = parse_date(published)
                        
                        new_articles.append({
                            "site": site_name,
                            "title": title,
                            "link": link,
                            "published": published,
                            "timestamp": date_obj.timestamp(),
                            "category": category
                        })
        except Exception as e:
            print(f"  -> [ERROR] Failed to fetch {site_name}: {e}")

    new_articles.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Save the seen links
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen_links), f)
        
    # Combine new and existing, keep max 150
    all_articles = new_articles + existing_articles
    all_articles.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    
    save_news(all_articles)
    
    if new_articles:
        print(f"\n=== Found {len(new_articles)} new RELEVANT articles! ===")
    else:
        print("\nNo new relevant articles found.")

def main():
    fetch_latest_news()

if __name__ == "__main__":
    main()
