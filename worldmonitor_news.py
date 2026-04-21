#!/usr/bin/env python3
"""
WorldMonitor-based news aggregator.
Fetches top news from selected RSS feeds every 6 hours.
"""

import feedparser
import json
from datetime import datetime, timedelta
import time
import sys
from pathlib import Path
import hashlib

# Selected feeds from WorldMonitor (focus on finance, tech, geopolitics)
FEEDS = [
    # Finance
    {"name": "CNBC", "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html", "category": "finance"},
    {"name": "Yahoo Finance", "url": "https://finance.yahoo.com/news/rssindex", "category": "finance"},
    {"name": "Reuters Business", "url": "https://www.reuters.com/business/", "category": "finance"},
    {"name": "MarketWatch", "url": "https://feeds.content.dowjones.io/public/rss/mw_realtimeheadlines", "category": "finance"},
    
    # Tech
    {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "category": "tech"},
    {"name": "Hacker News", "url": "https://hnrss.org/frontpage", "category": "tech"},
    {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "category": "tech"},
    
    # Geopolitics
    {"name": "BBC World", "url": "https://feeds.bbci.co.uk/news/world/rss.xml", "category": "geopolitics"},
    {"name": "Reuters World", "url": "https://www.reuters.com/world/", "category": "geopolitics"},
    {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml", "category": "geopolitics"},
    
    # Asia/Singapore focus
    {"name": "CNA", "url": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml", "category": "asia"},
    {"name": "Straits Times", "url": "https://www.straitstimes.com/news/rss.xml", "category": "asia"},
    {"name": "Nikkei Asia", "url": "https://asia.nikkei.com/rss/feed/nar", "category": "asia"},
]

# Cache to avoid duplicates
CACHE_FILE = Path(__file__).parent / "memory" / "news_cache.json"
CACHE_TTL_HOURS = 24

def load_cache():
    """Load seen article cache."""
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cache(cache):
    """Save cache with timestamp."""
    cache['_last_updated'] = datetime.now().isoformat()
    CACHE_FILE.parent.mkdir(exist_ok=True)
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

def is_seen(article_id, cache):
    """Check if article has been seen recently."""
    if article_id in cache:
        seen_time = datetime.fromisoformat(cache[article_id])
        if datetime.now() - seen_time < timedelta(hours=CACHE_TTL_HOURS):
            return True
    return False

def generate_article_id(title, link):
    """Generate unique ID for article."""
    return hashlib.md5(f"{title}|{link}".encode()).hexdigest()

def fetch_feed(feed):
    """Fetch and parse a single RSS feed."""
    try:
        parsed = feedparser.parse(feed['url'])
        articles = []
        
        for entry in parsed.entries[:5]:  # Top 5 per feed
            title = entry.get('title', 'No title')
            link = entry.get('link', '')
            published = entry.get('published', entry.get('updated', ''))
            summary = entry.get('summary', entry.get('description', ''))
            
            # Clean summary
            if summary:
                summary = summary[:200] + '...' if len(summary) > 200 else summary
            
            articles.append({
                'title': title,
                'link': link,
                'published': published,
                'summary': summary,
                'source': feed['name'],
                'category': feed['category']
            })
        
        return articles
    except Exception as e:
        print(f"Error fetching {feed['name']}: {e}", file=sys.stderr)
        return []

def fetch_all_news():
    """Fetch news from all feeds."""
    all_articles = []
    cache = load_cache()
    seen_ids = set()
    
    print(f"Fetching news from {len(FEEDS)} feeds...")
    
    for feed in FEEDS:
        articles = fetch_feed(feed)
        for article in articles:
            article_id = generate_article_id(article['title'], article['link'])
            
            if not is_seen(article_id, cache):
                article['id'] = article_id
                all_articles.append(article)
                seen_ids.add(article_id)
        
        time.sleep(0.5)  # Rate limiting
    
    # Update cache with new articles
    for article_id in seen_ids:
        cache[article_id] = datetime.now().isoformat()
    
    save_cache(cache)
    
    # Sort by recency (approximate)
    all_articles.sort(key=lambda x: x.get('published', ''), reverse=True)
    
    return all_articles[:15]  # Top 15 articles

def format_news_report(articles):
    """Format articles into a readable report with URLs at bottom."""
    if not articles:
        return "No new articles found in the last 24 hours."
    
    lines = []
    url_section = []
    lines.append("📰 **WORLDMONITOR NEWS UPDATE**")
    lines.append(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')} SGT")
    lines.append(f"Articles: {len(articles)} new items")
    lines.append("")
    
    # Group by category
    categories = {}
    for article in articles:
        cat = article['category']
        categories.setdefault(cat, []).append(article)
    
    article_counter = 1
    for category, cat_articles in categories.items():
        lines.append(f"**{category.upper()}**")
        for i, article in enumerate(cat_articles[:3], 1):  # Top 3 per category
            lines.append(f"{article_counter}. {article['title']}")
            lines.append(f"   Source: {article['source']}")
            if article.get('summary'):
                # Clean HTML tags from summary
                import re
                clean_summary = re.sub('<[^<]+?>', '', article['summary'])
                lines.append(f"   {clean_summary[:150]}..." if len(clean_summary) > 150 else f"   {clean_summary}")
            
            # Add to URL section
            url_section.append(f"{article_counter}. {article['title']}")
            url_section.append(f"   {article['link']}")
            url_section.append("")
            
            article_counter += 1
            lines.append("")
    
    # Add URL section
    lines.append("---")
    lines.append("🔗 **ALL ARTICLE LINKS:**")
    lines.append("")
    lines.extend(url_section)
    
    lines.append("---")
    lines.append("Updates every 6 hours (9 AM, 3 PM, 9 PM, 3 AM SGT)")
    lines.append("Based on WorldMonitor feed selection")
    
    return "\n".join(lines)

def main():
    """Main function."""
    articles = fetch_all_news()
    report = format_news_report(articles)
    
    print(report)
    
    # Save to file for logging
    report_file = Path(__file__).parent / f"news_update_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    report_file.write_text(report)
    
    print(f"\n📁 Report saved to: {report_file}")
    
    return articles

if __name__ == "__main__":
    main()