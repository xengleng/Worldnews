#!/usr/bin/env python3
"""
Price Extraction Scraper
Actually extracts price information from scraped websites.
"""

import json
import re
from datetime import datetime
from pathlib import Path
import time

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_LIBS = True
except ImportError:
    HAS_LIBS = False

DATA_DIR = Path(__file__).parent / "memory_prices"

def extract_prices_from_text(text):
    """Extract price patterns from text."""
    patterns = [
        # $12.34, $1,234.56
        r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
        # USD 12.34, 12.34 USD
        r'(?:USD\s*)?(\d+\.?\d*)\s*(?:USD)?',
        # 12.34 dollars
        r'(\d+\.?\d*)\s*dollars',
        # Price: $12.34
        r'[Pp]rice[:\s]*\$?(\d+\.?\d*)',
        # DDR4/5 price mentions
        r'DDR[45].*?\$?(\d+\.?\d*)',
    ]
    
    prices = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # Clean the match (remove commas)
            clean_match = match.replace(',', '')
            try:
                price = float(clean_match)
                # Filter reasonable memory prices (not page numbers, years, etc.)
                if 0.5 < price < 1000:  # Memory prices typically in this range
                    prices.append({
                        "price": price,
                        "currency": "USD",
                        "pattern": pattern[:30]
                    })
            except ValueError:
                continue
    
    return prices

