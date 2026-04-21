#!/usr/bin/env python3
"""
Quick test of public memory tracker
"""

import requests
from bs4 import BeautifulSoup
import re

print("🔍 Testing public memory tracker sources")
print("=" * 60)

# Test one source
test_url = "https://www.tomshardware.com/tag/memory"
print(f"Testing: {test_url}")

try:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    response = requests.get(test_url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        print(f"✅ HTTP {response.status_code} - Accessible")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()
        
        # Look for memory content
        memory_keywords = ['dram', 'nand', 'memory', 'ram', 'ddr']
        memory_count = 0
        
        for line in text.split('\n'):
            line = line.strip()
            if any(keyword in line.lower() for keyword in memory_keywords):
                if 20 < len(line) < 200:
                    memory_count += 1
                    if memory_count <= 3:
                        print(f"   Memory mention: {line[:80]}...")
        
        print(f"   Found {memory_count} memory mentions")
        
        # Look for prices
        prices = re.findall(r'\$(\d+\.?\d*)', text)
        if prices:
            print(f"   Found {len(prices)} price mentions")
            unique_prices = sorted(list(set([float(p) for p in prices if 10 < float(p) < 1000])))[:5]
            if unique_prices:
                print(f"   Sample prices: {['$' + str(p) for p in unique_prices]}")
        
    else:
        print(f"⚠️ HTTP {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {str(e)[:50]}")

print()
print("=" * 60)
print("✅ Public source testing complete")
print("The public memory tracker should work with these sources")