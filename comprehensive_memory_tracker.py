#!/usr/bin/env python3
"""
Comprehensive Memory Market Tracker
Combines:
1. DRAMExchange charts (public visual trends)
2. Public retail prices (Amazon, Newegg)
3. Market news and analysis
"""

import json
import time
from datetime import datetime
from pathlib import Path
import sys
import subprocess
import os

try:
    import requests
    from bs4 import BeautifulSoup
    import re
    HAS_LIBS = True
except ImportError:
    HAS_LIBS = False

DATA_DIR = Path(__file__).parent / "memory_prices"
CHARTS_DIR = DATA_DIR / "dramexchange_charts"

# DRAMExchange charts (publicly accessible)
DRAMEXCHANGE_CHARTS = [
    {
        "name": "DRAM Spot Price Chart",
        "url": "https://chart.dramexchange.com/getimage.php?type=dx&item=dram&id=47&class=spot&size=s",
        "category": "dram_spot"
    },
    {
        "name": "Flash Spot Price Chart", 
        "url": "https://chart.dramexchange.com/getimage.php?type=dx&item=flash&id=48&class=spot&size=s",
        "category": "flash_spot"
    }
]

# Public retail sources
RETAIL_SOURCES = [
    {
        "name": "Amazon Memory Best Sellers",
        "url": "https://www.amazon.com/Best-Sellers-Computers-Accessories-Memory/zgbs/pc/172500",
        "category": "retail_prices"
    },
    {
        "name": "Newegg Memory",
        "url": "https://www.newegg.com/p/pl?N=100007952",
        "category": "retail_prices"
    }
]

# Market news sources
NEWS_SOURCES = [
    {
        "name": "Tom's Hardware Memory",
        "url": "https://www.tomshardware.com/tag/memory",
        "category": "market_news"
    },
    {
        "name": "Google News Memory Search",
        "url": "https://news.google.com/search?q=memory+prices+dram+nand+2026",
        "category": "news_aggregator"
    }
]

def download_dramexchange_chart(chart_info):
    """Download DRAMExchange chart image."""
    name = chart_info["name"]
    url = chart_info["url"]
    category = chart_info["category"]
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.dramexchange.com/"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            return {
                "success": False,
                "name": name,
                "url": url,
                "category": category,
                "error": f"HTTP {response.status_code}"
            }
        
        # Save chart
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"{timestamp}_{category}.png"
        filepath = CHARTS_DIR / filename
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return {
            "success": True,
            "name": name,
            "url": url,
            "category": category,
            "filename": filename,
            "filepath": str(filepath),
            "size_bytes": len(response.content)
        }
        
    except Exception as e:
        return {
            "success": False,
            "name": name,
            "url": url,
            "category": category,
            "error": str(e)
        }

def scrape_retail_prices(source):
    """Scrape retail sites for memory prices."""
    name = source["name"]
    url = source["url"]
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            return {
                "success": False,
                "name": name,
                "url": url,
                "error": f"HTTP {response.status_code}"
            }
        
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()
        
        # Extract prices
        prices = re.findall(r'\$(\d+\.?\d*)', text)
        float_prices = []
        for price in prices:
            try:
                price_float = float(price)
                if 10 < price_float < 1000:  # Reasonable memory price range
                    float_prices.append(price_float)
            except ValueError:
                continue
        
        return {
            "success": True,
            "name": name,
            "url": url,
            "prices_found": len(float_prices),
            "unique_prices": sorted(list(set(float_prices)))[:10],
            "sample_prices": float_prices[:5]
        }
        
    except Exception as e:
        return {
            "success": False,
            "name": name,
            "url": url,
            "error": str(e)
        }

def scrape_market_news(source):
    """Scrape market news for memory trends."""
    name = source["name"]
    url = source["url"]
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            return {
                "success": False,
                "name": name,
                "url": url,
                "error": f"HTTP {response.status_code}"
            }
        
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()
        
        # Look for memory-related content
        memory_keywords = ['dram', 'nand', 'memory', 'ram', 'flash', 'price', 'market']
        mentions = []
        
        for line in text.split('\n'):
            line = line.strip()
            if any(keyword in line.lower() for keyword in memory_keywords):
                if 30 < len(line) < 200:
                    mentions.append(line[:150])
        
        return {
            "success": True,
            "name": name,
            "url": url,
            "mentions_found": len(mentions),
            "sample_mentions": mentions[:3]
        }
        
    except Exception as e:
        return {
            "success": False,
            "name": name,
            "url": url,
            "error": str(e)
        }

