#!/usr/bin/env python3
"""
Bloomberg-style news categorizer and alert system.
Categorizes WorldMonitor news into Bloomberg-style categories with alert levels.
"""

import json
from datetime import datetime
from pathlib import Path
import re

# Bloomberg-style categories with alert levels
BLOOMBERG_CATEGORIES = {
    # Top-level Bloomberg categories
    "MARKETS": {
        "description": "Financial markets, stocks, bonds, currencies, commodities",
        "subcategories": ["EQUITIES", "FIXED INCOME", "FOREX", "COMMODITIES", "CRYPTO"],
        "alert_keywords": ["crash", "plunge", "surge", "rally", "record high", "record low", "bankruptcy", "IPO"],
        "alert_levels": {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
    },
    "ECONOMY": {
        "description": "Macroeconomic data, central banks, policy, indicators",
        "subcategories": ["CENTRAL BANKS", "ECONOMIC DATA", "FISCAL POLICY", "TRADE"],
        "alert_keywords": ["recession", "inflation", "rate cut", "rate hike", "GDP", "unemployment", "stimulus"],
        "alert_levels": {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
    },
    "TECH": {
        "description": "Technology, innovation, startups, cybersecurity",
        "subcategories": ["AI", "CYBERSECURITY", "SOFTWARE", "HARDWARE", "STARTUPS"],
        "alert_keywords": ["breach", "hack", "outage", "breakthrough", "acquisition", "lawsuit", "antitrust"],
        "alert_levels": {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
    },
    "POLITICS": {
        "description": "Government, elections, legislation, geopolitical events",
        "subcategories": ["US POLITICS", "GEOPOLITICS", "ELECTIONS", "LEGISLATION"],
        "alert_keywords": ["election", "protest", "sanctions", "war", "attack", "crisis", "summit"],
        "alert_levels": {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
    },
    "CORPORATE": {
        "description": "Company news, earnings, M&A, executive moves",
        "subcategories": ["EARNINGS", "M&A", "EXECUTIVE MOVES", "RESTRUCTURING"],
        "alert_keywords": ["earnings miss", "acquisition", "CEO resigns", "layoffs", "recall", "scandal"],
        "alert_levels": {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
    },
    "ENERGY": {
        "description": "Oil, gas, renewables, utilities, energy policy",
        "subcategories": ["OIL & GAS", "RENEWABLES", "UTILITIES", "ENERGY POLICY"],
        "alert_keywords": ["oil spike", "OPEC", "pipeline", "blackout", "sanctions", "embargo"],
        "alert_levels": {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
    }
}

# Alert level definitions
ALERT_LEVELS = {
    1: {"name": "LOW", "color": "🟢", "description": "Routine update, no immediate action needed"},
    2: {"name": "MEDIUM", "color": "🟡", "description": "Notable development, monitor closely"},
    3: {"name": "HIGH", "color": "🟠", "description": "Significant event, consider action"},
    4: {"name": "CRITICAL", "color": "🔴", "description": "Market-moving event, immediate attention required"}
}

def determine_alert_level(title, category):
    """Determine alert level based on title keywords and category."""
    title_lower = title.lower()
    
    # Critical keywords (market-moving events)
    critical_keywords = ["war", "attack", "killed", "dead", "crash", "bankruptcy", "recession", 
                        "default", "crisis", "emergency", "evacuation", "blackout", "outage"]
    
    # High impact keywords
    high_keywords = ["surge", "plunge", "record high", "record low", "sanctions", "embargo",
                    "protest", "strike", "layoffs", "recall", "breach", "hack"]
    
    # Medium impact keywords
    medium_keywords = ["earnings", "acquisition", "merger", "resigns", "appoints", "rate cut",
                      "rate hike", "inflation", "GDP", "data", "results", "forecast"]
    
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
    source_lower = source.lower()
    
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
        "primary_category": primary_category,
        "subcategory": subcategory,
        "alert_level": alert_level,
        "alert_info": ALERT_LEVELS[alert_level]
    }

def determine_subcategory(title_lower, primary_category):
    """Determine subcategory based on title and primary category."""
    if primary_category == "MARKETS":
        if "stock" in title_lower or "equity" in title_lower:
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
    
    # Group by alert level (critical first)
    alerts_by_level = {4: [], 3: [], 2: [], 1: []}
    categorized_articles = []
    
    for article in articles:
        categorization = categorize_article(
            article['title'], 
            article['source'], 
            article['category']
        )
        
        categorized = {
            **article,
            **categorization
        }
        categorized_articles.append(categorized)
        alerts_by_level[categorized['alert_level']].append(categorized)
    
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
                lines.append(f"     [{article['primary_category']} → {article['subcategory']}]")
            
            lines.append("")
    
    # Show categorized articles by Bloomberg category
    lines.append("📊 **CATEGORIZED NEWS**")
    lines.append("")
    
    # Group by Bloomberg category
    by_category = {}
    for article in categorized_articles:
        cat = article['primary_category']
        by_category.setdefault(cat, []).append(article)
    
    for category in sorted(by_category.keys()):
        cat_articles = by_category[category]
        cat_info = BLOOMBERG_CATEGORIES[category]
        
        lines.append(f"**{category}** ({len(cat_articles)})")
        lines.append(f"   {cat_info['description']}")
        
        # Group by subcategory
        by_subcat = {}
        for article in cat_articles:
            subcat = article['subcategory']
            by_subcat.setdefault(subcat, []).append(article)
        
        for subcat in sorted(by_subcat.keys()):
            subcat_articles = by_subcat[subcat]
            lines.append(f"   └─ {subcat} ({len(subcat_articles)})")
            
            for article in subcat_articles[:2]:  # Show top 2 per subcategory
                alert_info = ALERT_LEVELS[article['alert_level']]
                lines.append(f"      • {alert_info['color']} {article['title']}")
                lines.append(f"        Source: {article['source']}")
        
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
    
    return "\n".join(lines), categorized_articles

def parse_worldmonitor_output():
    """Parse the latest WorldMonitor news output."""
    # Find the latest news update file
    news_files = sorted(Path(".").glob("news_update_*.txt"))
    if not news_files:
        return []
    
    latest_file = news_files[-1]
    print(f"📁 Parsing: {latest_file.name}")
    
    with open(latest_file, 'r') as f:
        content = f.read()
    
    # Parse the file to extract articles
    articles = []
    lines = content.split('\n')
    
    current_category = None
    current_article = None
    
    for line in lines:
        line = line.strip()
        
        # Detect category headers
        if line.startswith('**') and line.endswith('**'):
            current_category = line.strip('*').lower()
            continue
        
        # Detect article titles (numbered items)
        if re.match(r'^\d+\.\s+', line):
            if current_article:
                articles.append(current_article)
            
            title = re.sub(r'^\d+\.\s+', '', line)
            current_article = {
                'title': title,
                'category': current_category,
                'source': '',
                'summary': '',
                'link': ''
            }
        
        # Detect source lines
        elif line.startswith('Source:'):
            if current_article:
                current_article['source'] = line.replace('Source:', '').strip()
        
        # Detect summary lines
        elif line and not line.startswith('Link:') and current_article and not current_article.get('summary'):
            # Check if this looks like a summary (not a title, not empty)
            if len(line) > 20 and not re.match(r'^\d+\.\s+', line):
                current_article['summary'] = line
    
    # Add the last article
    if current_article:
        articles.append(current_article)
    
    return articles

def main():
    """Main function."""
    print("📈 Bloomberg-style News Categorizer")
    print("=" * 50)
    
    # Parse latest WorldMonitor news
    articles = parse_worldmonitor_output()
    
    if not articles:
        print("❌ No articles found. Please run worldmonitor_news.py first.")
        return
    
    print(f"✅ Parsed {len(articles)} articles")
    
    # Categorize articles
    report, categorized = format_bloomberg_report(articles)
    
    # Print report
    print("\n" + report)
    
    # Save report
    report_file = Path(__file__).parent / f"bloomberg_categorized_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    report_file.write_text(report)
    
    # Save categorized data as JSON
    json_file = Path(__file__).parent / f"bloomberg_data_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
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
            }
        }, f, indent=2)
    
    print(f"\n📁 Report saved to: {report_file}")
    print(f"📊 Data saved to: {json_file}")
    
    return categorized

if __name__ == "__main__":
    main()