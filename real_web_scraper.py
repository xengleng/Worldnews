#!/usr/bin/env python3
"""
REAL Web Scraper for Memory Prices
Actually scrapes websites - no hallucinations, no fake data.
"""

import json
import csv
from datetime import datetime
from pathlib import Path
import time
import sys
import re
from typing import Dict, List, Any, Optional

# Try to import scraping libraries
try:
    import requests
    from bs4 import BeautifulSoup
    HAS_BASIC_SCRAPING = True
except ImportError:
    HAS_BASIC_SCRAPING = False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False

# Configuration
DATA_DIR = Path(__file__).parent / "memory_prices"
SCRAPED_FILE = DATA_DIR / "real_scraped_data.json"

# Websites to scrape (all publicly accessible)
WEBSITES_TO_SCRAPE = [
    {
        "name": "DRAMExchange Home",
        "url": "https://www.dramexchange.com/",
        "method": "requests",
        "target": "Any price mentions, news, market updates"
    },
    {
        "name": "AnandTech Memory",
        "url": "https://www.anandtech.com/tag/memory",
        "method": "requests", 
        "target": "Memory market news, analysis, price mentions"
    },
    {
        "name": "TechSpot Memory",
        "url": "https://www.techspot.com/tag/memory/",
        "method": "requests",
        "target": "Memory news, price trends"
    },
    {
        "name": "Tom's Hardware Memory",
        "url": "https://www.tomshardware.com/tag/memory",
        "method": "requests",
        "target": "RAM prices, market analysis"
    }
]

def setup_data_directory():
    """Create data directory."""
    DATA_DIR.mkdir(exist_ok=True)

def scrape_with_requests(url, name):
    """Scrape a website using requests and BeautifulSoup."""
    print(f"🌐 Scraping {name}...")
    print(f"   URL: {url}")
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        print(f"   ✅ Status: {response.status_code}")
        print(f"   📏 Size: {len(response.content)} bytes")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove scripts and styles
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = '\n'.join(lines[:100])  # First 100 lines
        
        # Look for price-related content
        price_keywords = ['price', 'dram', 'nand', 'flash', 'usd', '$', 'dollar', 'memory', 'ram', 'ssd']
        price_lines = []
        
        for line in lines:
            if any(keyword in line.lower() for keyword in price_keywords):
                price_lines.append(line)
        
        return {
            "success": True,
            "url": url,
            "name": name,
            "content_preview": clean_text[:500] + "..." if len(clean_text) > 500 else clean_text,
            "price_mentions": price_lines[:10],  # First 10 price-related lines
            "price_mention_count": len(price_lines),
            "scraped_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {
            "success": False,
            "url": url,
            "name": name,
            "error": str(e),
            "scraped_at": datetime.now().isoformat()
        }

def scrape_with_selenium(url, name):
    """Scrape JavaScript-rendered websites using Selenium."""
    if not HAS_SELENIUM:
        return {
            "success": False,
            "url": url,
            "name": name,
            "error": "Selenium not installed",
            "scraped_at": datetime.now().isoformat()
        }
    
    print(f"🌐 Scraping with Selenium: {name}...")
    print(f"   URL: {url}")
    
    driver = None
    try:
        # Set up Chrome options
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in background
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Create driver
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Navigate to page
        driver.get(url)
        
        # Wait for page to load
        time.sleep(3)
        
        # Get page source
        page_source = driver.page_source
        print(f"   ✅ Page loaded")
        print(f"   📏 Size: {len(page_source)} bytes")
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Remove scripts and styles
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = '\n'.join(lines[:100])
        
        # Look for price-related content
        price_keywords = ['price', 'dram', 'nand', 'flash', 'usd', '$', 'dollar', 'memory', 'ram', 'ssd']
        price_lines = []
        
        for line in lines:
            if any(keyword in line.lower() for keyword in price_keywords):
                price_lines.append(line)
        
        return {
            "success": True,
            "url": url,
            "name": name,
            "method": "selenium",
            "content_preview": clean_text[:500] + "..." if len(clean_text) > 500 else clean_text,
            "price_mentions": price_lines[:10],
            "price_mention_count": len(price_lines),
            "scraped_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {
            "success": False,
            "url": url,
            "name": name,
            "error": str(e),
            "scraped_at": datetime.now().isoformat()
        }
    finally:
        if driver:
            driver.quit()

