#!/usr/bin/env python3
"""
Daily stock news monitor for MRVL, AMD, NVIDIA, and FIG.
Run at 8 AM daily via OpenClaw cron.
"""

import json
import requests
import feedparser
from datetime import datetime
import time
import sys
from typing import List, Dict, Any
import os

# Configuration
STOCKS = {
    "MRVL": "Marvell Technology",
    "AMD": "Advanced Micro Devices", 
    "NVIDIA": "NVIDIA Corporation",
    "FIG": "FIG Partners"  # Could also be Fortress Investment Group
}

# News sources (free APIs and RSS feeds)
NEWS_SOURCES = {
    "yahoo_finance": "https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US",
    "google_news": "https://news.google.com/rss/search?q={query}+stock+OR+shares&hl=en-US&gl=US&ceid=US:en",
    "marketwatch": "https://feeds.content.dowjones.io/public/rss/mw_realtimeheadlines",
    "seeking_alpha": "https://seekingalpha.com/api/sa/combined/{symbol}.xml"
}

def fetch_yahoo_news(symbol: str, company_name: str) -> List[Dict[str, Any]]:
    """Fetch news from Yahoo Finance RSS feed."""
    articles = []
    try:
        url = NEWS_SOURCES["yahoo_finance"].format(symbol=symbol)
        feed = feedparser.parse(url)
        
        for entry in feed.entries[:5]:  # Get latest 5 articles
            articles.append({
                "source": "Yahoo Finance",
                "title": entry.title,
                "link": entry.link,
                "published": entry.get("published", ""),
                "summary": entry.get("summary", ""),
                "symbol": symbol,
                "company": company_name
            })
    except Exception as e:
        print(f"Error fetching Yahoo news for {symbol}: {e}")
    
    return articles

def fetch_google_news(query: str, symbol: str, company_name: str) -> List[Dict[str, Any]]:
    """Fetch news from Google News RSS feed."""
    articles = []
    try:
        url = NEWS_SOURCES["google_news"].format(query=f"{company_name}+{symbol}")
        feed = feedparser.parse(url)
        
        for entry in feed.entries[:5]:
            articles.append({
                "source": "Google News",
                "title": entry.title,
                "link": entry.link,
                "published": entry.get("published", ""),
                "summary": entry.get("summary", ""),
                "symbol": symbol,
                "company": company_name
            })
    except Exception as e:
        print(f"Error fetching Google news for {symbol}: {e}")
    
    return articles

def fetch_marketwatch_news() -> List[Dict[str, Any]]:
    """Fetch general market news from MarketWatch."""
    articles = []
    try:
        feed = feedparser.parse(NEWS_SOURCES["marketwatch"])
        
        for entry in feed.entries[:10]:
            title = entry.title.lower()
            # Check if article mentions any of our stocks
            for symbol, company in STOCKS.items():
                if symbol.lower() in title or company.lower() in title:
                    articles.append({
                        "source": "MarketWatch",
                        "title": entry.title,
                        "link": entry.link,
                        "published": entry.get("published", ""),
                        "summary": entry.get("summary", ""),
                        "symbol": symbol,
                        "company": company
                    })
                    break
    except Exception as e:
        print(f"Error fetching MarketWatch news: {e}")
    
    return articles

