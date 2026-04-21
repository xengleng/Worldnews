#!/usr/bin/env python3
"""
Public Memory Price Tracker
Uses publicly available sources since DRAMExchange requires login
"""

import json
import re
import time
from datetime import datetime
from pathlib import Path
import sys

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_LIBS = True
except ImportError:
    HAS_LIBS = False

DATA_DIR = Path(__file__).parent / "memory_prices"

# Public sources that don't require login
PUBLIC_SOURCES = [
    # E-commerce (actual retail prices)
    {
        "name": "Amazon Memory Best Sellers",
        "url": "https://www.amazon.com/Best-Sellers-Computers-Accessories-Memory/zgbs/pc/172500",
        "category": "retail_prices",
        "priority": "high"
    },
    {
        "name": "Newegg Memory",
        "url": "https://www.newegg.com/p/pl?N=100007952",
        "category": "retail_prices",
        "priority": "high"
    },
    
    # News and analysis
    {
        "name": "Tom's Hardware Memory",
        "url": "https://www.tomshardware.com/tag/memory",
        "category": "market_news",
        "priority": "medium"
    },
    {
        "name": "Google News Memory Search",
        "url": "https://news.google.com/search?q=memory+prices+dram+nand+2026",
        "category": "news_aggregator",
        "priority": "medium"
    },
    
    # Manufacturer news
    {
        "name": "Micron Investor News",
        "url": "https://investors.micron.com/news-releases",
        "category": "manufacturer",
        "priority": "medium"
    }
]

def scrape_public_source(source):
    """Scrape a public source for memory-related data."""
    name = source["name"]
    url = source["url"]
    category = source["category"]
    
    print(f"   • {name}: {url}")
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            return {
                "success": False,
                "name": name,
                "url": url,
                "category": category,
                "error": f"HTTP {response.status_code}",
                "scraped_at": datetime.now().isoformat()
            }
        
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()
        
        # Look for prices
        price_patterns = [
            r'\$(\d+\.?\d*)',
            r'USD\s*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*USD',
            r'price.*?\$(\d+\.?\d*)'
        ]
        
        prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    price = float(match)
                    # Filter for memory-like prices
                    if 10 < price < 1000:  # Reasonable memory price range
                        prices.append(price)
                except ValueError:
                    continue
        
        # Look for memory-related content
        memory_keywords = ['dram', 'nand', 'memory', 'ram', 'ddr', 'flash', 'ssd']
        memory_mentions = []
        
        for line in text.split('\n'):
            line = line.strip()
            if any(keyword in line.lower() for keyword in memory_keywords):
                if 20 < len(line) < 200:
                    memory_mentions.append(line[:150])
        
        # Get headlines/titles
        headlines = []
        for tag in soup.find_all(['h1', 'h2', 'h3', 'title']):
            headline = tag.get_text(strip=True)
            if headline and len(headline) > 10:
                headlines.append(headline[:150])
        
        return {
            "success": True,
            "name": name,
            "url": url,
            "category": category,
            "prices_found": len(prices),
            "unique_prices": sorted(list(set(prices)))[:10],
            "memory_mentions": memory_mentions[:5],
            "headlines": headlines[:3],
            "scraped_at": datetime.now().isoformat(),
            "response_size": len(response.content)
        }
        
    except Exception as e:
        return {
            "success": False,
            "name": name,
            "url": url,
            "category": category,
            "error": str(e),
            "scraped_at": datetime.now().isoformat()
        }

