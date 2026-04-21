#!/usr/bin/env python3
"""
DRAMExchange.com Web Scraper
Attempts to fetch real memory prices from DRAMExchange.com
Includes proper error handling and fallbacks.
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
    HAS_SCRAPING_LIBS = True
except ImportError:
    HAS_SCRAPING_LIBS = False
    print("⚠️  Missing scraping libraries. Install with:")
    print("    pip install requests beautifulsoup4")

# Configuration
DATA_DIR = Path(__file__).parent / "memory_prices"
PRICES_FILE = DATA_DIR / "scraped_prices.json"
CSV_FILE = DATA_DIR / "scraped_price_history.csv"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def setup_data_directory():
    """Create data directory."""
    DATA_DIR.mkdir(exist_ok=True)

def scrape_dramexchange():
    """
    Attempt to scrape DRAMExchange.com for memory prices.
    Returns: List of price dictionaries or empty list if failed.
    """
    if not HAS_SCRAPING_LIBS:
        print("❌ Cannot scrape: Missing required libraries")
        return []
    
    print("🌐 Attempting to scrape DRAMExchange.com...")
    print("⚠️  WARNING: Web scraping may be blocked or violate terms of service")
    print("    Use responsibly and respect robots.txt")
    
    # DRAMExchange URLs to try
    urls_to_try = [
        "https://www.dramexchange.com/",
        "https://www.dramexchange.com/dram-price-trend/",
        "https://www.dramexchange.com/nand-flash-price-trend/",
        "https://www.dramexchange.com/daily-price/",
    ]
    
    prices = []
    
    for url in urls_to_try:
        print(f"   Trying: {url}")
        
        try:
            # Make request with headers
            headers = {
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            print(f"   ✅ Successfully fetched page (Status: {response.status_code})")
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for price tables - these are common patterns on DRAMExchange
            # Note: Actual selectors need to be determined by inspecting the site
            
            # Try to find tables with price data
            tables = soup.find_all('table')
            print(f"   Found {len(tables)} tables on page")
            
            # Look for text that might indicate price data
            price_keywords = ['price', 'dram', 'nand', 'flash', 'usd', '$', 'dollar']
            price_elements = []
            
            for element in soup.find_all(text=re.compile(r'price|dram|nand|flash|usd|\$', re.I)):
                if element.parent not in price_elements:
                    price_elements.append(element.parent)
            
            print(f"   Found {len(price_elements)} elements with price keywords")
            
            # If we found some price-related content, try to extract
            if price_elements:
                # This is where we'd parse actual price data
                # For now, we'll create sample data based on what we found
                print("   ⚠️  Found price-related content but need to implement specific parsing")
                print("   DRAMExchange likely uses JavaScript or requires authentication")
                
                # Check if there's a login requirement
                if any("login" in str(e).lower() or "sign in" in str(e).lower() for e in price_elements[:10]):
                    print("   ❌ Page appears to require login/authentication")
                    break
                
                # Check for JavaScript-rendered content
                if len(tables) == 0 and len(price_elements) < 5:
                    print("   ⚠️  Content may be JavaScript-rendered (requires Selenium)")
                    break
            
            # Be respectful - don't hammer the site
            time.sleep(2)
            
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {e}")
            continue
        except Exception as e:
            print(f"   ❌ Error parsing page: {e}")
            continue
    
    # If scraping failed, return empty list
    if not prices:
        print("❌ Could not extract price data from DRAMExchange")
        print("   Possible reasons:")
        print("   1. Site requires JavaScript (need Selenium)")
        print("   2. Requires authentication/login")
        print("   3. Anti-scraping measures in place")
        print("   4. Site structure changed")
    
    return prices

def get_fallback_sample_data():
    """
    Get sample data when scraping fails.
    Clearly labeled as sample/fallback.
    """
    print("📊 Using FALLBACK SAMPLE DATA")
    print("🔴 NOT REAL PRICES - Scraping failed or not implemented")
    
    # Sample data based on typical memory prices
    prices = [
        {
            "category": "dram_spot",
            "item": "DDR5 16Gb (2Gx8) 4800/5600",
            "session_avg": 37.000,
            "change_percent": 0.00,
            "data_source": "FALLBACK_SAMPLE",
            "scraping_status": "failed",
            "note": "Real scraping needed - site may require JS/auth"
        },
        {
            "category": "dram_spot", 
            "item": "DDR4 16Gb (2Gx8) 3200",
            "session_avg": 73.091,
            "change_percent": -0.31,
            "data_source": "FALLBACK_SAMPLE",
            "scraping_status": "failed",
            "note": "Real scraping needed - site may require JS/auth"
        },
        {
            "category": "flash_spot",
            "item": "SLC 2Gb 256MBx8",
            "session_avg": 2.989,
            "change_percent": 9.37,
            "data_source": "FALLBACK_SAMPLE",
            "scraping_status": "failed",
            "note": "Real scraping needed - site may require JS/auth"
        }
    ]
    
    timestamp = datetime.now().isoformat()
    for price in prices:
        price["timestamp"] = timestamp
        price["fetch_time"] = timestamp
        price["is_real_data"] = False
        price["scraping_attempted"] = True
        price["scraping_success"] = False
    
    return prices

def analyze_scraping_results(prices, scraping_success):
    """Analyze what we got from scraping."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    lines = []
    lines.append("🌐 **DRAMEXCHANGE SCRAPING REPORT**")
    lines.append(f"Time: {timestamp} SGT")
    lines.append("")
    
    if scraping_success and prices and prices[0].get("is_real_data", False):
        lines.append("✅ **SCRAPING STATUS:** SUCCESS")
        lines.append(f"   • Prices fetched: {len(prices)}")
        lines.append(f"   • Source: DRAMExchange.com")
        lines.append(f"   • Data freshness: Real-time")
    else:
        lines.append("❌ **SCRAPING STATUS:** FAILED")
        lines.append("   • Using fallback sample data")
        lines.append("   • Real prices not available")
        lines.append("")
        lines.append("🔍 **SCRAPING DIAGNOSTICS:**")
        lines.append("   1. DRAMExchange may require JavaScript")
        lines.append("   2. May need authentication/login")
        lines.append("   3. Anti-scraping measures detected")
        lines.append("   4. Site structure may have changed")
    
    lines.append("")
    lines.append("📊 **PRICE DATA:**")
    
    if prices:
        for price in prices[:5]:  # Show first 5
            change = price.get("change_percent", 0)
            emoji = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
            source = price.get("data_source", "unknown")
            
            lines.append(f"{emoji} {price['item']}: ${price.get('session_avg', 0):.3f} ({change:+.2f}%)")
            
            if not price.get("is_real_data", True):
                lines.append(f"   ⚠️ {source} - Not real scraped data")
            if price.get("note"):
                lines.append(f"   📝 {price['note']}")
    else:
        lines.append("No price data available")
    
    lines.append("")
    
    # Technical details
    lines.append("🔧 **TECHNICAL DETAILS:**")
    lines.append(f"   • Has scraping libraries: {HAS_SCRAPING_LIBS}")
    lines.append(f"   • User Agent: {USER_AGENT[:50]}...")
    lines.append(f"   • Data directory: {DATA_DIR}")
    
    lines.append("")
    
    # Next steps for better scraping
    lines.append("🎯 **NEXT STEPS FOR REAL SCRAPING:**")
    lines.append("1. **Inspect DRAMExchange site structure**")
    lines.append("   - Check if it's JavaScript-rendered")
    lines.append("   - Look for API endpoints")
    lines.append("   - Check robots.txt")
    
    lines.append("2. **Consider Selenium for JavaScript sites**")
    lines.append("   ```python")
    lines.append("   from selenium import webdriver")
    lines.append("   driver = webdriver.Chrome()")
    lines.append("   driver.get('https://www.dramexchange.com/')")
    lines.append("   # Wait for JavaScript to load")
    lines.append("   ```")
    
    lines.append("3. **Check for official API/data feeds**")
    lines.append("   - Contact DRAMExchange for API access")
    lines.append("   - Look for RSS/JSON feeds")
    lines.append("   - Check partner/data provider options")
    
    lines.append("")
    lines.append("⚠️ **LEGAL & ETHICAL NOTES:**")
    lines.append("• Respect robots.txt and terms of service")
    lines.append("• Don't overload servers with requests")
    lines.append("• Consider official API if available")
    lines.append("• Use for personal/research purposes only")
    
    return "\n".join(lines)

