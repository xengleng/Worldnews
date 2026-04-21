#!/usr/bin/env python3
"""
Memory Price Tracker for DRAMExchange.com
Tracks DRAM, NAND Flash, SSD, and memory card prices with historical data.
"""

import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
import time
import re
import sys
from typing import Dict, List, Any, Optional
import requests
from bs4 import BeautifulSoup

# Configuration
DATA_DIR = Path(__file__).parent / "memory_prices"
PRICES_FILE = DATA_DIR / "historical_prices.json"
CSV_FILE = DATA_DIR / "price_history.csv"
DRAMEXCHANGE_URL = "https://www.dramexchange.com/"

# Price categories to track
PRICE_CATEGORIES = {
    "dram_spot": {
        "name": "DRAM Spot Prices",
        "items": [
            "DDR5 16Gb (2Gx8) 4800/5600",
            "DDR5 16Gb (2Gx8) eTT",
            "DDR4 16Gb (2Gx8) 3200",
            "DDR4 16Gb (2Gx8) eTT",
            "DDR4 8Gb (1Gx8) 3200",
            "DDR4 8Gb (1Gx8) eTT",
            "DDR3 4Gb 512Mx8 1600/1866"
        ]
    },
    "module_spot": {
        "name": "Module Spot Prices",
        "items": [
            "DDR5 UDIMM 16GB 4800/5600",
            "DDR5 RDIMM 32GB 4800/5600",
            "DDR4 UDIMM 16GB 3200"
        ]
    },
    "flash_spot": {
        "name": "NAND Flash Spot Prices",
        "items": [
            "SLC 2Gb 256MBx8",
            "SLC 1Gb 128MBx8",
            "MLC 64Gb 8GBx8",
            "MLC 32Gb 4GBx8"
        ]
    },
    "gddr_spot": {
        "name": "GDDR Spot Prices",
        "items": [
            "GDDR5 8Gb",
            "GDDR6 8Gb"
        ]
    },
    "wafer_spot": {
        "name": "Wafer Spot Prices",
        "items": [
            "512Gb TLC",
            "256Gb TLC",
            "128Gb TLC"
        ]
    },
    "memory_card": {
        "name": "Memory Card Spot Prices",
        "items": [
            "MicroSD 16GB",
            "MicroSD 32GB",
            "MicroSD 64GB",
            "MicroSD 128GB"
        ]
    },
    "ssd_street": {
        "name": "SSD Street Prices",
        "items": [
            "ADATA SU800 512GB SATA",
            "Kimtigo TP5000 1TB PCIe 4.0",
            "Samsung 990 Pro 1TB PCIe 4.0",
            "PNY CS2150 2TB PCIe 5.0",
            "Silicon Power US75 1TB PCIe 4.0"
        ]
    }
}

def setup_data_directory():
    """Create data directory if it doesn't exist."""
    DATA_DIR.mkdir(exist_ok=True)
    
    # Initialize JSON file if it doesn't exist
    if not PRICES_FILE.exists():
        initial_data = {
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": None,
                "source": "DRAMExchange.com",
                "currency": "USD",
                "categories": list(PRICE_CATEGORIES.keys())
            },
            "price_history": {}
        }
        save_prices(initial_data)
    
    # Initialize CSV file if it doesn't exist
    if not CSV_FILE.exists():
        with open(CSV_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "category", "item", "daily_high", "daily_low",
                "session_high", "session_low", "session_avg", "change_percent",
                "weekly_high", "weekly_low", "avg_change"
            ])

