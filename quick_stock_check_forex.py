#!/usr/bin/env python3
"""
Quick stock news check for agent use with forex rates.
"""

import urllib.request
import xml.etree.ElementTree as ET
import json
import re
from datetime import datetime

STOCKS = {
    "MRVL": "Marvell",
    "AMD": "AMD",
    "NVDA": "NVIDIA",
    "FIG": "Figma",
    "XAUUSD": "Gold",
    "GLD": "SPDR Gold ETF",
    "S63.SI": "ST Engineering",
    "Z74.SI": "SingTel",
    "USDSGD=X": "USD/SGD",
    "SGDJPY=X": "SGD/JPY",
    "SGDCNY=X": "SGD/CNY",
    "MYRSGD=X": "MYR/SGD"
}

def fetch_forex_rates():
    """Fetch current forex rates for SGD pairs."""
    try:
        url = "https://api.exchangerate-api.com/v4/latest/SGD"
        headers = {'User-Agent': 'OpenClaw'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('rates', {})
    except:
        return {}

def get_news(symbol):
    """Get latest news for a symbol."""
    url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'OpenClaw'})
        with urllib.request.urlopen(req, timeout=5) as r:
            xml = r.read().decode('utf-8')
            xml = re.sub(r'xmlns="[^"]+"', '', xml)
            root = ET.fromstring(xml)
            
            articles = []
            for item in root.findall('.//item')[:3]:
                title = item.find('title')
                link = item.find('link')
                if title is not None and link is not None:
                    articles.append({
                        'title': title.text or '',
                        'link': link.text or ''
                    })
            return articles
    except:
        return []

def main():
    print(f"📊 Quick Stock & Forex Check - {datetime.now().strftime('%H:%M')}")
    print()
    
    # Show forex rates
    forex_rates = fetch_forex_rates()
    if forex_rates:
        print("💱 **Forex Rates (SGD base):**")
        usd_rate = 1 / forex_rates.get('USD', 0) if forex_rates.get('USD') else 0
        print(f"  USD/SGD: {usd_rate:.4f}")
        print(f"  SGD/JPY: {forex_rates.get('JPY', 0):.2f}")
        print(f"  SGD/CNY: {forex_rates.get('CNY', 0):.4f}")
        print(f"  SGD/MYR: {forex_rates.get('MYR', 0):.4f}")
        print()
    
    # Show stock news
    print("📰 **Stock News:**")
    for symbol in ["MRVL", "AMD", "NVDA", "FIG", "XAUUSD", "GLD", "S63.SI", "Z74.SI"]:
        articles = get_news(symbol)
        if articles:
            print(f"**{symbol}**:")
            for article in articles[:2]:
                title = article['title'][:80] + '...' if len(article['title']) > 80 else article['title']
                print(f"• {title}")
            print()
        else:
            print(f"**{symbol}**: No recent news")
            print()

if __name__ == "__main__":
    main()