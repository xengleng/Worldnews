#!/usr/bin/env python3
"""
Check what's actually on DRAMExchange pages
"""

import requests
from bs4 import BeautifulSoup
import re

url = "https://www.dramexchange.com/Price/Dram_Spot"

print(f"🔍 Checking DRAMExchange page: {url}")
print("=" * 70)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

try:
    response = requests.get(url, headers=headers, timeout=15)
    
    print(f"Status: HTTP {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
    print(f"Size: {len(response.content)} bytes")
    print()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Get page title
    title = soup.title.get_text(strip=True) if soup.title else "No title"
    print(f"Page Title: {title}")
    print()
    
    # Check for login forms
    login_forms = soup.find_all('form')
    login_inputs = soup.find_all('input', {'type': ['text', 'password', 'email']})
    
    print(f"Forms found: {len(login_forms)}")
    print(f"Input fields (possible login): {len(login_inputs)}")
    print()
    
    # Get first 2000 characters of text
    text = soup.get_text()
    print("First 1000 characters of page text:")
    print("-" * 70)
    print(text[:1000])
    print("-" * 70)
    print()
    
    # Look for specific patterns
    print("Looking for specific patterns:")
    print("-" * 70)
    
    # Look for USD or $ signs
    usd_matches = re.findall(r'USD|\$', text[:2000])
    print(f"USD/$ mentions in first 2000 chars: {len(usd_matches)}")
    
    # Look for numbers (potential prices)
    number_patterns = [
        r'\$\d+\.\d{4}',  # $1.2345 (4 decimal places common for memory)
        r'\$\d+\.\d{2}',  # $1.23 (2 decimal places)
        r'\d+\.\d{4}\s*USD',  # 1.2345 USD
        r'price.*?\d+\.?\d*',  # price 1.23
    ]
    
    for pattern in number_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            print(f"Pattern '{pattern}': {len(matches)} matches")
            for match in matches[:5]:  # Show first 5
                print(f"  • {match}")
    
    print()
    
    # Look for memory-related terms
    memory_terms = ['dram', 'ddr', 'nand', 'flash', 'memory', 'module', 'wafer', 'gddr']
    for term in memory_terms:
        count = text.lower().count(term)
        if count > 0:
            print(f"'{term}' appears {count} times")
    
    print()
    
    # Check for tables (common for price data)
    tables = soup.find_all('table')
    print(f"Tables found: {len(tables)}")
    
    if tables:
        print("First table structure:")
        first_table = tables[0]
        rows = first_table.find_all('tr')
        print(f"  Rows: {len(rows)}")
        if rows:
            cells = rows[0].find_all(['td', 'th'])
            print(f"  Cells in first row: {len(cells)}")
            for i, cell in enumerate(cells[:5]):
                print(f"    Cell {i}: {cell.get_text(strip=True)[:50]}")
    
    print()
    print("=" * 70)
    print("Analysis complete")
    
except Exception as e:
    print(f"Error: {e}")