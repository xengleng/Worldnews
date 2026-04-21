#!/usr/bin/env python3
"""
Check DRAMExchange homepage for price data
"""

import requests
from bs4 import BeautifulSoup
import re

url = "https://www.dramexchange.com/"

print(f"🔍 Checking DRAMExchange homepage: {url}")
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
    
    # Check if it's a login page
    is_login = "login" in title.lower() or "sign in" in title.lower()
    
    if is_login:
        print("⚠️ Homepage is ALSO a login page!")
        print()
        
        # Extract text
        text = soup.get_text()
        
        # Look for any price data or indicators
        print("Looking for price data on homepage:")
        print("-" * 40)
        
        # Check for price mentions
        price_terms = ['price', 'dram', 'nand', 'flash', 'memory', 'spot', 'contract']
        found_any = False
        
        for term in price_terms:
            if term in text.lower():
                print(f"✓ Mentions '{term}'")
                found_any = True
        
        if not found_any:
            print("❌ No price-related terms found")
        
        # Look for actual price numbers
        price_patterns = [
            r'\$\d+\.\d{4}',  # $1.2345
            r'\$\d+\.\d{2}',  # $1.23
            r'\d+\.\d{4}\s*USD',  # 1.2345 USD
        ]
        
        found_prices = False
        for pattern in price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                print(f"✓ Found price pattern '{pattern}': {len(matches)} matches")
                for match in matches[:3]:  # Show first 3
                    print(f"  • {match}")
                found_prices = True
        
        if not found_prices:
            print("❌ No actual price numbers found")
        
        print()
        print("Checking for free/public data sections:")
        print("-" * 40)
        
        # Look for any free data, market indicators, or public charts
        free_terms = ['free', 'public', 'chart', 'graph', 'indicator', 'index', 'trend']
        for term in free_terms:
            if term in text.lower():
                print(f"✓ Mentions '{term}' - might have public data")
        
        # Check for DXI (DRAMeXchange Index) - sometimes publicly available
        if 'DXI' in text or 'dxi' in text.lower():
            print("✓ Mentions 'DXI' (DRAMeXchange Index) - might be public")
        
    else:
        print("✅ Homepage is NOT a login page!")
        print()
        
        # Extract text and look for prices
        text = soup.get_text()
        
        print("Searching for price data on homepage:")
        print("-" * 40)
        
        # Look for price tables or data
        price_matches = re.findall(r'\$\d+\.?\d*|\d+\.?\d*\s*USD', text)
        if price_matches:
            print(f"✅ Found {len(price_matches)} price mentions")
            unique_prices = list(set(price_matches))[:10]
            for price in unique_prices:
                print(f"  • {price}")
        else:
            print("❌ No price mentions found")
        
        # Look for memory market data
        memory_terms = ['dram', 'nand', 'flash', 'memory', 'ddr', 'ssd']
        for term in memory_terms:
            count = text.lower().count(term)
            if count > 0:
                print(f"📝 '{term}' appears {count} times")
        
        # Check for charts/graphs
        img_tags = soup.find_all('img')
        chart_imgs = [img for img in img_tags if 'chart' in img.get('src', '').lower() or 'graph' in img.get('src', '').lower()]
        if chart_imgs:
            print(f"📊 Found {len(chart_imgs)} chart/graph images")
    
    print()
    print("=" * 70)
    print("Analysis complete")
    
    if is_login:
        print()
        print("🎯 CONCLUSION:")
        print("• DRAMExchange homepage ALSO requires login")
        print("• Entire site appears to be behind login wall")
        print("• Need to use alternative public sources for memory prices")
    
except Exception as e:
    print(f"Error: {e}")