def scrape_alternative_sources():
    """Scrape alternative sources for memory price information."""
    print("\n🔍 Looking for memory price data in alternative sources...")
    
    # Try to find memory price mentions in tech news sites
    alternative_sources = [
        {
            "name": "Google News Search - Memory Prices",
            "url": "https://news.google.com/search?q=memory+prices+dram+nand",
            "method": "requests",
            "note": "News aggregator for memory price articles"
        },
        {
            "name": "Reddit r/hardware - Memory",
            "url": "https://www.reddit.com/r/hardware/search/?q=memory%20price&restrict_sr=1",
            "method": "requests",
            "note": "Community discussions about memory prices"
        },
        {
            "name": "TechPowerUp News",
            "url": "https://www.techpowerup.com/",
            "method": "requests",
            "note": "Tech news site with memory coverage"
        }
    ]
    
    results = []
    for source in alternative_sources:
        if source["method"] == "requests" and HAS_BASIC_SCRAPING:
            result = scrape_with_requests(source["url"], source["name"])
            result["note"] = source.get("note", "")
            results.append(result)
        time.sleep(1)  # Be polite
    
    return results

def extract_price_data_from_scrapes(scrape_results):
    """Extract actual price data from scrape results."""
    print("\n💰 Extracting price information from scraped content...")
    
    price_patterns = [
        r'\$(\d+\.?\d*)',  # $12.34
        r'USD\s*(\d+\.?\d*)',  # USD 12.34
        r'(\d+\.?\d*)\s*USD',  # 12.34 USD
        r'price.*?\$(\d+\.?\d*)',  # price $12.34
        r'DDR[45].*?\$(\d+\.?\d*)',  # DDR4 $12.34
        r'(\d+\.?\d*)\s*per\s*GB',  # 12.34 per GB
    ]
    
    extracted_prices = []
    
    for result in scrape_results:
        if not result.get("success"):
            continue
        
        content = result.get("content_preview", "") + " " + " ".join(result.get("price_mentions", []))
        
        for pattern in price_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                try:
                    price = float(match)
                    if 0.1 < price < 1000:  # Reasonable price range for memory
                        extracted_prices.append({
                            "price": price,
                            "currency": "USD",
                            "source": result["name"],
                            "url": result["url"],
                            "matched_pattern": pattern,
                            "scraped_at": result["scraped_at"]
                        })
                except ValueError:
                    continue
    
    # Deduplicate similar prices
    unique_prices = []
    seen_prices = set()
    
    for price_data in extracted_prices:
        price_key = f"{price_data['price']:.2f}-{price_data['source']}"
        if price_key not in seen_prices:
            seen_prices.add(price_key)
            unique_prices.append(price_data)
    
    print(f"   Found {len(unique_prices)} potential price points")
    return unique_prices

