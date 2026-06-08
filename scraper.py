import feedparser
import json
import os
import socket
from datetime import datetime
from email.utils import parsedate_to_datetime

# Prevent infinite hangs if a server is unresponsive
socket.setdefaulttimeout(15)

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
    "Mettl": "https://mettl.com/feed/",
    "YourStory": "https://yourstory.com/feed",
    "DQ India": "https://www.dqindia.com/rss",
    "Express Computer": "https://www.expresscomputer.in/feed/",
    "CIO India": "https://www.cio.com/in/feed/",
    "Layoffs.fyi": "https://layoffs.fyi/feed/",
    "Punekar News": "https://www.punekarnews.in/category/business/feed/",
    "iCreate": "https://icreate.org.in/feed/",
    "Face2News": "https://face2news.com/feed/",
    "OCAC": "https://ocac.in/en/rss.xml",
    "IT Mission Kerala": "https://itmission.kerala.gov.in/rss.xml",
    "Google News Bengaluru": "https://news.google.com/rss/search?q=Bengaluru+AND+(Startup+OR+Tech+OR+IT+OR+Business+OR+Funding)",
    "Google News Hyderabad": "https://news.google.com/rss/search?q=Hyderabad+AND+(Startup+OR+Tech+OR+IT+OR+Business+OR+Funding)",
    "Google News Pune": "https://news.google.com/rss/search?q=Pune+AND+(Startup+OR+Tech+OR+IT+OR+Business+OR+Funding)",
    "Google News Chennai": "https://news.google.com/rss/search?q=Chennai+AND+(Startup+OR+Tech+OR+IT+OR+Business+OR+Funding)",
    "Google News Mumbai": "https://news.google.com/rss/search?q=Mumbai+AND+(Startup+OR+Tech+OR+IT+OR+Business+OR+Funding)",
    "Google News Delhi": "https://news.google.com/rss/search?q=Delhi+AND+(Startup+OR+Tech+OR+IT+OR+Business+OR+Funding)",
    "Google News Ahmedabad": "https://news.google.com/rss/search?q=Ahmedabad+AND+(Startup+OR+Tech+OR+IT+OR+Business+OR+Funding)",
    "Google News Kolkata": "https://news.google.com/rss/search?q=Kolkata+AND+(Startup+OR+Tech+OR+IT+OR+Business+OR+Funding)",
    "Google News Gurugram": "https://news.google.com/rss/search?q=Gurugram+AND+(Startup+OR+Tech+OR+IT+OR+Business+OR+Funding)",
    "Google News Noida": "https://news.google.com/rss/search?q=Noida+AND+(Startup+OR+Tech+OR+IT+OR+Business+OR+Funding)",
    "Google News Chandigarh": "https://news.google.com/rss/search?q=Chandigarh+AND+(Startup+OR+Tech+OR+IT+OR+Business+OR+Funding)",
    "Google News Jaipur": "https://news.google.com/rss/search?q=Jaipur+AND+(Startup+OR+Tech+OR+IT+OR+Business+OR+Funding)",
    "Google News Visakhapatnam": "https://news.google.com/rss/search?q=Visakhapatnam+AND+(Startup+OR+Tech+OR+IT+OR+Business+OR+Funding)",
    "Google News Indore": "https://news.google.com/rss/search?q=Indore+AND+(Startup+OR+Tech+OR+IT+OR+Business+OR+Funding)",
    "Google News Coimbatore": "https://news.google.com/rss/search?q=Coimbatore+AND+(Startup+OR+Tech+OR+IT+OR+Business+OR+Funding)",
    "Google News Bhubaneswar": "https://news.google.com/rss/search?q=Bhubaneswar+AND+(Startup+OR+Tech+OR+IT+OR+Business+OR+Funding)",
    "Google News Lucknow": "https://news.google.com/rss/search?q=Lucknow+AND+(Startup+OR+Tech+OR+IT+OR+Business+OR+Funding)",
    "Google News Thiruvananthapuram": "https://news.google.com/rss/search?q=Thiruvananthapuram+AND+(Startup+OR+Tech+OR+IT+OR+Business+OR+Funding)",
    "Google News Kochi": "https://news.google.com/rss/search?q=Kochi+AND+(Startup+OR+Tech+OR+IT+OR+Business+OR+Funding)",
    "Google News Nashik": "https://news.google.com/rss/search?q=Nashik+AND+(Startup+OR+Tech+OR+IT+OR+Business+OR+Funding)"
}

