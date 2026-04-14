#!/usr/bin/env python3
"""
WorldMonitor with Bloomberg-style categorization AND Obsidian/GitHub integration.
Saves reports to Obsidian vault and pushes to GitHub repository.
"""

import feedparser
import json
from datetime import datetime, timedelta
import time
import sys
from pathlib import Path
import hashlib
import re
import subprocess
import os

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

# Bloomberg-style categories with alert levels
BLOOMBERG_CATEGORIES = {
    "MARKETS": {
        "description": "Financial markets, stocks, bonds, currencies, commodities",
        "subcategories": ["EQUITIES", "FIXED INCOME", "FOREX", "COMMODITIES", "CRYPTO"],
        "alert_keywords": ["crash", "plunge", "surge", "rally", "record high", "record low", "bankruptcy", "IPO"],
    },
    "ECONOMY": {
        "description": "Macroeconomic data, central banks, policy, indicators",
        "subcategories": ["CENTRAL BANKS", "ECONOMIC DATA", "FISCAL POLICY", "TRADE"],
        "alert_keywords": ["recession", "inflation", "rate cut", "rate hike", "GDP", "unemployment", "stimulus"],
    },
    "TECH": {
        "description": "Technology, innovation, startups, cybersecurity",
        "subcategories": ["AI", "CYBERSECURITY", "SOFTWARE", "HARDWARE", "STARTUPS"],
        "alert_keywords": ["breach", "hack", "outage", "breakthrough", "acquisition", "lawsuit", "antitrust"],
    },
    "POLITICS": {
        "description": "Government, elections, legislation, geopolitical events",
        "subcategories": ["US POLITICS", "GEOPOLITICS", "ELECTIONS", "LEGISLATION"],
        "alert_keywords": ["election", "protest", "sanctions", "war", "attack", "crisis", "summit"],
    },
    "CORPORATE": {
        "description": "Company news, earnings, M&A, executive moves",
        "subcategories": ["EARNINGS", "M&A", "EXECUTIVE MOVES", "RESTRUCTURING"],
        "alert_keywords": ["earnings miss", "acquisition", "CEO resigns", "layoffs", "recall", "scandal"],
    },
    "ENERGY": {
        "description": "Oil, gas, renewables, utilities, energy policy",
        "subcategories": ["OIL & GAS", "RENEWABLES", "UTILITIES", "ENERGY POLICY"],
        "alert_keywords": ["oil spike", "OPEC", "pipeline", "blackout", "sanctions", "embargo"],
    }
}

# Alert level definitions
ALERT_LEVELS = {
    1: {"name": "LOW", "color": "🟢", "description": "Routine update, no immediate action needed"},
    2: {"name": "MEDIUM", "color": "🟡", "description": "Notable development, monitor closely"},
    3: {"name": "HIGH", "color": "🟠", "description": "Significant event, consider action"},
    4: {"name": "CRITICAL", "color": "🔴", "description": "Market-moving event, immediate attention required"}
}

# Cache to avoid duplicates
CACHE_FILE = Path(__file__).parent / "memory" / "news_cache.json"
CACHE_TTL_HOURS = 24