def generate_public_report(results):
    """Generate report from public sources."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    lines = []
    lines.append("💰 **PUBLIC MEMORY MARKET REPORT**")
    lines.append(f"Time: {timestamp} SGT")
    lines.append("")
    lines.append("## 📋 **DATA SOURCES**")
    lines.append("")
    lines.append("⚠️ **Note:** DRAMExchange requires login for professional price data")
    lines.append("Using publicly available sources as alternative indicators")
    lines.append("")
    
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    if successful:
        lines.append(f"✅ **Successfully scraped: {len(successful)}/{len(results)} sources**")
        lines.append("")
        
        # Retail prices
        retail_sources = [r for r in successful if r["category"] == "retail_prices"]
        if retail_sources:
            lines.append("### 🛒 **RETAIL MEMORY PRICES**")
            lines.append("")
            for result in retail_sources:
                lines.append(f"**{result['name']}**")
                lines.append(f"URL: {result['url']}")
                lines.append(f"Prices found: {result.get('prices_found', 0)}")
                
                if result.get('unique_prices'):
                    lines.append("Sample prices:")
                    for price in result['unique_prices'][:5]:
                        lines.append(f"• ${price:.2f}")
                
                lines.append("")
        
        # Market news
        news_sources = [r for r in successful if r["category"] in ["market_news", "news_aggregator"]]
        if news_sources:
            lines.append("### 📰 **MARKET NEWS & TRENDS**")
            lines.append("")
            for result in news_sources:
                lines.append(f"**{result['name']}**")
                lines.append(f"URL: {result['url']}")
                
                if result.get('memory_mentions'):
                    lines.append("Memory mentions:")
                    for mention in result['memory_mentions'][:3]:
                        lines.append(f"• {mention}")
                
                lines.append("")
        
        # Manufacturer news
        manufacturer_sources = [r for r in successful if r["category"] == "manufacturer"]
        if manufacturer_sources:
            lines.append("### 🏭 **MANUFACTURER UPDATES**")
            lines.append("")
            for result in manufacturer_sources:
                lines.append(f"**{result['name']}**")
                lines.append(f"URL: {result['url']}")
                
                if result.get('headlines'):
                    lines.append("Recent headlines:")
                    for headline in result['headlines']:
                        lines.append(f"• {headline}")
                
                lines.append("")
        
        # Price analysis
        all_prices = []
        for result in successful:
            all_prices.extend(result.get('unique_prices', []))
        
        if all_prices:
            lines.append("### 📊 **PRICE ANALYSIS**")
            lines.append("")
            
            unique_prices = sorted(list(set(all_prices)))
            avg_price = sum(all_prices) / len(all_prices) if all_prices else 0
            
            lines.append(f"**Summary from public sources:**")
            lines.append(f"• Total price points: {len(all_prices)}")
            lines.append(f"• Unique prices: {len(unique_prices)}")
            if unique_prices:
                lines.append(f"• Price range: ${min(unique_prices):.2f} - ${max(unique_prices):.2f}")
            lines.append(f"• Average: ${avg_price:.2f}")
            lines.append("")
            
            if unique_prices:
                lines.append("**Common price points:**")
                for price in unique_prices[:8]:
                    lines.append(f"• ${price:.2f}")
                lines.append("")
    else:
        lines.append("⚠️ **No sources successfully scraped**")
        lines.append("")
    
    if failed:
        lines.append("## ❌ **FAILED SOURCES**")
        lines.append("")
        for result in failed:
            lines.append(f"• {result['name']}: {result.get('error', 'Unknown error')}")
        lines.append("")
    
    lines.append("## 🔍 **DATA QUALITY NOTES**")
    lines.append("")
    lines.append("• **Public sources only** - No login required")
    lines.append("• **Retail prices** - Actual consumer memory product prices")
    lines.append("• **Market indicators** - News and trends, not spot prices")
    lines.append("• **Limitations:** Professional memory price data requires subscriptions")
    lines.append("• **Use case:** General market awareness, not professional trading")
    lines.append("")
    
    lines.append("## 🔗 **PUBLIC URLS USED**")
    lines.append("")
    for source in PUBLIC_SOURCES:
        lines.append(f"• {source['url']}")
    
    lines.append("")
    lines.append("---")
    lines.append("Generated: Public Memory Tracker v1.0")
    lines.append(f"Timestamp: {datetime.now().isoformat()}")
    
    return "\n".join(lines)

def save_to_obsidian(report_content):
    """Save report to Obsidian vault."""
    try:
        obsidian_dir = Path.home() / "Documents" / "openclaw" / "World News"
        obsidian_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"{datetime.now().strftime('%Y-%m-%d')}_Public_Memory_Market_Report_-_{timestamp}_SGT.md"
        filepath = obsidian_dir / filename
        
        filepath.write_text(report_content)
        print(f"📁 Report saved to Obsidian: {filepath}")
        
        return filepath
    except Exception as e:
        print(f"❌ Failed to save to Obsidian: {e}")
        return None

def main():
    """Main public memory tracker."""
    print("💰 Public Memory Price Tracker")
    print("=" * 60)
    print("Using publicly available sources (no login required)")
    print("Alternative to DRAMExchange which requires authentication")
    print("")
    
    if not HAS_LIBS:
        print("❌ Missing libraries. Install with:")
        print("   pip install --user --break-system-packages requests beautifulsoup4")
        sys.exit(1)
    
    DATA_DIR.mkdir(exist_ok=True)
    
    # Scrape public sources
    print("🌐 Scraping public memory sources...")
    results = []
    
    for source in PUBLIC_SOURCES:
        result = scrape_public_source(source)
        results.append(result)
        
        if result["success"]:
            print(f"     ✅ Found {result.get('prices_found', 0)} prices")
        else:
            print(f"     ❌ Failed: {result.get('error', 'Unknown')}")
        
        time.sleep(2)  # Be respectful
    
    # Generate report
    report = generate_public_report(results)
    
    # Print summary
    print("\n" + "=" * 60)
    successful = [r for r in results if r["success"]]
    print(f"📊 Summary: {len(successful)}/{len(results)} sources successful")
    
    total_prices = sum([len(r.get('unique_prices', [])) for r in successful])
    print(f"💰 Prices found: {total_prices}")
    print("=" * 60)
    
    # Save data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    data = {
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "metadata": {
            "total_sources": len(PUBLIC_SOURCES),
            "successful": len(successful),
            "total_prices": total_prices,
            "note": "Public sources only - no login required"
        }
    }
    
    data_file = DATA_DIR / f"public_memory_data_{timestamp}.json"
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    report_file = DATA_DIR / f"public_memory_report_{timestamp}.txt"
    report_file.write_text(report)
    
    print(f"\n📁 Data saved to: {data_file}")
    print(f"📄 Report saved to: {report_file}")
    
    # Save to Obsidian
    obsidian_file = save_to_obsidian(report)
    
    # Summary
    print("\n✅ **PUBLIC MEMORY TRACKER COMPLETE:**")
    print(f"   • Sources attempted: {len(results)}")
    print(f"   • Successful: {len(successful)}")
    print(f"   • Total prices found: {total_prices}")
    
    if obsidian_file:
        print(f"   • Obsidian report: {obsidian_file}")
    
    print("\n🔗 **PUBLIC SOURCES USED:**")
    for source in PUBLIC_SOURCES:
        print(f"   • {source['url']}")

if __name__ == "__main__":
    main()