def scrape_and_extract_prices():
    """Scrape sites and extract price information."""
    print("💰 Scraping for actual price information...")
    print("=" * 60)
    
    sites = [
        {
            "name": "DRAMExchange Home",
            "url": "https://www.dramexchange.com/",
            "note": "Market research site - may have price mentions"
        },
        {
            "name": "Google News Memory Prices",
            "url": "https://news.google.com/search?q=memory+price+2026+dram+nand",
            "note": "News articles about memory prices"
        },
        {
            "name": "Tom's Hardware Memory News",
            "url": "https://www.tomshardware.com/tag/memory",
            "note": "Tech news with price discussions"
        }
    ]
    
    all_results = []
    
    for site in sites:
        print(f"\n🌐 {site['name']}")
        print(f"   URL: {site['url']}")
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(site["url"], headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Get all text
                text = soup.get_text()
                
                # Extract prices
                prices = extract_prices_from_text(text)
                
                # Get article titles/headlines that might contain price info
                headlines = []
                for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a']):
                    headline = tag.get_text(strip=True)
                    if headline and any(keyword in headline.lower() for keyword in ['price', 'dram', 'nand', 'memory', '$']):
                        headlines.append(headline[:100])
                
                result = {
                    "success": True,
                    "name": site["name"],
                    "url": site["url"],
                    "prices_found": len(prices),
                    "prices": prices[:10],  # First 10 prices
                    "headlines": headlines[:5],  # First 5 relevant headlines
                    "note": site["note"],
                    "scraped_at": datetime.now().isoformat()
                }
                
                all_results.append(result)
                
                print(f"   ✅ Found {len(prices)} price mentions")
                if prices:
                    print(f"   Sample prices: {[p['price'] for p in prices[:3]]}")
                
            else:
                print(f"   ❌ HTTP {response.status_code}")
                all_results.append({
                    "success": False,
                    "name": site["name"],
                    "url": site["url"],
                    "error": f"HTTP {response.status_code}",
                    "scraped_at": datetime.now().isoformat()
                })
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            all_results.append({
                "success": False,
                "name": site["name"],
                "url": site["url"],
                "error": str(e),
                "scraped_at": datetime.now().isoformat()
            })
        
        time.sleep(2)  # Be polite
    
    return all_results

def analyze_extracted_prices(results):
    """Analyze the extracted price data."""
    print("\n📊 Analyzing extracted price data...")
    
    successful = [r for r in results if r["success"]]
    all_prices = []
    
    for result in successful:
        all_prices.extend(result.get("prices", []))
    
    if not all_prices:
        print("   ⚠️ No specific prices extracted")
        return None
    
    # Group by price ranges
    price_ranges = {
        "under_10": [p for p in all_prices if p["price"] < 10],
        "10_50": [p for p in all_prices if 10 <= p["price"] < 50],
        "50_100": [p for p in all_prices if 50 <= p["price"] < 100],
        "100_500": [p for p in all_prices if 100 <= p["price"] < 500],
        "over_500": [p for p in all_prices if p["price"] >= 500]
    }
    
    # Calculate statistics
    if all_prices:
        prices_only = [p["price"] for p in all_prices]
        avg_price = sum(prices_only) / len(prices_only)
        min_price = min(prices_only)
        max_price = max(prices_only)
    else:
        avg_price = min_price = max_price = 0
    
    analysis = {
        "total_prices": len(all_prices),
        "unique_prices": len(set(p["price"] for p in all_prices)),
        "average_price": avg_price,
        "min_price": min_price,
        "max_price": max_price,
        "price_ranges": {k: len(v) for k, v in price_ranges.items()},
        "sources_with_prices": len([r for r in successful if r.get("prices")]),
        "most_common_prices": sorted(set(p["price"] for p in all_prices))[:5]
    }
    
    print(f"   • Total price mentions: {analysis['total_prices']}")
    print(f"   • Unique prices: {analysis['unique_prices']}")
    print(f"   • Price range: ${analysis['min_price']:.2f} - ${analysis['max_price']:.2f}")
    print(f"   • Average: ${analysis['average_price']:.2f}")
    
    return analysis

def generate_price_report(results, analysis):
    """Generate report with actual price data."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    lines = []
    lines.append("💰 **REAL PRICE EXTRACTION REPORT**")
    lines.append(f"Time: {timestamp} SGT")
    lines.append("")
    lines.append("## 🔍 **ACTUALLY SCRAPED WEBSITES**")
    lines.append("")
    
    successful = [r for r in results if r["success"]]
    
    for result in successful:
        lines.append(f"✅ **{result['name']}**")
        lines.append(f"• URL: {result['url']}")
        lines.append(f"• Prices found: {result.get('prices_found', 0)}")
        lines.append(f"• Note: {result.get('note', '')}")
        
        if result.get("headlines"):
            lines.append("• Relevant headlines:")
            for headline in result["headlines"][:3]:
                lines.append(f"  - {headline}")
        
        if result.get("prices"):
            lines.append("• Sample prices:")
            for price in result["prices"][:3]:
                lines.append(f"  - ${price['price']:.2f} USD")
        
        lines.append("")
    
    lines.append("## 📊 **PRICE ANALYSIS**")
    lines.append("")
    
    if analysis:
        lines.append(f"**Summary:**")
        lines.append(f"• Total price mentions: {analysis['total_prices']}")
        lines.append(f"• Unique prices: {analysis['unique_prices']}")
        lines.append(f"• Price range: ${analysis['min_price']:.2f} - ${analysis['max_price']:.2f}")
        lines.append(f"• Average price: ${analysis['average_price']:.2f}")
        lines.append("")
        
        lines.append("**Price distribution:**")
        for range_name, count in analysis["price_ranges"].items():
            if count > 0:
                lines.append(f"• {range_name.replace('_', ' ').title()}: {count} prices")
        
        lines.append("")
        lines.append("**Most common prices:**")
        for price in analysis["most_common_prices"]:
            lines.append(f"• ${price:.2f}")
    else:
        lines.append("⚠️ No price data extracted")
        lines.append("")
        lines.append("**Possible reasons:**")
        lines.append("1. Price data often in paid sections")
        lines.append("2. News sites discuss trends, not specific prices")
        lines.append("3. Need to scrape at right time (when articles published)")
    
    lines.append("")
    lines.append("## 🎯 **NEXT STEPS FOR BETTER PRICE DATA**")
    lines.append("")
    
    next_steps = [
        "1. **Scrape e-commerce for retail prices:**",
        "   - Amazon: RAM, SSD listings",
        "   - Newegg: Component prices",
        "   - Microcenter: Retail memory prices",
        "",
        "2. **Monitor deal sites:**",
        "   - Slickdeals: Memory/SSD deals",
        "   - TechBargains: Price drops",
        "",
        "3. **Use price tracking tools:**",
        "   - Keepa (Amazon price history)",
        "   - CamelCamelCamel",
        "",
        "4. **Check manufacturer sites:**",
        "   - Micron, Samsung investor relations",
        "   - Quarterly reports with ASP data"
    ]
    
    for step in next_steps:
        lines.append(step)
    
    lines.append("")
    lines.append("## 🔗 **ACTUALLY VISITED URLS**")
    lines.append("")
    for result in successful:
        lines.append(f"• {result['url']}")
    
    lines.append("")
    lines.append("---")
    lines.append("Generated: Price Extraction Scraper v1.0")
    lines.append(f"Websites scraped: {len(results)}")
    lines.append(f"Successful: {len(successful)}")
    
    return "\n".join(lines)

def main():
    """Main function."""
    print("💰 Real Price Extraction Scraper")
    print("=" * 60)
    print("Actually scraping for price information...")
    print("")
    
    if not HAS_LIBS:
        print("❌ Missing libraries. Install with:")
        print("   pip install --user --break-system-packages requests beautifulsoup4")
        return
    
    DATA_DIR.mkdir(exist_ok=True)
    
    # Scrape and extract prices
    results = scrape_and_extract_prices()
    
    # Analyze prices
    analysis = analyze_extracted_prices(results)
    
    # Generate report
    report = generate_price_report(results, analysis)
    
    # Print report
    print("\n" + report)
    
    # Save data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    data_file = DATA_DIR / f"price_extraction_{timestamp}.json"
    
    with open(data_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "analysis": analysis,
            "metadata": {
                "total_scrapes": len(results),
                "successful_scrapes": len([r for r in results if r["success"]]),
                "total_prices": analysis["total_prices"] if analysis else 0
            }
        }, f, indent=2)
    
    report_file = DATA_DIR / f"price_report_{timestamp}.txt"
    report_file.write_text(report)
    
    print(f"\n📁 Data saved to: {data_file}")
    print(f"📄 Report saved to: {report_file}")
    
    # Show what we actually got
    print("\n✅ **REAL DATA COLLECTED:**")
    successful = [r for r in results if r["success"]]
    print(f"   • Websites scraped: {len(successful)}/{len(results)}")
    if analysis:
        print(f"   • Price mentions found: {analysis['total_prices']}")
        print(f"   • Price range: ${analysis['min_price']:.2f} - ${analysis['max_price']:.2f}")
    
    print("\n🔗 **ACTUAL WORKING URLS (No hallucinations):**")
    for result in successful:
        print(f"   • {result['url']}")

if __name__ == "__main__":
    main()