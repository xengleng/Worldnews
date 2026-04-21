#!/usr/bin/env python3
"""
DRAMExchange Real Price Scraper
Extracts actual prices from DRAMExchange pages
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

DRAMEXCHANGE_URLS = [
    {
        "name": "DRAM Spot Prices",
        "url": "https://www.dramexchange.com/Price/Dram_Spot",
        "category": "dram_spot"
    },
    {
        "name": "Module Spot Prices",
        "url": "https://www.dramexchange.com/Price/Module_Spot",
        "category": "module_spot"
    },
    {
        "name": "Flash Spot Prices",
        "url": "https://www.dramexchange.com/Price/Flash_Spot",
        "category": "flash_spot"
    },
    {
        "name": "GDDR Spot Prices",
        "url": "https://www.dramexchange.com/Price/GDDR_Spot",
        "category": "gddr_spot"
    },
    {
        "name": "Wafer Spot Prices",
        "url": "https://www.dramexchange.com/Price/Wafer_Spot",
        "category": "wafer_spot"
    },
    {
        "name": "Memory Card Spot Prices",
        "url": "https://www.dramexchange.com/Price/MemoryCard_Spot",
        "category": "memorycard_spot"
    },
    {
        "name": "National Contract DRAM Details",
        "url": "https://www.dramexchange.com/Price/NationalContractDramDetail",
        "category": "contract_dram"
    },
    {
        "name": "National Contract Flash Details",
        "url": "https://www.dramexchange.com/Price/NationalContractFlashDetail",
        "category": "contract_flash"
    }
]

def extract_dramexchange_prices(html_content, url):
    """Extract prices from DRAMExchange HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Method 1: Look for tables (common for price data)
    price_data = []
    
    # Look for price tables - DRAMExchange often uses tables with USD prices
    tables = soup.find_all('table')
    
    for table_idx, table in enumerate(tables):
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            row_text = ' '.join([cell.get_text(strip=True) for cell in cells])
            
            # Look for price patterns in table rows
            price_patterns = [
                r'(\d+\.?\d*)\s*USD',
                r'USD\s*(\d+\.?\d*)',
                r'\$(\d+\.?\d*)',
                r'price.*?(\d+\.?\d*)',
                r'(\d+\.?\d*)\s*per'
            ]
            
            for pattern in price_patterns:
                matches = re.findall(pattern, row_text, re.IGNORECASE)
                for match in matches:
                    price_str = match if isinstance(match, str) else match[0]
                    try:
                        price = float(price_str)
                        # Memory prices are typically in specific ranges
                        if 0.01 < price < 1000:  # Reasonable range for memory prices
                            price_data.append({
                                "price": price,
                                "unit": "USD",
                                "source": f"table_{table_idx}",
                                "context": row_text[:100]
                            })
                    except ValueError:
                        continue
    
    # Method 2: Look for specific memory product mentions with prices
    products = []
    
    # Common memory product patterns
    product_patterns = [
        r'(DDR\d[^\$]*\$?\s*(\d+\.?\d*))',
        r'(NAND[^\$]*\$?\s*(\d+\.?\d*))',
        r'(Flash[^\$]*\$?\s*(\d+\.?\d*))',
        r'(DRAM[^\$]*\$?\s*(\d+\.?\d*))',
        r'(Module[^\$]*\$?\s*(\d+\.?\d*))',
        r'(Wafer[^\$]*\$?\s*(\d+\.?\d*))',
        r'(GDDR[^\$]*\$?\s*(\d+\.?\d*))'
    ]
    
    text = soup.get_text()
    for pattern in product_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            full_text = match[0]
            price_str = match[1]
            try:
                price = float(price_str)
                if 0.01 < price < 1000:
                    products.append({
                        "product": full_text[:150],
                        "price": price,
                        "unit": "USD"
                    })
            except ValueError:
                continue
    
    # Method 3: Look for any numbers that look like prices with 4 decimal places
    # (common for memory spot prices: e.g., 4.1234)
    precise_prices = re.findall(r'(\d+\.\d{4})', text)
    for price_str in precise_prices:
        try:
            price = float(price_str)
            if 0.01 < price < 100:
                price_data.append({
                    "price": price,
                    "unit": "USD",
                    "source": "precise_decimal",
                    "context": "4-decimal precision (typical for spot prices)"
                })
        except ValueError:
            continue
    
    # Method 4: Look for price change indicators (+, - percentages)
    change_patterns = re.findall(r'([+-]\d+\.?\d*%)', text)
    
    return {
        "price_data": price_data,
        "products": products[:20],  # Limit products
        "table_count": len(tables),
        "price_changes": change_patterns[:10],
        "text_sample": text[:500]  # First 500 chars for debugging
    }

