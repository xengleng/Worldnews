#!/usr/bin/env python3
"""
Simple Real Web Scraper
Actually scrapes websites right now - no waiting.
"""

import json
from datetime import datetime
from pathlib import Path
import time
import sys

# Try to import
try:
    import requests
    from bs4 import BeautifulSoup
    HAS_LIBS = True
except ImportError:
    HAS_LIBS = False

DATA_DIR = Path(__file__).parent / "memory_prices"

def scrape_site(url, name):
    """Simple site scraper."""
    print(f"🌐 {name}: {url}")
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get title
            title = soup.title.string if soup.title else "No title"
            
            # Look for memory/price related text
            text = soup.get_text()[:2000]  # First 2000 chars
            
            # Check for keywords
            keywords = ['dram', 'nand', 'memory', 'price', 'ram', 'ssd', 'usd', '$']
            found_keywords = []
            
            for kw in keywords:
                if kw in text.lower():
                    found_keywords.append(kw)
            
            return {
                "success": True,
                "url": url,
                "name": name,
                "title": title[:100],
                "found_keywords": found_keywords,
                "sample_text": text[:500],
                "status": response.status_code
            }
        else:
            return {
                "success": False,
                "url": url,
                "name": name,
                "error": f"HTTP {response.status_code}",
                "status": response.status_code
            }
            
    except Exception as e:
        return {
            "success": False,
            "url": url,
            "name": name,
            "error": str(e)
        }

def main():
    """Main function."""
    print("🌐 Simple Real Web Scraper")
    print("=" * 50)
    
    if not HAS_LIBS:
        print("❌ Missing libraries. Run:")
        print("   pip install --user --break-system-packages requests beautifulsoup4")
        return
    
    DATA_DIR.mkdir(exist_ok=True)
    
    # Sites to scrape
    sites = [
        ("DRAMExchange", "https://www.dramexchange.com/"),
        ("AnandTech Memory", "https://www.anandtech.com/tag/memory"),
        ("TechSpot", "https://www.techspot.com/tag/memory/"),
        ("Tom's Hardware", "https://www.tomshardware.com/tag/memory"),
        ("Google News Memory", "https://news.google.com/search?q=memory+price+dram")
    ]
    
    results = []
    
    for name, url in sites:
        result = scrape_site(url, name)
        results.append(result)
        
        if result["success"]:
            print(f"   ✅ Success: {len(result.get('found_keywords', []))} keywords found")
        else:
            print(f"   ❌ Failed: {result.get('error', 'Unknown')}")
        
        time.sleep(1)  # Be polite
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    data_file = DATA_DIR / f"simple_scrape_{timestamp}.json"
    
    with open(data_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "summary": {
                "total": len(results),
                "successful": len([r for r in results if r["success"]]),
                "failed": len([r for r in results if not r["success"]])
            }
        }, f, indent=2)
    
    # Generate report
    print("\n📊 **SCRAPING RESULTS:**")
    print("=" * 50)
    
    successful = [r for r in results if r["success"]]
    
    for result in successful:
        print(f"\n✅ {result['name']}:")
        print(f"   URL: {result['url']}")
        print(f"   Title: {result.get('title', 'N/A')}")
        print(f"   Keywords found: {', '.join(result.get('found_keywords', []))}")
        if result.get('sample_text'):
            print(f"   Sample: {result['sample_text'][:100]}...")
    
    print(f"\n📁 Data saved to: {data_file}")
    print(f"✅ Successful scrapes: {len(successful)}/{len(results)}")
    
    # Show actual working URLs
    print("\n🔗 **ACTUALLY VISITED URLS (No hallucinations):**")
    for result in successful:
        print(f"• {result['url']}")

if __name__ == "__main__":
    main()