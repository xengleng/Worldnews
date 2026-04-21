#!/usr/bin/env python3
"""
Daily stock news report for OpenClaw cron.
Uses only standard libraries to avoid dependency issues.
"""

import urllib.request
import xml.etree.ElementTree as ET
import json
import sys
from datetime import datetime
import time
import re

# Stock symbols and names
STOCKS = {
    "MRVL": "Marvell Technology",
    "AMD": "Advanced Micro Devices",
    "NVDA": "NVIDIA Corporation",
    "FIG": "Figma Inc",  # Figma Inc, not FIGS
    "XAUUSD": "Gold (USD per ounce)",
    "GLD": "SPDR Gold Shares ETF",
    "S63.SI": "ST Engineering (Singapore)",
    "Z74.SI": "SingTel (Singapore)",
    "USDSGD=X": "USD/SGD",
    "SGDJPY=X": "SGD/JPY",
    "SGDCNY=X": "SGD/CNY",
    "MYRSGD=X": "MYR/SGD"
}

def fetch_rss_feed(url):
    """Fetch and parse RSS feed."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (OpenClaw Stock Monitor)'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8')
            return content
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_rss(xml_content, source, symbol):
    """Parse RSS XML and extract articles."""
    articles = []
    if not xml_content:
        return articles
    
    try:
        # Clean XML namespaces
        xml_content = re.sub(r'xmlns="[^"]+"', '', xml_content)
        xml_content = re.sub(r'xmlns:[^=]+="[^"]+"', '', xml_content)
        
        root = ET.fromstring(xml_content)
        
        # Find all item elements
        for item in root.findall('.//item'):
            title_elem = item.find('title')
            link_elem = item.find('link')
            pubdate_elem = item.find('pubDate') or item.find('date')
            desc_elem = item.find('description')
            
            if title_elem is not None and link_elem is not None:
                title = title_elem.text or ''
                link = link_elem.text or ''
                pubdate = pubdate_elem.text if pubdate_elem is not None else ''
                description = desc_elem.text if desc_elem is not None else ''
                
                # Clean up description (remove HTML tags)
                description = re.sub(r'<[^>]+>', '', description)
                description = description[:200] + '...' if len(description) > 200 else description
                
                articles.append({
                    'source': source,
                    'symbol': symbol,
                    'title': title.strip(),
                    'link': link.strip(),
                    'published': pubdate.strip(),
                    'description': description.strip()
                })
                
                if len(articles) >= 5:  # Limit to 5 articles per source
                    break
    except Exception as e:
        print(f"Error parsing RSS: {e}")
    
    return articles

def check_impact(title, description):
    """Check if article has potential market impact."""
    text = (title + ' ' + description).lower()
    
    high_impact = ['earnings', 'results', 'quarter', 'guidance', 'forecast', 
                   'upgrade', 'downgrade', 'analyst', 'price target', 'target',
                   'merger', 'acquisition', 'buyout', 'lawsuit', 'sue', 'sued',
                   'investigation', 'sec', 'fda', 'approval', 'reject', 'recall',
                   'layoff', 'layoffs', 'cut', 'cuts', 'restructuring']
    
    medium_impact = ['partnership', 'deal', 'contract', 'win', 'won', 'award',
                    'launch', 'release', 'new', 'product', 'expansion', 'expand',
                    'hire', 'appoint', 'ceo', 'cfo', 'dividend', 'buyback',
                    'share', 'stock', 'conference', 'presentation']
    
    for word in high_impact:
        if word in text:
            return 'HIGH'
    
    for word in medium_impact:
        if word in text:
            return 'MEDIUM'
    
    return 'LOW'

def fetch_forex_rates():
    """Fetch current forex rates for SGD pairs."""
    try:
        url = "https://api.exchangerate-api.com/v4/latest/SGD"
        headers = {'User-Agent': 'Mozilla/5.0 (OpenClaw Stock Monitor)'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('rates', {})
    except Exception as e:
        print(f"Error fetching forex rates: {e}")
        return {}

def generate_report():
    """Generate the daily stock news report."""
    print(f"📈 **Daily Stock News Report** - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"**Monitoring:** {', '.join(STOCKS.keys())}")
    print()
    
    # Fetch forex rates first
    print("💱 **Fetching Forex Rates...**")
    forex_rates = fetch_forex_rates()
    
    if forex_rates:
        print(f"  Base currency: SGD (as of {datetime.now().strftime('%Y-%m-%d')})")
        
        # Calculate and display key rates
        usd_rate = 1 / forex_rates.get('USD', 0) if forex_rates.get('USD') else 0
        jpy_rate = forex_rates.get('JPY', 0)
        cny_rate = forex_rates.get('CNY', 0)
        myr_rate = forex_rates.get('MYR', 0)
        
        print(f"  USD/SGD: {usd_rate:.4f} (1 USD = {usd_rate:.4f} SGD)")
        print(f"  SGD/JPY: {jpy_rate:.2f} (1 SGD = {jpy_rate:.2f} JPY)")
        print(f"  SGD/CNY: {cny_rate:.4f} (1 SGD = {cny_rate:.4f} CNY)")
        print(f"  SGD/MYR: {myr_rate:.4f} (1 SGD = {myr_rate:.4f} MYR)")
        
        # Calculate inverse for MYR/SGD
        if myr_rate:
            myr_sgd_rate = 1 / myr_rate
            print(f"  MYR/SGD: {myr_sgd_rate:.4f} (1 MYR = {myr_sgd_rate:.4f} SGD)")
        print()
    else:
        print("  Could not fetch forex rates")
        print()
    
    all_articles = []
    
    for symbol, name in STOCKS.items():
        print(f"  Checking {symbol} ({name})...")
        
        # Yahoo Finance RSS
        yahoo_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
        yahoo_xml = fetch_rss_feed(yahoo_url)
        yahoo_articles = parse_rss(yahoo_xml, "Yahoo Finance", symbol)
        all_articles.extend(yahoo_articles)
        
        # Sleep to avoid rate limiting
        time.sleep(1)
    
    if not all_articles:
        print("\n✅ No news articles found today.")
        return
    
    # Analyze impact
    for article in all_articles:
        article['impact'] = check_impact(article['title'], article['description'])
    
    # Sort by impact (HIGH first)
    all_articles.sort(key=lambda x: {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}[x['impact']])
    
    # Group by impact
    high_impact = [a for a in all_articles if a['impact'] == 'HIGH']
    medium_impact = [a for a in all_articles if a['impact'] == 'MEDIUM']
    low_impact = [a for a in all_articles if a['impact'] == 'LOW']
    
    # Print report
    if high_impact:
        print("\n🔴 **HIGH IMPACT NEWS**")
        for article in high_impact:
            print(f"• **{article['symbol']}** ({article['source']}): {article['title']}")
            print(f"  {article['link']}")
            if article['description']:
                print(f"  {article['description']}")
            print()
    
    if medium_impact:
        print("🟡 **MEDIUM IMPACT NEWS**")
        for article in medium_impact:
            print(f"• **{article['symbol']}** ({article['source']}): {article['title']}")
            print(f"  {article['link']}")
            print()
    
    if low_impact:
        print(f"🟢 **Other news** ({len(low_impact)} articles)")
        print("  Run with --verbose to see all articles")
    
    print(f"\n📊 **Summary:** {len(high_impact)} high, {len(medium_impact)} medium, {len(low_impact)} low impact articles")
    
    # Save to file for reference
    with open(f"stock_news_{datetime.now().strftime('%Y%m%d')}.txt", 'w') as f:
        f.write(f"Stock News Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Stocks monitored: {', '.join(STOCKS.keys())}\n\n")
        
        # Write forex rates if available
        if forex_rates:
            f.write("Forex Rates (SGD base):\n")
            f.write(f"  USD/SGD: {1/forex_rates.get('USD', 0):.4f}\n" if forex_rates.get('USD') else "  USD/SGD: N/A\n")
            f.write(f"  SGD/JPY: {forex_rates.get('JPY', 0):.2f}\n")
            f.write(f"  SGD/CNY: {forex_rates.get('CNY', 0):.4f}\n")
            f.write(f"  SGD/MYR: {forex_rates.get('MYR', 0):.4f}\n\n")
        
        for article in all_articles:
            f.write(f"[{article['impact']}] {article['symbol']} - {article['title']}\n")
            f.write(f"Source: {article['source']}\n")
            f.write(f"Link: {article['link']}\n\n")

if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Daily Stock News Monitor")
        print("Usage: python3 daily_stock_report.py [--verbose]")
        print()
        print("Options:")
        print("  --verbose  Show all articles including low impact")
        print("  --json     Output in JSON format")
        sys.exit(0)
    
    generate_report()