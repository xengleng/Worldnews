#!/usr/bin/env python3
"""
DRAMExchange Memory Price Scraper
Scrapes actual DRAMExchange URLs for memory spot prices.
Primary data sources as specified by user.
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

# Primary DRAMExchange URLs as specified
DRAMEXCHANGE_URLS = [
    {
        "name": "DRAM Spot Prices",
        "url": "https://www.dramexchange.com/Price/Dram_Spot",
        "category": "dram_spot",
        "description": "DRAM spot market prices"
    },
    {
        "name": "Module Spot Prices",
        "url": "https://www.dramexchange.com/Price/Module_Spot",
        "category": "module_spot",
        "description": "Memory module spot prices"
    },
    {
        "name": "Flash Spot Prices",
        "url": "https://www.dramexchange.com/Price/Flash_Spot",
        "category": "flash_spot",
        "description": "NAND flash spot prices"
    },
    {
        "name": "GDDR Spot Prices",
        "url": "https://www.dramexchange.com/Price/GDDR_Spot",
        "category": "gddr_spot",
        "description": "GDDR memory spot prices"
    },
    {
        "name": "Wafer Spot Prices",
        "url": "https://www.dramexchange.com/Price/Wafer_Spot",
        "category": "wafer_spot",
        "description": "Memory wafer spot prices"
    },
    {
        "name": "Memory Card Spot Prices",
        "url": "https://www.dramexchange.com/Price/MemoryCard_Spot",
        "category": "memorycard_spot",
        "description": "Memory card spot prices"
    },
    {
        "name": "National Contract DRAM Details",
        "url": "https://www.dramexchange.com/Price/NationalContractDramDetail",
        "category": "contract_dram",
        "description": "National contract DRAM pricing details"
    },
    {
        "name": "National Contract Flash Details",
        "url": "https://www.dramexchange.com/Price/NationalContractFlashDetail",
        "category": "contract_flash",
        "description": "National contract flash pricing details"
    }
]

def scrape_dramexchange_page(url_info):
    """Scrape a single DRAMExchange page for price data."""
    name = url_info["name"]
    url = url_info["url"]
    category = url_info["category"]
    
    print(f"   • {name}: {url}")
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        
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
        
        # Extract prices
        price_patterns = [
            r'(\d+\.?\d*)\s*USD',
            r'USD\s*(\d+\.?\d*)',
            r'\$(\d+\.?\d*)',
            r'price.*?(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*per'
        ]
        
        price_data = []
        for pattern in price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                price_str = match if isinstance(match, str) else match[0]
                try:
                    price = float(price_str)
                    if 0.01 < price < 1000:
                        price_data.append({
                            "price": price,
                            "unit": "USD",
                            "source": "regex"
                        })
                except ValueError:
                    continue
        
        # Look for memory products
        products = []
        memory_keywords = ['dram', 'ddr', 'nand', 'flash', 'module', 'wafer', 'gddr', 'memory']
        
        for line in text.split('\n'):
            line = line.strip()
            if any(keyword in line.lower() for keyword in memory_keywords):
                price_matches = re.findall(r'(\d+\.?\d*)\s*USD|\$(\d+\.?\d*)', line)
                if price_matches:
                    for match in price_matches:
                        price = match[0] or match[1]
                        try:
                            price_float = float(price)
                            products.append({
                                "description": line[:100],
                                "price": price_float,
                                "unit": "USD"
                            })
                        except ValueError:
                            continue
        
        # Get page info
        title = soup.title.get_text(strip=True) if soup.title else ""
        
        return {
            "success": True,
            "name": name,
            "url": url,
            "category": category,
            "title": title,
            "price_count": len(price_data),
            "prices": price_data[:20],
            "products_found": len(products),
            "products": products[:10],
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

def generate_report(dramexchange_results):
    """Generate DRAMExchange report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    lines = []
    lines.append("💰 **DRAMEXCHANGE MEMORY PRICE REPORT**")
    lines.append(f"Time: {timestamp} SGT")
    lines.append("")
    lines.append("## 📋 **PRIMARY DATA SOURCES**")
    lines.append("")
    
    successful = [r for r in dramexchange_results if r["success"]]
    failed = [r for r in dramexchange_results if not r["success"]]
    
    if successful:
        lines.append(f"✅ **Successfully scraped: {len(successful)}/{len(dramexchange_results)} pages**")
        lines.append("")
        
        all_prices = []
        
        for result in successful:
            lines.append(f"### {result['name']}")
            lines.append(f"**Category:** {result['category']}")
            lines.append(f"**URL:** {result['url']}")
            
            if result.get('title'):
                lines.append(f"**Page Title:** {result['title']}")
            
            lines.append(f"**Prices Found:** {result.get('price_count', 0)}")
            
            if result.get('prices'):
                price_values = [p['price'] for p in result['prices']]
                all_prices.extend(price_values)
                
                if price_values:
                    lines.append("**Sample Prices:**")
                    for price_info in result['prices'][:5]:
                        lines.append(f"• ${price_info['price']:.4f} USD")
            
            if result.get('products'):
                lines.append("**Products Mentioned:**")
                for product in result['products'][:3]:
                    lines.append(f"• {product['description']} - ${product['price']:.2f} USD")
            
            lines.append("")
    else:
        lines.append("⚠️ **No pages successfully scraped**")
        lines.append("")
    
    if failed:
        lines.append("## ❌ **FAILED SCRAPES**")
        lines.append("")
        for result in failed:
            lines.append(f"• {result['name']}: {result.get('error', 'Unknown error')}")
        lines.append("")
    
    # Price analysis
    if all_prices:
        lines.append("## 📊 **PRICE ANALYSIS**")
        lines.append("")
        
        unique_prices = sorted(list(set(all_prices)))
        if all_prices:
            avg_price = sum(all_prices) / len(all_prices)
        else:
            avg_price = 0
        
        lines.append(f"**Summary:**")
        lines.append(f"• Total price points: {len(all_prices)}")
        lines.append(f"• Unique prices: {len(unique_prices)}")
        if unique_prices:
            lines.append(f"• Price range: ${min(unique_prices):.4f} - ${max(unique_prices):.4f} USD")
        lines.append(f"• Average: ${avg_price:.4f} USD")
        lines.append("")
        
        if unique_prices:
            lines.append("**Common Price Points:**")
            for price in unique_prices[:10]:
                lines.append(f"• ${price:.4f} USD")
    
    lines.append("")
    lines.append("## 🔗 **ACTUAL URLS SCRAPED**")
    lines.append("")
    for url_info in DRAMEXCHANGE_URLS:
        lines.append(f"• {url_info['url']}")
    
    lines.append("")
    lines.append("---")
    lines.append("Generated: DRAMExchange Scraper")
    lines.append(f"Timestamp: {datetime.now().isoformat()}")
    
    return "\n".join(lines)

