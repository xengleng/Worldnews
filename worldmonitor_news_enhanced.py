#!/usr/bin/env python3
"""
Enhanced WorldMonitor news aggregator using actual feed structure from the codebase.
Includes threat classification, source tiers, and Asia/Singapore focus.
"""

import feedparser
import json
import re
from datetime import datetime, timedelta
import time
import sys
from pathlib import Path
import hashlib
from typing import List, Dict, Any

# ==================== WORLD MONITOR FEED STRUCTURE ====================
# Based on server/worldmonitor/news/v1/_feeds.ts

WORLDMONITOR_FEEDS = {
    "finance": [
        {"name": "CNBC", "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html", "tier": 1},
        {"name": "Yahoo Finance", "url": "https://finance.yahoo.com/news/rssindex", "tier": 1},
        {"name": "Reuters Business", "url": "https://www.reuters.com/business/", "tier": 1},
        {"name": "MarketWatch", "url": "https://feeds.content.dowjones.io/public/rss/mw_realtimeheadlines", "tier": 1},
        {"name": "Financial Times", "url": "https://www.ft.com/rss/home", "tier": 1},
        {"name": "Federal Reserve", "url": "https://www.federalreserve.gov/feeds/press_all.xml", "tier": 1},
        {"name": "SEC News", "url": "https://www.sec.gov/news/pressreleases.rss", "tier": 1},
    ],
    "tech": [
        {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "tier": 1},
        {"name": "Hacker News", "url": "https://hnrss.org/frontpage", "tier": 1},
        {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "tier": 1},
        {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/technology-lab", "tier": 1},
        {"name": "AI News", "url": "https://news.google.com/rss/search?q=(OpenAI+OR+Anthropic+OR+Google+AI+OR+large+language+model+OR+ChatGPT)+when:2d&hl=en-US&gl=US&ceid=US:en", "tier": 2},
        {"name": "GitHub Blog", "url": "https://github.blog/feed/", "tier": 2},
    ],
    "geopolitics": [
        {"name": "BBC World", "url": "https://feeds.bbci.co.uk/news/world/rss.xml", "tier": 1},
        {"name": "Reuters World", "url": "https://www.reuters.com/world/", "tier": 1},
        {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml", "tier": 1},
        {"name": "Guardian World", "url": "https://www.theguardian.com/world/rss", "tier": 1},
        {"name": "AP News", "url": "https://news.google.com/rss/search?q=site:apnews.com&hl=en-US&gl=US&ceid=US:en", "tier": 1},
        {"name": "UN News", "url": "https://news.un.org/feed/subscribe/en/news/all/rss.xml", "tier": 1},
    ],
    "asia": [
        {"name": "CNA", "url": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml", "tier": 1},
        {"name": "Straits Times", "url": "https://www.straitstimes.com/news/rss.xml", "tier": 1},
        {"name": "Nikkei Asia", "url": "https://asia.nikkei.com/rss/feed/nar", "tier": 1},
        {"name": "The Diplomat", "url": "https://thediplomat.com/feed/", "tier": 2},
        {"name": "South China Morning Post", "url": "https://news.google.com/rss/search?q=site:scmp.com+when:2d&hl=en-US&gl=US&ceid=US:en", "tier": 1},
        {"name": "BBC Asia", "url": "https://feeds.bbci.co.uk/news/world/asia/rss.xml", "tier": 1},
    ],
    "singapore": [
        {"name": "CNA Singapore", "url": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=singapore", "tier": 1},
        {"name": "Straits Times Singapore", "url": "https://www.straitstimes.com/news/singapore/rss.xml", "tier": 1},
        {"name": "Today Online", "url": "https://www.todayonline.com/feed", "tier": 2},
        {"name": "Business Times", "url": "https://www.businesstimes.com.sg/feed", "tier": 2},
    ]
}

# Threat classification keywords (simplified from WorldMonitor)
THREAT_KEYWORDS = {
    "critical": ["war", "attack", "terror", "nuclear", "missile", "invasion", "coup", "assassination"],
    "high": ["crisis", "sanctions", "protest", "riot", "earthquake", "tsunami", "cyberattack", "hack"],
    "medium": ["tensions", "dispute", "negotiations", "summit", "election", "scandal", "investigation"],
    "low": ["meeting", "talks", "agreement", "deal", "visit", "speech", "report"],
}

# ==================== CACHE MANAGEMENT ====================
CACHE_FILE = Path(__file__).parent / "memory" / "news_cache_enhanced.json"
CACHE_TTL_HOURS = 24

def load_cache():
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cache(cache):
    cache['_last_updated'] = datetime.now().isoformat()
    CACHE_FILE.parent.mkdir(exist_ok=True)
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

def is_seen(article_id, cache):
    if article_id in cache:
        seen_time = datetime.fromisoformat(cache[article_id])
        if datetime.now() - seen_time < timedelta(hours=CACHE_TTL_HOURS):
            return True
    return False

def generate_article_id(title, link):
    return hashlib.md5(f"{title}|{link}".encode()).hexdigest()

# ==================== THREAT CLASSIFICATION ====================
def classify_threat_level(title, summary):
    """Simple threat classification based on keywords."""
    text = (title + " " + summary).lower()
    
    for level, keywords in THREAT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return level
    
    return "info"

def compute_importance_score(threat_level, source_tier, published_ago_hours):
    """Compute importance score (0-100) similar to WorldMonitor."""
    threat_scores = {"critical": 100, "high": 75, "medium": 50, "low": 25, "info": 0}
    tier_scores = {1: 100, 2: 75, 3: 50}
    
    threat_score = threat_scores.get(threat_level, 0)
    tier_score = tier_scores.get(source_tier, 50)
    
    # Recency bonus (more recent = higher score)
    recency_score = max(0, 100 - (published_ago_hours * 4))
    
    # Weighted average
    importance = (threat_score * 0.4) + (tier_score * 0.3) + (recency_score * 0.3)
    return min(100, max(0, int(importance)))

# ==================== FEED PROCESSING ====================
def fetch_feed(feed_config, category):
    """Fetch and parse a single RSS feed with threat classification."""
    try:
        parsed = feedparser.parse(feed_config['url'])
        articles = []
        
        for entry in parsed.entries[:5]:  # Top 5 per feed
            title = entry.get('title', 'No title').strip()
            link = entry.get('link', '')
            published = entry.get('published', entry.get('updated', ''))
            summary = entry.get('summary', entry.get('description', ''))
            
            if not title or not link:
                continue
            
            # Clean summary
            if summary:
                summary = re.sub(r'<[^>]+>', '', summary)
                summary = summary[:200] + '...' if len(summary) > 200 else summary
            
            # Parse publication time
            try:
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_time = datetime(*entry.published_parsed[:6])
                    published_ago = (datetime.now() - pub_time).total_seconds() / 3600
                else:
                    published_ago = 24  # Default to 24 hours if unknown
            except:
                published_ago = 24
            
            # Threat classification
            threat_level = classify_threat_level(title, summary)
            
            # Importance score
            importance = compute_importance_score(
                threat_level, 
                feed_config.get('tier', 3),
                published_ago
            )
            
            articles.append({
                'title': title,
                'link': link,
                'published': published,
                'summary': summary,
                'source': feed_config['name'],
                'category': category,
                'threat_level': threat_level,
                'importance': importance,
                'source_tier': feed_config.get('tier', 3),
                'published_ago_hours': published_ago,
            })
        
        return articles
    except Exception as e:
        print(f"Error fetching {feed_config['name']}: {e}", file=sys.stderr)
        return []

def fetch_all_news():
    """Fetch news from all WorldMonitor feeds."""
    all_articles = []
    cache = load_cache()
    seen_ids = set()
    
    print(f"Fetching news from WorldMonitor feeds...")
    
    for category, feeds in WORLDMONITOR_FEEDS.items():
        print(f"  Processing {category} ({len(feeds)} feeds)")
        
        for feed in feeds:
            articles = fetch_feed(feed, category)
            
            for article in articles:
                article_id = generate_article_id(article['title'], article['link'])
                
                if not is_seen(article_id, cache):
                    article['id'] = article_id
                    all_articles.append(article)
                    seen_ids.add(article_id)
            
            time.sleep(0.3)  # Rate limiting
    
    # Update cache
    for article_id in seen_ids:
        cache[article_id] = datetime.now().isoformat()
    
    save_cache(cache)
    
    # Sort by importance score (highest first)
    all_articles.sort(key=lambda x: x['importance'], reverse=True)
    
    return all_articles[:20]  # Top 20 articles

# ==================== REPORT FORMATTING ====================
def format_news_report(articles):
    """Format articles into an enhanced report."""
    if not articles:
        return "No new articles found in the last 24 hours."
    
    lines = []
    lines.append("📰 **WORLDMONITOR INTELLIGENCE UPDATE**")
    lines.append(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')} SGT")
    lines.append(f"Articles: {len(articles)} new items (threat-classified)")
    lines.append("")
    
    # Group by category
    categories = {}
    for article in articles:
        cat = article['category']
        categories.setdefault(cat, []).append(article)
    
    # Display order: critical threats first, then by category
    threat_order = ["critical", "high", "medium", "low", "info"]
    
    for category, cat_articles in categories.items():
        lines.append(f"## {category.upper()} NEWS")
        
        # Sort within category by threat level
        cat_articles.sort(key=lambda x: threat_order.index(x['threat_level']) 
                         if x['threat_level'] in threat_order else 5)
        
        for i, article in enumerate(cat_articles[:4], 1):  # Top 4 per category
            # Threat level emoji
            threat_emoji = {
                "critical": "🔴",
                "high": "🟠", 
                "medium": "🟡",
                "low": "🟢",
                "info": "🔵"
            }.get(article['threat_level'], "⚪")
            
            lines.append(f"{threat_emoji} **{article['title']}**")
            lines.append(f"   Source: {article['source']} (Tier {article['source_tier']})")
            lines.append(f"   Threat: {article['threat_level'].upper()} • Score: {article['importance']}/100")
            
            if article.get('summary'):
                lines.append(f"   {article['summary']}")
            
            lines.append(f"   Link: {article['link']}")
            lines.append("")
    
    # Summary statistics
    threat_counts = {}
    for article in articles:
        threat_counts[article['threat_level']] = threat_counts.get(article['threat_level'], 0) + 1
    
    lines.append("---")
    lines.append("**THREAT SUMMARY:**")
    for level in ["critical", "high", "medium", "low", "info"]:
        if level in threat_counts:
            lines.append(f"• {level.upper()}: {threat_counts[level]} articles")
    
    lines.append("")
    lines.append("**SCHEDULE:** Updates every 6 hours (9 AM, 3 PM, 9 PM, 3 AM SGT)")
    lines.append("**SOURCE:** WorldMonitor feed selection with threat classification")
    lines.append("**TIERS:** Tier 1 = Major news orgs, Tier 2 = Specialized sources")
    
    return "\n".join(lines)

# ==================== MAIN ====================
def main():
    """Main function."""
    print("Starting enhanced WorldMonitor news aggregation...")
    
    articles = fetch_all_news()
    report = format_news_report(articles)
    
    print("\n" + "="*60)
    print(report)
    print("="*60)
    
    # Save to file
    report_file = Path(__file__).parent / f"wm_intel_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    report_file.write_text(report)
    
    print(f"\n📁 Report saved to: {report_file}")
    
    # Also save JSON for programmatic use
    json_file = Path(__file__).parent / f"wm_intel_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(json_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'article_count': len(articles),
            'articles': articles
        }, f, indent=2)
    
    print(f"📊 JSON data saved to: {json_file}")
    
    return articles

if __name__ == "__main__":
    main()