def save_scraped_data(prices, scraping_success):
    """Save scraped data with metadata."""
    timestamp = datetime.now().isoformat()
    
    data = {
        "timestamp": timestamp,
        "scraping_success": scraping_success,
        "prices": prices,
        "metadata": {
            "source": "DRAMExchange.com" if scraping_success and prices and prices[0].get("is_real_data", False) else "Fallback sample",
            "has_real_data": scraping_success and prices and prices[0].get("is_real_data", False),
            "user_agent": USER_AGENT,
            "scraping_libraries": HAS_SCRAPING_LIBS
        }
    }
    
    # Save to JSON
    data_file = DATA_DIR / f"scraped_data_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Append to CSV if we have real data
    if scraping_success and prices and prices[0].get("is_real_data", False):
        csv_exists = CSV_FILE.exists()
        with open(CSV_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            if not csv_exists:
                # Write header
                writer.writerow(["timestamp", "category", "item", "price", "change", "source"])
            
            for price in prices:
                writer.writerow([
                    timestamp,
                    price.get("category", ""),
                    price.get("item", ""),
                    price.get("session_avg", 0),
                    price.get("change_percent", 0),
                    "DRAMExchange"
                ])
    
    return data_file

def main():
    """Main scraping function."""
    print("🌐 DRAMExchange.com Web Scraper")
    print("=" * 60)
    print("Attempting to fetch REAL memory prices...")
    print("")
    
    # Setup
    setup_data_directory()
    
    # Check if we have scraping libraries
    if not HAS_SCRAPING_LIBS:
        print("❌ Missing required libraries. Install with:")
        print("   pip install requests beautifulsoup4")
        print("")
        print("Using fallback data for now...")
        prices = get_fallback_sample_data()
        scraping_success = False
    else:
        # Attempt to scrape
        prices = scrape_dramexchange()
        
        if prices and prices[0].get("is_real_data", False):
            scraping_success = True
            print(f"✅ Successfully scraped {len(prices)} price points")
        else:
            scraping_success = False
            print("❌ Scraping failed, using fallback data")
            prices = get_fallback_sample_data()
    
    # Generate report
    report = analyze_scraping_results(prices, scraping_success)
    
    # Print report
    print("\n" + report)
    
    # Save data
    data_file = save_scraped_data(prices, scraping_success)
    
    print(f"\n📁 Data saved to: {data_file}")
    
    # Summary
    print("\n🎯 **SCRAPING SUMMARY:**")
    if scraping_success:
        print("✅ Framework working but needs specific parsing logic")
        print("✅ Successfully connected to DRAMExchange")
        print("⚠️  Need to implement actual price table parsing")
    else:
        print("❌ Could not extract real price data")
        print("⚠️  Likely reasons: JavaScript rendering, authentication, or anti-scraping")
        print("💡 Next: Try Selenium for JavaScript sites or look for API")
    
    return {
        "success": scraping_success,
        "prices_count": len(prices),
        "has_real_data": prices[0].get("is_real_data", False) if prices else False,
        "data_file": str(data_file)
    }

if __name__ == "__main__":
    main()