NEWS_FILE = "news.json"
MAX_ARTICLES = 2000

# Keyword matching for auto-categorization

# City matching for auto-categorization
CITIES = {
    "Bengaluru": ["bengaluru", "bangalore"],
    "Hyderabad": ["hyderabad", "cyberabad"],
    "Pune": ["pune"],
    "Chennai": ["chennai"],
    "Mumbai": ["mumbai"],
    "Delhi NCR": ["delhi", "ncr", "new delhi"],
    "Ahmedabad": ["ahmedabad"],
    "Kolkata": ["kolkata", "calcutta"],
    "Gurugram": ["gurugram", "gurgaon"],
    "Noida": ["noida"],
    "Chandigarh": ["chandigarh"],
    "Jaipur": ["jaipur"],
    "Visakhapatnam": ["visakhapatnam", "vizag"],
    "Indore": ["indore"],
    "Coimbatore": ["coimbatore"],
    "Bhubaneswar": ["bhubaneswar"],
    "Lucknow": ["lucknow"],
    "Thiruvananthapuram": ["thiruvananthapuram", "trivandrum"],
    "Kochi": ["kochi", "cochin"],
    "Nashik": ["nashik", "nasik"]
}

CATEGORIES = {
    "Funding": ["fund", "raised", "million", "billion", "seed", "series a", "series b", "series c", "investment", "capital", "valuation"],
    "Layoffs": ["layoff", "fired", "job cut", "let go", "downsize", "restructur", "pink slip", "sack"],
    "Recruitment": ["hiring", "recruit", "talent", "jobs", "workforce", "appoint"],
    "Startup": ["startup", "founder", "unicorn", "co-founder", "incubat", "accelerat"],
    "IT Industry": ["software", "tech", "saas", "cybersecurity", "ai ", "artificial intelligence", "data center", "cloud"],
    "Business": ["revenue", "profit", "acquisition", "merger", "shares", "ipo", "market", "corporate", "economy", "nclt"]
}



def is_english(text):
    import re
    if re.search(r'[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]', text):
        return False
    return True

def categorize_city(title, summary):
    text = (title + " " + summary).lower()
    for city_name, keywords in CITIES.items():
        for kw in keywords:
            if kw in text:
                return city_name
    return "National"

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

from datetime import datetime, timedelta

def save_news(articles):
    ist_time = datetime.now() + timedelta(hours=5, minutes=30)
    data = {
        "last_updated": ist_time.strftime('%Y-%m-%d %H:%M:%S IST'),
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
                    
                    if not is_english(title + summary):
                        continue
                        
                    category = categorize_article(title, summary)
                    
                    # SAFETY BYPASS: Google News searches are already strictly filtered by Google's backend.
                    # If our python script misses a keyword, don't throw it away! Default to Business.
                    if not category and "Google News" in site_name:
                        category = "Business"
                        
                    if category: # Only save if it matches our strict categories
                        published = entry.get('published', '')
                        date_obj = parse_date(published)
                        
                        city = categorize_city(title, summary)
                        new_articles.append({
                            "site": site_name,
                            "title": title,
                            "link": link,
                            "published": published,
                            "timestamp": date_obj.timestamp(),
                            "category": category,
                            "city": city
                        })
        except Exception as e:
            print(f"  -> [ERROR] Failed to fetch {site_name}: {e}")

    new_articles.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Save the seen links
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen_links), f)
        
    # Re-filter existing articles just in case
    filtered_existing = [a for a in existing_articles if is_english(a.get('title', '') + a.get('summary', ''))]
    
    # Combine new and existing, keeping max limit
    all_articles = new_articles + filtered_existing
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
