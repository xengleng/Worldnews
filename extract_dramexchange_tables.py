#!/usr/bin/env python3
"""
Extract price tables from DRAMExchange homepage
Look for tables with price data that are visible without login
"""

import requests
from bs4 import BeautifulSoup
import re

url = "https://www.dramexchange.com/"

print(f"🔍 Extracting price tables from DRAMExchange homepage")
print("=" * 70)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

try:
    response = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print(f"Status: HTTP {response.status_code}")
    print(f"Page size: {len(response.content):,} bytes")
    print()
    
    # Find ALL tables on the page
    tables = soup.find_all('table')
    print(f"Total tables found: {len(tables)}")
    print()
    
    # Look for tables that might contain price data
    price_tables = []
    
    for i, table in enumerate(tables):
        # Get table text content
        table_text = table.get_text(strip=True)
        
        # Check if table contains price-related keywords
        price_keywords = ['price', 'dram', 'nand', 'flash', 'memory', 'spot', 'contract', 'usd', '$']
        has_price_keywords = any(keyword in table_text.lower() for keyword in price_keywords)
        
        # Check if table contains numbers (potential prices)
        has_numbers = bool(re.search(r'\d+\.?\d*', table_text))
        
        # Check if table has a reasonable structure (multiple rows/cells)
        rows = table.find_all('tr')
        cells = table.find_all(['td', 'th'])
        
        if (has_price_keywords and has_numbers) or (len(rows) > 2 and len(cells) > 4):
            price_tables.append({
                "index": i,
                "rows": len(rows),
                "cells": len(cells),
                "has_price_keywords": has_price_keywords,
                "has_numbers": has_numbers,
                "preview": table_text[:200]
            })
    
    print(f"Potential price tables found: {len(price_tables)}")
    print()
    
    # Examine each potential price table in detail
    for table_info in price_tables[:10]:  # Check first 10
        print(f"📊 Table {table_info['index'] + 1}:")
        print(f"  Rows: {table_info['rows']}, Cells: {table_info['cells']}")
        print(f"  Has price keywords: {table_info['has_price_keywords']}")
        print(f"  Has numbers: {table_info['has_numbers']}")
        print(f"  Preview: {table_info['preview']}")
        print()
        
        # Get the actual table
        table = tables[table_info['index']]
        
        # Extract table data
        print("  Table structure:")
        rows = table.find_all('tr')
        for row_idx, row in enumerate(rows[:5]):  # First 5 rows
            cells = row.find_all(['td', 'th'])
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            
            if cell_texts:  # Only show rows with content
                print(f"    Row {row_idx + 1}: {cell_texts}")
        
        print()
    
    # Also look for specific price patterns in the entire page
    print("=" * 70)
    print("🔍 Searching for specific price patterns in page text:")
    print("-" * 40)
    
    all_text = soup.get_text()
    
    # Look for price patterns like: $1.23, 1.23 USD, etc.
    price_patterns = [
        r'\$\s*(\d+\.?\d*)',  # $1.23
        r'(\d+\.?\d*)\s*USD',  # 1.23 USD
        r'USD\s*(\d+\.?\d*)',  # USD 1.23
        r'price.*?(\d+\.?\d*)',  # price 1.23
        r'(\d+\.\d{4})',  # 1.2345 (4 decimal places common for memory)
    ]
    
    all_prices = []
    for pattern in price_patterns:
        matches = re.findall(pattern, all_text, re.IGNORECASE)
        for match in matches:
            try:
                price = float(match)
                # Filter for reasonable memory prices
                if 0.01 < price < 1000:
                    all_prices.append(price)
            except ValueError:
                continue
    
    print(f"Found {len(all_prices)} price mentions in page text")
    if all_prices:
        unique_prices = sorted(list(set(all_prices)))
        print(f"Unique prices: {len(unique_prices)}")
        print("Sample prices:")
        for price in unique_prices[:10]:
            print(f"  • ${price:.4f}")
    
    print()
    print("=" * 70)
    print("🎯 STRATEGY:")
    print("1. Identify which tables contain price data")
    print("2. Extract structured data from those tables")
    print("3. Parse price numbers and their categories")
    print("4. Create organized price report")
    
except Exception as e:
    print(f"Error: {e}")