def generate_comprehensive_report(chart_results, retail_results, news_results):
    """Generate comprehensive memory market report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    lines = []
    lines.append("💰 **COMPREHENSIVE MEMORY MARKET REPORT**")
    lines.append(f"Time: {timestamp} SGT")
    lines.append("")
    
    # DRAMExchange Charts section
    lines.append("## 📊 **DRAMEXCHANGE MARKET CHARTS**")
    lines.append("")
    lines.append("Publicly accessible chart images showing price trends")
    lines.append("")
    
    successful_charts = [r for r in chart_results if r["success"]]
    if successful_charts:
        lines.append(f"✅ **Downloaded {len(successful_charts)}/{len(chart_results)} charts**")
        lines.append("")
        for result in successful_charts:
            lines.append(f"**{result['name']}**")
            lines.append(f"• Category: {result['category']}")
            lines.append(f"• File: {result['filename']}")
            lines.append(f"• Size: {result['size_bytes']:,} bytes")
            lines.append("")
    else:
        lines.append("⚠️ No charts downloaded")
        lines.append("")
    
    # Retail Prices section
    lines.append("## 🛒 **RETAIL MEMORY PRICES**")
    lines.append("")
    lines.append("Actual consumer memory prices from major retailers")
    lines.append("")
    
    successful_retail = [r for r in retail_results if r["success"]]
    if successful_retail:
        all_retail_prices = []
        for result in successful_retail:
            lines.append(f"**{result['name']}**")
            lines.append(f"• URL: {result['url']}")
            lines.append(f"• Prices found: {result.get('prices_found', 0)}")
            
            if result.get('sample_prices'):
                lines.append("• Sample prices:")
                for price in result['sample_prices']:
                    lines.append(f"  - ${price:.2f}")
                all_retail_prices.extend(result.get('unique_prices', []))
            
            lines.append("")
        
        # Retail price analysis
        if all_retail_prices:
            lines.append("### 📈 **RETAIL PRICE ANALYSIS**")
            lines.append("")
            unique_prices = sorted(list(set(all_retail_prices)))
            avg_price = sum(all_retail_prices) / len(all_retail_prices) if all_retail_prices else 0
            
            lines.append(f"**Summary:**")
            lines.append(f"• Total price points: {len(all_retail_prices)}")
            lines.append(f"• Unique prices: {len(unique_prices)}")
            if unique_prices:
                lines.append(f"• Price range: ${min(unique_prices):.2f} - ${max(unique_prices):.2f}")
            lines.append(f"• Average: ${avg_price:.2f}")
            lines.append("")
            
            lines.append("**Most common retail prices:**")
            for price in unique_prices[:8]:
                lines.append(f"• ${price:.2f}")
            lines.append("")
    else:
        lines.append("⚠️ No retail price data collected")
        lines.append("")
    
    # Market News section
    lines.append("## 📰 **MARKET NEWS & TRENDS**")
    lines.append("")
    
    successful_news = [r for r in news_results if r["success"]]
    if successful_news:
        for result in successful_news:
            lines.append(f"**{result['name']}**")
            lines.append(f"• URL: {result['url']}")
            lines.append(f"• Memory mentions: {result.get('mentions_found', 0)}")
            
            if result.get('sample_mentions'):
                lines.append("• Sample mentions:")
                for mention in result['sample_mentions']:
                    lines.append(f"  - {mention}")
            
            lines.append("")
    else:
        lines.append("⚠️ No market news collected")
        lines.append("")
    
    # Data Sources section
    lines.append("## 🔗 **DATA SOURCES**")
    lines.append("")
    lines.append("**DRAMExchange Charts:**")
    for chart in DRAMEXCHANGE_CHARTS:
        lines.append(f"• {chart['url']}")
    
    lines.append("")
    lines.append("**Retail Price Sources:**")
    for source in RETAIL_SOURCES:
        lines.append(f"• {source['url']}")
    
    lines.append("")
    lines.append("**Market News Sources:**")
    for source in NEWS_SOURCES:
        lines.append(f"• {source['url']}")
    
    lines.append("")
    lines.append("---")
    lines.append("Generated: Comprehensive Memory Market Tracker")
    lines.append(f"Timestamp: {datetime.now().isoformat()}")
    
    return "\n".join(lines)

def main():
    """Main comprehensive tracker."""
    print("💰 Comprehensive Memory Market Tracker")
    print("=" * 60)
    print("Combining DRAMExchange charts, retail prices, and market news")
    print("")
    
    if not HAS_LIBS:
        print("❌ Missing libraries. Install with:")
        print("   pip install --user --break-system-packages requests beautifulsoup4")
        sys.exit(1)
    
    # Create directories
    DATA_DIR.mkdir(exist_ok=True)
    CHARTS_DIR.mkdir(exist_ok=True)
    
    timestamp = datetime.now().isoformat()
    
    # 1. Download DRAMExchange charts
    print("📊 Downloading DRAMExchange charts...")
    chart_results = []
    for chart in DRAMEXCHANGE_CHARTS:
        result = download_dramexchange_chart(chart)
        chart_results.append(result)
        
        if result["success"]:
            print(f"   ✅ {result['name']}: {result['filename']}")
        else:
            print(f"   ❌ {result['name']}: {result.get('error', 'Unknown')}")
        
        time.sleep(1)
    
    # 2. Scrape retail prices
    print("\n🛒 Scraping retail prices...")
    retail_results = []
    for source in RETAIL_SOURCES:
        result = scrape_retail_prices(source)
        retail_results.append(result)
        
        if result["success"]:
            print(f"   ✅ {result['name']}: {result.get('prices_found', 0)} prices")
        else:
            print(f"   ❌ {result['name']}: {result.get('error', 'Unknown')}")
        
        time.sleep(2)
    
    # 3. Scrape market news
    print("\n📰 Scraping market news...")
    news_results = []
    for source in NEWS_SOURCES:
        result = scrape_market_news(source)
        news_results.append(result)
        
        if result["success"]:
            print(f"   ✅ {result['name']}: {result.get('mentions_found', 0)} mentions")
        else:
            print(f"   ❌ {result['name']}: {result.get('error', 'Unknown')}")
        
        time.sleep(2)
    
    # Generate report
    report = generate_comprehensive_report(chart_results, retail_results, news_results)
    
    # Print summary
    print("\n" + "=" * 60)
    successful_charts = len([r for r in chart_results if r["success"]])
    successful_retail = len([r for r in retail_results if r["success"]])
    successful_news = len([r for r in news_results if r["success"]])
    
    total_prices = sum([r.get('prices_found', 0) for r in retail_results if r["success"]])
    
    print(f"📊 COMPREHENSIVE SUMMARY:")
    print(f"   • Charts: {successful_charts}/{len(chart_results)} successful")
    print(f"   • Retail sources: {successful_retail}/{len(retail_results)} successful")
    print(f"   • News sources: {successful_news}/{len(news_results)} successful")
    print(f"   • Total prices found: {total_prices}")
    print("=" * 60)
    
    # Save data
    data = {
        "timestamp": timestamp,
        "charts": chart_results,
        "retail": retail_results,
        "news": news_results,
        "metadata": {
            "total_sources": len(chart_results) + len(retail_results) + len(news_results),
            "successful_sources": successful_charts + successful_retail + successful_news,
            "total_prices": total_prices
        }
    }
    
    data_file = DATA_DIR / f"comprehensive_data_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    report_file = DATA_DIR / f"comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    report_file.write_text(report)
    
    print(f"\n📁 Data saved to: {data_file}")
    print(f"📄 Report saved to: {report_file}")
    
    # Save to Obsidian
    try:
        obsidian_dir = Path.home() / "Documents" / "openclaw" / "World News"
        obsidian_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{datetime.now().strftime('%Y-%m-%d')}_Memory_Market_Report_-_{datetime.now().strftime('%Y%m%d_%H%M')}_SGT.md"
        filepath = obsidian_dir / filename
        filepath.write_text(report)
        print(f"📁 Report saved to Obsidian: {filepath}")
        
        # Push to GitHub
        try:
            push_to_github(filepath, f"💰 Comprehensive Memory Market Report: {datetime.now().strftime('%Y-%m-%d %H:%M')} SGT")
        except Exception as git_error:
            print(f"⚠️  GitHub push failed (will retry later): {git_error}")
            
    except Exception as e:
        print(f"❌ Failed to save to Obsidian: {e}")
    
    # Final summary
    print("\n✅ **COMPREHENSIVE MEMORY TRACKER COMPLETE:**")
    print(f"   • Combines DRAMExchange charts + retail prices + market news")
    print(f"   • Daily automated reports at 9 AM SGT")
    print(f"   • No login required - all sources publicly accessible")

def push_to_github(filepath, commit_message):
    """Push report to GitHub repository."""
    obsidian_vault = Path.home() / "Documents" / "openclaw"
    
    # Navigate to Obsidian vault
    original_cwd = Path.cwd()
    os.chdir(obsidian_vault)
    
    try:
        # Add file to git
        subprocess.run(["git", "add", str(filepath.relative_to(obsidian_vault))], 
                      check=True, capture_output=True, text=True)
        
        # Commit
        subprocess.run(["git", "commit", "-m", commit_message], 
                      check=True, capture_output=True, text=True)
        
        # Push to GitHub
        result = subprocess.run(["git", "push", "origin", "main"], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Successfully pushed to GitHub: {commit_message}")
        else:
            # Try with -u flag if first push
            subprocess.run(["git", "push", "-u", "origin", "main"], 
                          capture_output=True, text=True)
            print(f"✅ Successfully pushed to GitHub (with -u flag): {commit_message}")
            
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Git operation failed: {e.stderr}")
    finally:
        # Return to original directory
        os.chdir(original_cwd)

if __name__ == "__main__":
    main()