def scrape_dramexchange_real(url_info):
    """Scrape DRAMExchange for real price data."""
    name = url_info["name"]
    url = url_info["url"]
    category = url_info["category"]
    
    print(f"   • {name}: {url}")
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        
        response = requests.get(url, headers=headers, timeout=20)
        
        if response.status_code != 200:
            return {
                "success": False,
                "name": name,
                "url": url,
                "category": category,
                "error": f"HTTP {response.status_code}",
                "scraped_at": datetime.now().isoformat()
            }
        
        # Extract prices using specialized function
        extraction_result = extract_dramexchange_prices(response.content, url)
        
        # Get page info
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.get_text(strip=True) if soup.title else ""
        
        # Check if we're actually getting price data or just login page
        is_login_page = "login" in title.lower() or "sign in" in title.lower()
        
        return {
            "success": True,
            "name": name,
            "url": url,
            "category": category,
            "title": title,
            "is_login_page": is_login_page,
            "price_count": len(extraction_result["price_data"]),
            "prices": extraction_result["price_data"][:30],  # Limit to 30 prices
            "products_found": len(extraction_result["products"]),
            "products": extraction_result["products"][:10],  # Top 10 products
            "table_count": extraction_result["table_count"],
            "price_changes": extraction_result["price_changes"],
            "text_sample": extraction_result["text_sample"],
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

def generate_real_report(results):
    """Generate report from DRAMExchange price data."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    lines = []
    lines.append("💰 **DRAMEXCHANGE REAL PRICE REPORT**")
    lines.append(f"Time: {timestamp} SGT")
    lines.append("")
    lines.append("## 📋 **DRAMEXCHANGE PRICE DATA**")
    lines.append("")
    lines.append("Extracting actual prices from DRAMExchange pages")
    lines.append("")
    
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    if successful:
        lines.append(f"✅ **Successfully scraped: {len(successful)}/{len(results)} pages**")
        lines.append("")
        
        total_prices = 0
        all_prices = []
        all_products = []
        
        for result in successful:
            lines.append(f"### {result['name']}")
            lines.append(f"**Category:** {result['category']}")
            lines.append(f"**URL:** {result['url']}")
            
            if result.get('title'):
                lines.append(f"**Page Title:** {result['title']}")
                if result.get('is_login_page'):
                    lines.append("⚠️ **Note:** Page appears to be login page")
            
            lines.append(f"**Prices Found:** {result.get('price_count', 0)}")
            lines.append(f"**Products Found:** {result.get('products_found', 0)}")
            
            if result.get('prices'):
                price_values = [p['price'] for p in result['prices']]
                all_prices.extend(price_values)
                total_prices += len(price_values)
                
                if price_values:
                    lines.append("**Sample Prices:**")
                    unique_prices = sorted(list(set(price_values)))[:8]
                    for price in unique_prices:
                        lines.append(f"• ${price:.4f} USD")
            
            if result.get('products'):
                all_products.extend(result['products'])
                lines.append("**Products Mentioned:**")
                for product in result['products'][:3]:
                    lines.append(f"• {product['product']} - ${product['price']:.4f} USD")
            
            if result.get('price_changes'):
                lines.append("**Price Changes:**")
                for change in result['price_changes'][:3]:
                    lines.append(f"• {change}")
            
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
            lines.append("**Most Common Prices:**")
            # Count frequency
            price_counts = {}
            for price in all_prices:
                price_key = f"{price:.4f}"
                price_counts[price_key] = price_counts.get(price_key, 0) + 1
            
            sorted_prices = sorted(price_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            for price_str, count in sorted_prices:
                percentage = (count / len(all_prices)) * 100
                lines.append(f"• ${price_str} USD ({count} times, {percentage:.1f}%)")
    
    # Product analysis
    if all_products:
        lines.append("")
        lines.append("## 🏷️ **PRODUCT ANALYSIS**")
        lines.append("")
        lines.append(f"**Total products found:** {len(all_products)}")
        lines.append("")
        lines.append("**Sample Products with Prices:**")
        for product in all_products[:10]:
            lines.append(f"• {product['product']} - ${product['price']:.4f} USD")
    
    lines.append("")
    lines.append("## 🔗 **DRAMEXCHANGE URLS**")
    lines.append("")
    for url_info in DRAMEXCHANGE_URLS:
        lines.append(f"• {url_info['url']}")
    
    lines.append("")
    lines.append("---")
    lines.append("Generated: DRAMExchange Real Scraper")
    lines.append(f"Timestamp: {datetime.now().isoformat()}")
    
    return "\n".join(lines)

def main():
    """Main DRAMExchange real scraper."""
    print("💰 DRAMExchange Real Price Scraper")
    print("=" * 60)
    print("Extracting actual prices from DRAMExchange pages")
    print("Looking for price tables and memory product mentions")
    print("")
    
    if not HAS_LIBS:
        print("❌ Missing libraries. Install with:")
        print("   pip install --user --break-system-packages requests beautifulsoup4")
        sys.exit(1)
    
    DATA_DIR.mkdir(exist_ok=True)
    
    # Scrape DRAMExchange pages
    print("🌐 Scraping DRAMExchange for price data...")
    results = []
    
    for url_info in DRAMEXCHANGE_URLS:
        result = scrape_dramexchange_real(url_info)
        results.append(result)
        
        if result["success"]:
            status = "✅" if result.get('price_count', 0) > 0 else "⚠️"
            print(f"     {status} Found {result.get('price_count', 0)} prices, {result.get('products_found', 0)} products")
            if result.get('is_login_page'):
                print(f"     ⚠️ Page appears to be login page: {result.get('title', '')}")
        else:
            print(f"     ❌ Failed: {result.get('error', 'Unknown')}")
        
        time.sleep(2)  # Be respectful
    
    # Generate report
    report = generate_real_report(results)
    
    # Print summary
    print("\n" + "=" * 60)
    successful = [r for r in results if r["success"]]
    total_prices = sum([r.get('price_count', 0) for r in successful])
    total_products = sum([r.get('products_found', 0) for r in successful])
    
    print(f"📊 Summary: {len(successful)}/{len(results)} pages successful")
    print(f"💰 Prices found: {total_prices}")
    print(f"🏷️ Products found: {total_products}")
    print("=" * 60)
    
    # Save data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    data = {
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "metadata": {
            "total_urls": len(DRAMEXCHANGE_URLS),
            "successful": len(successful),
            "total_prices": total_prices,
            "total_products": total_products
        }
    }
    
    data_file = DATA_DIR / f"dramexchange_real_data_{timestamp}.json"
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    report_file = DATA_DIR / f"dramexchange_real_report_{timestamp}.txt"
    report_file.write_text(report)
    
    print(f"\n📁 Data saved to: {data_file}")
    print(f"📄 Report saved to: {report_file}")
    
    # Save to Obsidian
    try:
        obsidian_dir = Path.home() / "Documents" / "openclaw" / "World News"
        obsidian_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{datetime.now().strftime('%Y-%m-%d')}_DRAMExchange_Real_Prices_-_{timestamp}_SGT.md"
        filepath = obsidian_dir / filename
        filepath.write_text(report)
        print(f"📁 Report saved to Obsidian: {filepath}")
    except Exception as e:
        print(f"❌ Failed to save to Obsidian: {e}")
    
    # Summary
    print("\n✅ **DRAMEXCHANGE REAL SCRAPER COMPLETE:**")
    print(f"   • URLs attempted: {