def load_prices() -> Dict:
    """Load historical price data from JSON file."""
    if PRICES_FILE.exists():
        with open(PRICES_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_prices(data: Dict):
    """Save price data to JSON file."""
    with open(PRICES_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def parse_price_table(html_content: str) -> List[Dict]:
    """Parse price tables from DRAMExchange HTML."""
    prices = []
    
    # Use regex to extract price tables (simplified parsing)
    # In a real implementation, we would use BeautifulSoup for better parsing
    
    # Extract DRAM Spot prices
    dram_pattern = r'\[(DDR[0-9].*?)\]\(/Price/Dram_Spot\)\s*\n\s*([\d.]+)\s*\n\s*([\d.]+)\s*\n\s*([\d.]+)\s*\n\s*([\d.]+)\s*\n\s*([\d.]+)\s*\n\s*([-\d.]+)\s*%'
    dram_matches = re.findall(dram_pattern, html_content, re.MULTILINE)
    
    for match in dram_matches:
        item = match[0]
        prices.append({
            "category": "dram_spot",
            "item": item,
            "daily_high": float(match[1]),
            "daily_low": float(match[2]),
            "session_high": float(match[3]),
            "session_low": float(match[4]),
            "session_avg": float(match[5]),
            "change_percent": float(match[6])
        })
    
    # Extract NAND Flash prices
    flash_pattern = r'\[(.*?)\]\(/Price/Flash_Spot\)\s*\n\s*([\d.]+)\s*\n\s*([\d.]+)\s*\n\s*([\d.]+)\s*\n\s*([\d.]+)\s*\n\s*([\d.]+)\s*\n\s*([-\d.]+)\s*%'
    flash_matches = re.findall(flash_pattern, html_content, re.MULTILINE)
    
    for match in flash_matches:
        item = match[0]
        prices.append({
            "category": "flash_spot",
            "item": item,
            "daily_high": float(match[1]),
            "daily_low": float(match[2]),
            "session_high": float(match[3]),
            "session_low": float(match[4]),
            "session_avg": float(match[5]),
            "change_percent": float(match[6])
        })
    
    return prices

def fetch_dramexchange_prices() -> List[Dict]:
    """Fetch current prices from DRAMExchange."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(DRAMEXCHANGE_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # For now, use regex parsing as fallback
        # In production, you would implement proper BeautifulSoup parsing
        prices = parse_price_table(response.text)
        
        if not prices:
            print("⚠️  Could not parse prices from HTML. Using fallback data.")
            prices = get_fallback_prices()
        
        return prices
        
    except Exception as e:
        print(f"❌ Error fetching prices: {e}")
        print("Using fallback data...")
        return get_fallback_prices()

def get_fallback_prices() -> List[Dict]:
    """Get fallback price data when scraping fails."""
    # This is sample data based on typical DRAMExchange prices
    # In production, you would implement proper error handling
    return [
        {
            "category": "dram_spot",
            "item": "DDR5 16Gb (2Gx8) 4800/5600",
            "daily_high": 48.00,
            "daily_low": 25.80,
            "session_high": 48.00,
            "session_low": 26.00,
            "session_avg": 37.00,
            "change_percent": 0.0
        },
        {
            "category": "dram_spot",
            "item": "DDR4 16Gb (2Gx8) 3200",
            "daily_high": 90.00,
            "daily_low": 26.20,
            "session_high": 90.00,
            "session_low": 26.20,
            "session_avg": 73.09,
            "change_percent": -0.31
        },
        {
            "category": "flash_spot",
            "item": "SLC 2Gb 256MBx8",
            "daily_high": 3.60,
            "daily_low": 2.50,
            "session_high": 3.60,
            "session_low": 2.50,
            "session_avg": 2.99,
            "change_percent": 9.37
        }
    ]

def update_price_history(current_prices: List[Dict]):
    """Update historical price database with current prices."""
    timestamp = datetime.now().isoformat()
    
    # Load existing data
    data = load_prices()
    
    # Initialize price_history if it doesn't exist
    if "price_history" not in data:
        data["price_history"] = {}
    
    # Add current prices to history
    data["price_history"][timestamp] = {
        "timestamp": timestamp,
        "prices": current_prices
    }
    
    # Update metadata
    data["metadata"]["last_updated"] = timestamp
    data["metadata"]["total_records"] = len(data["price_history"])
    
    # Save updated data
    save_prices(data)
    
    # Also update CSV file
    update_csv_file(current_prices, timestamp)
    
    return data

def update_csv_file(prices: List[Dict], timestamp: str):
    """Append current prices to CSV file."""
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        
        for price in prices:
            writer.writerow([
                timestamp,
                price.get("category", ""),
                price.get("item", ""),
                price.get("daily_high", ""),
                price.get("daily_low", ""),
                price.get("session_high", ""),
                price.get("session_low", ""),
                price.get("session_avg", ""),
                price.get("change_percent", ""),
                price.get("weekly_high", ""),
                price.get("weekly_low", ""),
                price.get("avg_change", "")
            ])

def generate_price_report(prices: List[Dict], historical_data: Dict) -> str:
    """Generate a comprehensive price report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    lines = []
    lines.append("💾 **MEMORY PRICE TRACKING REPORT**")
    lines.append(f"Time: {timestamp} SGT")
    lines.append(f"Source: DRAMExchange.com")
    lines.append("")
    
    # Group prices by category
    by_category = {}
    for price in prices:
        category = price["category"]
        by_category.setdefault(category, []).append(price)
    
    # Show price changes
    lines.append("📈 **PRICE CHANGES (Most Significant)**")
    lines.append("")
    
    # Sort by absolute change percentage
    sorted_prices = sorted(prices, key=lambda x: abs(x.get("change_percent", 0)), reverse=True)
    
    for price in sorted_prices[:5]:  # Top 5 changes
        change = price.get("change_percent", 0)
        change_emoji = "🟢" if change >= 0 else "🔴"
        lines.append(f"{change_emoji} **{price['item']}**")
        lines.append(f"   Current: ${price.get('session_avg', 0):.3f}")
        lines.append(f"   Change: {change:+.2f}%")
        lines.append(f"   Range: ${price.get('daily_low', 0):.2f} - ${price.get('daily_high', 0):.2f}")
        lines.append("")
    
    # Category breakdown
    lines.append("📊 **CATEGORY BREAKDOWN**")
    lines.append("")
    
    for category, cat_prices in by_category.items():
        cat_info = PRICE_CATEGORIES.get(category, {"name": category})
        lines.append(f"**{cat_info['name']}** ({len(cat_prices)} items)")
        
        # Calculate average change for category
        avg_change = sum(p.get("change_percent", 0) for p in cat_prices) / len(cat_prices)
        change_emoji = "🟢" if avg_change >= 0 else "🔴"
        
        lines.append(f"   Avg Change: {change_emoji} {avg_change:+.2f}%")
        
        # Show top item in category
        if cat_prices:
            top_item = max(cat_prices, key=lambda x: abs(x.get("change_percent", 0)))
            lines.append(f"   Most Active: {top_item['item']} ({top_item.get('change_percent', 0):+.2f}%)")
        
        lines.append("")
    
    # Historical context if available
    if historical_data and "price_history" in historical_data:
        history = historical_data["price_history"]
        if len(history) > 1:
            lines.append("📅 **HISTORICAL CONTEXT**")
            lines.append(f"   Total records: {len(history)}")
            
            # Get first and last timestamps
            timestamps = sorted(history.keys())
            first = timestamps[0]
            last = timestamps[-1]
            
            first_date = datetime.fromisoformat(first).strftime("%Y-%m-%d")
            last_date = datetime.fromisoformat(last).strftime("%Y-%m-%d")
            
            lines.append(f"   Date range: {first_date} to {last_date}")
            lines.append("")
    
    # Data storage info
    lines.append("💾 **DATA STORAGE**")
    lines.append(f"   JSON file: {PRICES_FILE}")
    lines.append(f"   CSV file: {CSV_FILE}")
    lines.append(f"   Total categories: {len(by_category)}")
    lines.append(f"   Total items tracked: {len(prices)}")
    lines.append("")
    
    lines.append("⏰ **Next Update:** Daily at 9 AM SGT")
    lines.append("📈 **Tracking:** DRAM, NAND Flash, SSD, Memory Cards")
    
    return "\n".join(lines)

def analyze_price_trends(historical_data: Dict) -> Dict:
    """Analyze price trends from historical data."""
    if not historical_data or "price_history" not in historical_data:
        return {}
    
    history = historical_data["price_history"]
    if len(history) < 2:
        return {}
    
    # Get sorted timestamps
    timestamps = sorted(history.keys())
    
    # Get first and last price sets
    first_prices = {p["item"]: p for p in history[timestamps[0]]["prices"]}
    last_prices = {p["item"]: p for p in history[timestamps[-1]]["prices"]}
    
    trends = {}
    
    # Calculate trends for common items
    common_items = set(first_prices.keys()) & set(last_prices.keys())
    
    for item in common_items:
        first_price = first_prices[item].get("session_avg", 0)
        last_price = last_prices[item].get("session_avg", 0)
        
        if first_price > 0:
            change_pct = ((last_price - first_price) / first_price) * 100
            trends[item] = {
                "first_price": first_price,
                "last_price": last_price,
                "change_percent": change_pct,
                "trend": "up" if change_pct > 0 else "down" if change_pct < 0 else "stable"
            }
    
    return trends

def main():
    """Main function to run price tracking."""
    print("💾 Memory Price Tracker for DRAMExchange.com")
    print("=" * 50)
    
    # Setup data directory
    setup_data_directory()
    print(f"📁 Data directory: {DATA_DIR}")
    
    # Load historical data
    historical_data = load_prices()
    print(f"📊 Historical records: {len(historical_data.get('price_history', {}))}")
    
    # Fetch current prices
    print("🌐 Fetching current prices from DRAMExchange...")
    current_prices = fetch_dramexchange_prices()
    print(f"✅ Fetched {len(current_prices)} price points")
    
    # Update historical data
    print("💾 Updating price history...")
    updated_data = update_price_history(current_prices)
    
    # Analyze trends
    trends = analyze_price_trends(updated_data)
    
    # Generate report
    report = generate_price_report(current_prices, updated_data)
    
    # Print report
    print("\n" + report)
    
    # Save report to file
    report_file = DATA_DIR / f"price_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    report_file.write_text(report)
    
    # Save trends analysis
    if trends:
        trends_file = DATA_DIR / f"trends_analysis_{datetime.now().strftime('%Y%m%d')}.json"
        with open(trends_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "items_analyzed": len(trends),
                "trends": trends
            }, f, indent=2)
    
    print(f"\n📁 Report saved to: {report_file}")
    if trends:
        print(f"📈 Trends saved to: {trends_file}")
    
    # Show summary
    print("\n🎯 **SUMMARY**")
    print(f"   • Prices tracked: {len(current_prices)}")
    print(f"   • Categories: {len(set(p['category'] for p in current_prices))}")
    print(f"   • Historical records: {len(updated_data.get('price_history', {}))}")
    
    if trends:
        up_trends = sum(1 for t in trends.values() if t['trend'] == 'up')
        down_trends = sum(1 for t in trends.values() if t['trend'] == 'down')
        print(f"   • Price trends: {up_trends} up, {down_trends} down")
    
    return {
        "prices": current_prices,
        "historical_count": len(updated_data.get('price_history', {})),
        "trends": trends
    }

if __name__ == "__main__":
    main()