def generate_real_scraping_report(scrape_results, extracted_prices):
    """Generate report with actual scraped data."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    lines = []
    lines.append("🌐 **REAL WEB SCRAPING REPORT - MEMORY PRICES**")
    lines.append(f"Time: {timestamp} SGT")
    lines.append("")
    lines.append("## 🔍 **ACTUAL WEBSITES SCRAPED**")
    lines.append("")
    
    successful_scrapes = [r for r in scrape_results if r.get("success")]
    failed_scrapes = [r for r in scrape_results if not r.get("success")]
    
    lines.append(f"✅ **Successful:** {len(successful_scrapes)} websites")
    for result in successful_scrapes:
        lines.append(f"• {result['name']}")
        lines.append(f"  URL: {result['url']}")
        lines.append(f"  Price mentions: {result.get('price_mention_count', 0)}")
        if result.get("price_mentions"):
            lines.append(f"  Sample: {result['price_mentions'][0][:80]}...")
        lines.append("")
    
    if failed_scrapes:
        lines.append(f"❌ **Failed:** {len(failed_scrapes)} websites")
        for result in failed_scrapes[:3]:  # Show first 3 failures
            lines.append(f"• {result['name']}: {result.get('error', 'Unknown error')}")
        lines.append("")
    
    lines.append("## 💰 **PRICE DATA EXTRACTED**")
    lines.append("")
    
    if extracted_prices:
        lines.append(f"✅ Found {len(extracted_prices)} price references")
        lines.append("")
        
        # Group by source
        sources = {}
        for price in extracted_prices:
            source = price["source"]
            sources.setdefault(source, []).append(price)
        
        for source, prices in sources.items():
            lines.append(f"**{source}:**")
            for price in prices[:3]:  # Show first 3 from each source
                lines.append(f"• ${price['price']:.2f} USD (Pattern: {price['matched_pattern'][:20]}...)")
            lines.append("")
    else:
        lines.append("⚠️ No specific price data extracted")
        lines.append("")
        lines.append("**Why this might happen:**")
        lines.append("1. Price data often behind paywalls/login")
        lines.append("2. News sites discuss trends, not specific prices")
        lines.append("3. Need to scrape e-commerce sites for retail prices")
        lines.append("")
    
    lines.append("## 🎯 **NEXT STEPS FOR BETTER SCRAPING**")
    lines.append("")
    
    next_steps = [
        "1. **Scrape e-commerce sites** for retail memory prices:",
        "   • Amazon: RAM, SSD listings",
        "   • Newegg: Memory component prices",
        "   • PCPartPicker: Price tracking",
        "",
        "2. **Monitor tech deal sites**:",
        "   • Slickdeals: Memory/SSD deals",
        "   • TechBargains: Component prices",
        "",
        "3. **Use price tracking APIs**:",
        "   • Keepa API (Amazon price history)",
        "   • CamelCamelCamel (price tracking)",
        "",
        "4. **Community data sources**:",
        "   • Reddit r/buildapcsales",
        "   • Forum price tracking threads"
    ]
    
    for step in next_steps:
        lines.append(step)
    
    lines.append("")
    lines.append("## ⚠️ **SCRAPING REALITIES**")
    lines.append("")
    lines.append("• **Professional price data is paid** - DRAMExchange, TrendForce charge")
    lines.append("• **Retail prices ≠ spot prices** - Different markets")
    lines.append("• **Web scraping has limits** - Sites block, change structure")
    lines.append("• **Ethical considerations** - Respect robots.txt, rate limiting")
    
    lines.append("")
    lines.append("## 🔗 **ACTUALLY SCRAPED URLS**")
    lines.append("")
    for result in successful_scrapes:
        lines.append(f"• {result['url']}")
    
    lines.append("")
    lines.append("---")
    lines.append("Generated: Real Web Scraper v1.0")
    lines.append(f"Total websites attempted: {len(scrape_results)}")
    
    return "\n".join(lines)

def main():
    """Main scraping function."""
    print("🌐 REAL Web Scraper for Memory Prices")
    print("=" * 60)
    print("Actually scraping websites - no hallucinations")
    print("")
    
    # Check libraries
    if not HAS_BASIC_SCRAPING:
        print("❌ Missing requests/BeautifulSoup. Install with:")
        print("   pip install requests beautifulsoup4")
        return
    
    print(f"✅ Basic scraping libraries: {'Available' if HAS_BASIC_SCRAPING else 'Missing'}")
    print(f"✅ Selenium for JavaScript: {'Available' if HAS_SELENIUM else 'Missing'}")
    print("")
    
    # Setup
    setup_data_directory()
    
    # Scrape websites
    scrape_results = []
    
    for website in WEBSITES_TO_SCRAPE:
        if website["method"] == "requests":
            result = scrape_with_requests(website["url"], website["name"])
        elif website["method"] == "selenium" and HAS_SELENIUM:
            result = scrape_with_selenium(website["url"], website["name"])
        else:
            result = {
                "success": False,
                "url": website["url"],
                "name": website["name"],
                "error": f"Method {website['method']} not available",
                "scraped_at": datetime.now().isoformat()
            }
        
        scrape_results.append(result)
        time.sleep(2)  # Be polite between requests
    
    # Scrape alternative sources
    alternative_results = scrape_alternative_sources()
    scrape_results.extend(alternative_results)
    
    # Extract price data
    extracted_prices = extract_price_data_from_scrapes(scrape_results)
    
    # Generate report
    report = generate_real_scraping_report(scrape_results, extracted_prices)
    
    # Print report
    print("\n" + report)
    
    # Save data
    data = {
        "timestamp": datetime.now().isoformat(),
        "scrape_results": scrape_results,
        "extracted_prices": extracted_prices,
        "metadata": {
            "has_basic_scraping": HAS_BASIC_SCRAPING,
            "has_selenium": HAS_SELENIUM,
            "websites_attempted": len(scrape_results),
            "successful_scrapes": len([r for r in scrape_results if r.get("success")]),
            "price_points_found": len(extracted_prices)
        }
    }
    
    data_file = DATA_DIR / f"real_scraped_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    report_file = DATA_DIR / f"real_scraping_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    report_file.write_text(report)
    
    print(f"\n📁 Data saved to: {data_file}")
    print(f"📄 Report saved to: {report_file}")
    
    # Summary
    print("\n✅ **REAL SCRAPING SUMMARY:**")
    print(f"   • Websites attempted: {len(scrape_results)}")
    print(f"   • Successful scrapes: {len([r for r in scrape_results if r.get('success')])}")
    print(f"   • Price points found: {len(extracted_prices)}")
    print(f"   • Using Selenium: {HAS_SELENIUM}")
    
    print("\n🔗 **ACTUALLY VISITED URLS (No hallucinations):")
    for result in scrape_results:
        if result.get("success"):
            print(f"   • {result['url']}")
    
    return data

if __name__ == "__main__":
    main()