# Integration paths
OBSIDIAN_INTEGRATION_SCRIPT = Path("/home/yeoel/.openclaw/workspace/save_bloomberg_report.sh")

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
                # Remove HTML tags
                summary = re.sub('<[^<]+?>', '', summary)
                summary = summary[:200] + '...' if len(summary) > 200 else summary
            
            articles.append({
                'title': title,
                'link': link,
                'published': published,
                'summary': summary,
                'source': feed['name'],
                'original_category': feed['category']
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
                # Suppress trivial individual incidents with no systemic significance
                if is_trivial(article['title']):
                    print(f"  [SUPPRESSED] {article['title'][:60]}...")
                    continue
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

# Trivial item patterns — individual/local incidents with no systemic significance
# These are completely removed from the report
TRIVIAL_PATTERNS = [
    # Individual workplace incidents
    (r"warehouse worker (?:died|death|dead| killed)", 1),
    (r"factory worker (?:died|death|dead| killed)", 1),
    (r"employee (?:died|death|dead| killed)", 1),
    (r"(?:worker|employee|staffer) (?:died|death|dead)", 1),
    # Individual crimes/incidents (no broader systemic pattern)
    (r"(?:man|woman|person|driver) (?:dies|died|killed|dead)", 1),
    (r"(?:single|one) (?:dead|killed|died)", 1),
    # Routine local incidents
    (r"(?:dies|died|killed) in (?:accident|incident|crash)", 1),
    # Sports/celebrity trivial deaths
    (r"(?:dies|dead|killed) after (?:short|brief|short) illness", 1),
]

def is_trivial(title):
    """Check if article is a trivial individual incident with no systemic significance."""
    title_lower = title.lower()
    for pattern, _ in TRIVIAL_PATTERNS:
        if re.search(pattern, title_lower):
            return True
    return False

def determine_alert_level(title, category):
    """Determine alert level based on title keywords and category."""
    title_lower = title.lower()
    
    # Trivial items always downgrade to LOW
    if is_trivial(title):
        return 1  # LOW
    
    # Critical keywords (market-moving events)
    critical_keywords = ["war", "attack", "killed", "dead", "crash", "bankruptcy", "recession", 
                        "default", "crisis", "emergency", "evacuation", "blackout", "outage",
                        "terror", "bombing", "shooting", "fire"]
    
    # High impact keywords
    high_keywords = ["surge", "plunge", "record high", "record low", "sanctions", "embargo",
                    "protest", "strike", "layoffs", "recall", "breach", "hack", "rescue",
                    "missing", "downed", "airstrike"]
    
    # Medium impact keywords
    medium_keywords = ["earnings", "acquisition", "merger", "resigns", "appoints", "rate cut",
                      "rate hike", "inflation", "GDP", "data", "results", "forecast", "retires"]
    
    # Check for critical alerts first
    for keyword in critical_keywords:
        if keyword in title_lower:
            return 4  # CRITICAL
    
    # Check for high alerts
    for keyword in high_keywords:
        if keyword in title_lower:
            return 3  # HIGH
    
    # Check for medium alerts
    for keyword in medium_keywords:
        if keyword in title_lower:
            return 2  # MEDIUM
    
    # Default to low alert
    return 1  # LOW

def categorize_article(title, source, original_category):
    """Categorize article into Bloomberg-style categories."""
    title_lower = title.lower()
    
    # Map original categories to Bloomberg categories
    category_map = {
        "finance": "MARKETS",
        "tech": "TECH",
        "geopolitics": "POLITICS",
        "asia": "POLITICS",  # Asia news often geopolitical
    }
    
    # Determine primary Bloomberg category
    primary_category = category_map.get(original_category.lower(), "CORPORATE")
    
    # Refine category based on content
    if "iran" in title_lower or "russia" in title_lower or "ukraine" in title_lower:
        primary_category = "POLITICS"
    elif "oil" in title_lower or "energy" in title_lower or "gas" in title_lower:
        primary_category = "ENERGY"
    elif "fed" in title_lower or "central bank" in title_lower or "interest rate" in title_lower:
        primary_category = "ECONOMY"
    elif "stock" in title_lower or "market" in title_lower or "invest" in title_lower:
        primary_category = "MARKETS"
    elif "ai" in title_lower or "software" in title_lower or "tech" in title_lower:
        primary_category = "TECH"
    
    # Determine subcategory
    subcategory = determine_subcategory(title_lower, primary_category)
    
    # Determine alert level
    alert_level = determine_alert_level(title, primary_category)
    
    return {
        "bloomberg_category": primary_category,
        "bloomberg_subcategory": subcategory,
        "alert_level": alert_level,
        "alert_info": ALERT_LEVELS[alert_level]
    }

def determine_subcategory(title_lower, primary_category):
    """Determine subcategory based on title and primary category."""
    if primary_category == "MARKETS":
        if "stock" in title_lower or "equity" in title_lower or "asml" in title_lower:
            return "EQUITIES"
        elif "bond" in title_lower or "yield" in title_lower:
            return "FIXED INCOME"
        elif "dollar" in title_lower or "yen" in title_lower or "euro" in title_lower:
            return "FOREX"
        elif "oil" in title_lower or "gold" in title_lower or "commodity" in title_lower:
            return "COMMODITIES"
        elif "crypto" in title_lower or "bitcoin" in title_lower:
            return "CRYPTO"
    
    elif primary_category == "ECONOMY":
        if "fed" in title_lower or "central bank" in title_lower:
            return "CENTRAL BANKS"
        elif "gdp" in title_lower or "inflation" in title_lower or "unemployment" in title_lower:
            return "ECONOMIC DATA"
        elif "stimulus" in title_lower or "budget" in title_lower:
            return "FISCAL POLICY"
        elif "trade" in title_lower or "tariff" in title_lower:
            return "TRADE"
    
    elif primary_category == "TECH":
        if "ai" in title_lower or "artificial intelligence" in title_lower:
            return "AI"
        elif "hack" in title_lower or "breach" in title_lower or "cyber" in title_lower:
            return "CYBERSECURITY"
        elif "software" in title_lower or "app" in title_lower:
            return "SOFTWARE"
        elif "chip" in title_lower or "hardware" in title_lower:
            return "HARDWARE"
        elif "startup" in title_lower or "funding" in title_lower:
            return "STARTUPS"
    
    elif primary_category == "POLITICS":
        if "trump" in title_lower or "biden" in title_lower or "us " in title_lower:
            return "US POLITICS"
        elif "iran" in title_lower or "russia" in title_lower or "china" in title_lower:
            return "GEOPOLITICS"
        elif "election" in title_lower or "vote" in title_lower:
            return "ELECTIONS"
        elif "bill" in title_lower or "law" in title_lower or "legislation" in title_lower:
            return "LEGISLATION"
    
    elif primary_category == "CORPORATE":
        if "earnings" in title_lower or "profit" in title_lower or "loss" in title_lower:
            return "EARNINGS"
        elif "acquisition" in title_lower or "merger" in title_lower or "buy" in title_lower:
            return "M&A"
        elif "ceo" in title_lower or "resign" in title_lower or "appoint" in title_lower:
            return "EXECUTIVE MOVES"
        elif "layoff" in title_lower or "restructure" in title_lower:
            return "RESTRUCTURING"
    
    elif primary_category == "ENERGY":
        if "oil" in title_lower or "gas" in title_lower:
            return "OIL & GAS"
        elif "solar" in title_lower or "wind" in title_lower or "renewable" in title_lower:
            return "RENEWABLES"
        elif "power" in title_lower or "utility" in title_lower:
            return "UTILITIES"
        elif "policy" in title_lower or "regulation" in title_lower:
            return "ENERGY POLICY"
    
    # Default subcategory
    return "GENERAL"

def format_bloomberg_report(articles):
    """Format articles into Bloomberg-style report with alerts."""
    if not articles:
        return "No articles to categorize."
    
    lines = []
    lines.append("📈 **BLOOMBERG-STYLE NEWS CATEGORIZATION**")
    lines.append(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')} SGT")
    lines.append(f"Articles Analyzed: {len(articles)}")
    lines.append("")
    
    # Categorize all articles
    categorized_articles = []
    for article in articles:
        categorization = categorize_article(
            article['title'], 
            article['source'], 
            article['original_category']
        )
        categorized_articles.append({**article, **categorization})
    
    # Group by alert level (critical first)
    alerts_by_level = {4: [], 3: [], 2: [], 1: []}
    for article in categorized_articles:
        alerts_by_level[article['alert_level']].append(article)
    
    # Show critical alerts first
    lines.append("🚨 **ALERT SUMMARY**")
    lines.append("")
    
    for level in [4, 3, 2, 1]:
        if alerts_by_level[level]:
            alert_info = ALERT_LEVELS[level]
            lines.append(f"{alert_info['color']} **{alert_info['name']} ALERTS** ({len(alerts_by_level[level])})")
            lines.append(f"   {alert_info['description']}")
            
            for article in alerts_by_level[level][:3]:  # Show top 3 per level
                lines.append(f"   • {article['title']}")
                lines.append(f"     [{article['bloomberg_category']} → {article['bloomberg_subcategory']}]")
                lines.append(f"     Source: {article['source']}")
                lines.append(f"     🔗 {article['link']}")  # Add link here
            
            lines.append("")
    
    # Show categorized articles by Bloomberg category
    lines.append("📊 **CATEGORIZED NEWS**")
    lines.append("")
    
    # Group by Bloomberg category
    by_category = {}
    for article in categorized_articles:
        cat = article['bloomberg_category']
        by_category.setdefault(cat, []).append(article)
    
    for category in sorted(by_category.keys()):
        cat_articles = by_category[category]
        cat_info = BLOOMBERG_CATEGORIES[category]
        
        lines.append(f"**{category}** ({len(cat_articles)})")
        lines.append(f"   {cat_info['description']}")
        
        # Group by subcategory
        by_subcat = {}
        for article in cat_articles:
            subcat = article['bloomberg_subcategory']
            by_subcat.setdefault(subcat, []).append(article)
        
        for subcat in sorted(by_subcat.keys()):
            subcat_articles = by_subcat[subcat]
            lines.append(f"   └─ {subcat} ({len(subcat_articles)})")
            
            for article in subcat_articles[:2]:  # Show top 2 per subcategory
                alert_info = ALERT_LEVELS[article['alert_level']]
                lines.append(f"      • {alert_info['color']} {article['title']}")
                lines.append(f"        Source: {article['source']}")
                lines.append(f"        🔗 {article['link']}")  # Add link here
                if article.get('summary'):
                    lines.append(f"        {article['summary'][:100]}...")
        
        lines.append("")
    
    # Add summary statistics
    lines.append("📈 **SUMMARY STATISTICS**")
    lines.append("")
    
    total_alerts = sum(len(alerts) for alerts in alerts_by_level.values())
    lines.append(f"Total Articles: {total_alerts}")
    
    for level in [4, 3, 2, 1]:
        count = len(alerts_by_level[level])
        if count > 0:
            alert_info = ALERT_LEVELS[level]
            lines.append(f"{alert_info['color']} {alert_info['name']}: {count} ({count/total_alerts*100:.1f}%)")
    
    lines.append("")
    lines.append("---")
    lines.append("📰 **Source:** WorldMonitor News Aggregator")
    lines.append("🎯 **Categorization:** Bloomberg-style with alert levels")
    lines.append("⏰ **Next Update:** Every 6 hours (9 AM, 3 PM, 9 PM, 3 AM SGT)")
    
    # Add URL section
    lines.append("")
    lines.append("🔗 **ALL ARTICLE LINKS:**")
    lines.append("")
    
    for i, article in enumerate(categorized_articles, 1):
        alert_info = ALERT_LEVELS[article['alert_level']]
        lines.append(f"{i}. {alert_info['color']} {article['title']}")
        lines.append(f"   {article['link']}")
        lines.append("")
    
    return "\n".join(lines), categorized_articles

def save_to_obsidian_and_github(report_title, report_content, categorized_articles):
    """Save COMPLETE Bloomberg-style report to Obsidian vault and push to GitHub."""
    if not OBSIDIAN_INTEGRATION_SCRIPT.exists():
        print(f"⚠️  Obsidian/GitHub integration script not found: {OBSIDIAN_INTEGRATION_SCRIPT}")
        return False
    
    try:
        # Use the new script that saves the COMPLETE report as-is
        # Pass title and content as separate arguments (not JSON)
        cmd = ["bash", str(OBSIDIAN_INTEGRATION_SCRIPT), report_title, report_content]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Successfully saved COMPLETE report to Obsidian and pushed to GitHub")
            print(result.stdout)
            return True
        else:
            print(f"❌ Failed to save to Obsidian/GitHub:")
            print(f"   Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error during Obsidian/GitHub integration: {e}")
        return False

def main():
    """Main function."""
    print("📈 WorldMonitor with Bloomberg Categorization & Obsidian/GitHub Integration")
    print("=" * 70)
    
    # Fetch news
    articles = fetch_all_news()
    
    if not articles:
        print("❌ No new articles found.")
        return
    
    print(f"✅ Fetched {len(articles)} new articles")
    
    # Generate Bloomberg-style report
    report, categorized = format_bloomberg_report(articles)
    
    # Print report
    print("\n" + report)
    
    # Save local reports
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    
    # Save text report
    report_file = Path(__file__).parent / f"bloomberg_report_{timestamp}.txt"
    report_file.write_text(report)
    
    # Save JSON data
    json_file = Path(__file__).parent / f"bloomberg_data_{timestamp}.json"
    with open(json_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'articles_analyzed': len(articles),
            'categorized_articles': categorized,
            'alert_summary': {
                'critical': len([a for a in categorized if a['alert_level'] == 4]),
                'high': len([a for a in categorized if a['alert_level'] == 3]),
                'medium': len([a for a in categorized if a['alert_level'] == 2]),
                'low': len([a for a in categorized if a['alert_level'] == 1])
            },
            'category_summary': {
                cat: len([a for a in categorized if a['bloomberg_category'] == cat])
                for cat in BLOOMBERG_CATEGORIES.keys()
            }
        }, f, indent=2)
    
    print(f"\n📁 Local report saved to: {report_file}")
    print(f"📊 Local data saved to: {json_file}")
    
    # Save to Obsidian and push to GitHub
    report_title = f"World Monitor Brief - {datetime.now().strftime('%Y-%m-%d %H:%M')} SGT"
    print("\n💾 Saving to Obsidian and GitHub...")
    
    if save_to_obsidian_and_github(report_title, report, categorized):
        print("\n🎉 Integration complete! Report saved to:")
        print("   • Obsidian vault: ~/Documents/openclaw/World News/")
        print("   • GitHub repo: https://github.com/xengleng/Worldnews")
    else:
        print("\n⚠️  Obsidian/GitHub integration failed. Report saved locally only.")
    
    return categorized

if __name__ == "__main__":
    main()