def analyze_news_impact(articles: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Categorize articles by potential impact level."""
    impact_keywords = {
        "high": ["earnings", "results", "quarterly", "guidance", "forecast", "upgrade", "downgrade", 
                "analyst", "price target", "merger", "acquisition", "lawsuit", "regulation", "fda", 
                "recall", "short", "investigation", "layoff", "restructuring"],
        "medium": ["partnership", "deal", "contract", "product launch", "new", "update", "expansion", 
                  "hire", "appointment", "conference", "presentation", "dividend", "buyback"],
        "low": ["interview", "opinion", "analysis", "trend", "market", "general", "overview"]
    }
    
    categorized = {"high": [], "medium": [], "low": []}
    
    for article in articles:
        title_lower = article["title"].lower()
        summary_lower = article.get("summary", "").lower()
        
        impact_level = "low"
        for level, keywords in impact_keywords.items():
            for keyword in keywords:
                if keyword in title_lower or keyword in summary_lower:
                    impact_level = level
                    break
            if impact_level != "low":
                break
        
        article["impact"] = impact_level
        categorized[impact_level].append(article)
    
    return categorized

def format_report(categorized_news: Dict[str, List[Dict[str, Any]]]) -> str:
    """Format the news report for display/notification."""
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    report = f"📈 **Daily Stock News Report** - {today}\n\n"
    report += f"**Monitoring:** {', '.join(STOCKS.keys())}\n\n"
    
    total_articles = sum(len(articles) for articles in categorized_news.values())
    
    if total_articles == 0:
        report += "✅ No significant news found for your stocks today.\n"
        return report
    
    # High impact news first
    if categorized_news["high"]:
        report += "🔴 **HIGH IMPACT NEWS**\n"
        for article in categorized_news["high"]:
            report += f"• **{article['symbol']}** ({article['source']}): {article['title']}\n"
            report += f"  {article['link']}\n\n"
    
    # Medium impact news
    if categorized_news["medium"]:
        report += "🟡 **MEDIUM IMPACT NEWS**\n"
        for article in categorized_news["medium"]:
            report += f"• **{article['symbol']}** ({article['source']}): {article['title']}\n"
            report += f"  {article['link']}\n\n"
    
    # Low impact/news count
    if categorized_news["low"]:
        report += f"🟢 **Other news** ({len(categorized_news['low'])} articles)\n"
        report += f"  Run with --verbose to see all articles\n"
    
    report += f"\n📊 **Summary:** {len(categorized_news['high'])} high, {len(categorized_news['medium'])} medium, {len(categorized_news['low'])} low impact articles"
    
    return report

def main():
    """Main function to fetch and analyze news."""
    print(f"Fetching news for {len(STOCKS)} stocks...")
    
    all_articles = []
    
    # Fetch news for each stock
    for symbol, company in STOCKS.items():
        print(f"  Checking {symbol} ({company})...")
        
        # Yahoo Finance
        yahoo_articles = fetch_yahoo_news(symbol, company)
        all_articles.extend(yahoo_articles)
        
        # Google News
        google_articles = fetch_google_news(f"{company} {symbol}", symbol, company)
        all_articles.extend(google_articles)
        
        time.sleep(1)  # Be nice to the servers
    
    # MarketWatch general news
    print("  Checking MarketWatch...")
    mw_articles = fetch_marketwatch_news()
    all_articles.extend(mw_articles)
    
    # Remove duplicates (by title)
    unique_articles = []
    seen_titles = set()
    for article in all_articles:
        title = article["title"].lower()
        if title not in seen_titles:
            seen_titles.add(title)
            unique_articles.append(article)
    
    print(f"Found {len(unique_articles)} unique articles")
    
    # Analyze impact
    categorized = analyze_news_impact(unique_articles)
    
    # Generate report
    report = format_report(categorized)
    
    # Output based on arguments
    if "--json" in sys.argv:
        output = {
            "timestamp": datetime.now().isoformat(),
            "stocks": STOCKS,
            "articles": unique_articles,
            "categorized": categorized,
            "summary": {
                "total": len(unique_articles),
                "high": len(categorized["high"]),
                "medium": len(categorized["medium"]),
                "low": len(categorized["low"])
            }
        }
        print(json.dumps(output, indent=2))
    elif "--verbose" in sys.argv:
        print("\n" + "="*80)
        print(report)
        print("="*80)
        
        # Show all articles in verbose mode
        if categorized["low"]:
            print("\n📰 **All Articles:**")
            for article in unique_articles:
                print(f"\n• [{article['impact'].upper()}] {article['symbol']} - {article['title']}")
                print(f"  Source: {article['source']}")
                print(f"  Link: {article['link']}")
    else:
        print(report)
    
    # Return exit code based on high impact news
    if len(categorized["high"]) > 0:
        return 1  # High impact news found
    return 0  # No high impact news

if __name__ == "__main__":
    sys.exit(main())