def save_to_obsidian(report_content):
    """Save report to Obsidian vault."""
    try:
        obsidian_dir = Path.home() / "Documents" / "openclaw" / "World News"
        obsidian_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"{datetime.now().strftime('%Y-%m-%d')}_DRAMExchange_Memory_Prices_-_{timestamp}_SGT.md"
        filepath = obsidian_dir / filename
        
        filepath.write_text(report_content)
        print(f"📁 Report saved to Obsidian: {filepath}")
        
        return filepath
    except Exception as e:
        print(f"❌ Failed to save to Obsidian: {e}")
        return None

def main():
    """Main DRAMExchange scraper."""
    print("💰 DRAMExchange Memory Price Scraper")
    print("=" * 60)
    print("Scraping official DRAMExchange price pages")
    print("Primary data sources as specified")
    print("")
    
    if not HAS_LIBS:
        print("❌ Missing libraries. Install with:")
        print("   pip install --user --break-system-packages requests beautifulsoup4")
        sys.exit(1)
    
    DATA_DIR.mkdir(exist_ok=True)
    
    # Scrape DRAMExchange pages
    print("🌐 Scraping DRAMExchange price pages...")
    results = []
    
    for url_info in DRAMEXCHANGE_URLS:
        result = scrape_dramexchange_page(url_info)
        results.append(result)
        
        if result["success"]:
            print(f"     ✅ Found {result.get('price_count', 0)} prices")
        else:
            print(f"     ❌ Failed: {result.get('error', 'Unknown')}")
        
        time.sleep(2)  # Be respectful
    
    # Generate report
    report = generate_report(results)
    
    # Print report
    print("\n" + "=" * 60)
    print(report[:1000] + "..." if len(report) > 1000 else report)
    print("=" * 60)
    
    # Save data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    data = {
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "metadata": {
            "total_urls": len(DRAMEXCHANGE_URLS),
            "successful": len([r for r in results if r["success"]]),
            "total_prices": sum([len(r.get('prices', [])) for r in results if r["success"]])
        }
    }
    
    data_file = DATA_DIR / f"dramexchange_data_{timestamp}.json"
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    report_file = DATA_DIR / f"dramexchange_report_{timestamp}.txt"
    report_file.write_text(report)
    
    print(f"\n📁 Data saved to: {data_file}")
    print(f"📄 Report saved to: {report_file}")
    
    # Save to Obsidian
    obsidian_file = save_to_obsidian(report)
    
    # Summary
    print("\n✅ **DRAMEXCHANGE SCRAPER COMPLETE:**")
    print(f"   • URLs attempted: {len(results)}")
    print(f"   • Successful: {len([r for r in results if r['success']])}")
    print(f"   • Total prices found: {sum([len(r.get('prices', [])) for r in results if r['success']])}")
    
    if obsidian_file:
        print(f"   • Obsidian report: {obsidian_file}")
    
    print("\n🔗 **PRIMARY SOURCES USED:**")
    for url_info in DRAMEXCHANGE_URLS:
        print(f"   • {url_info['url']}")

if __name__ == "__main__":
    main()