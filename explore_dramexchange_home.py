#!/usr/bin/env python3
"""
Explore DRAMExchange homepage for any public data
"""

import requests
from bs4 import BeautifulSoup
import re

url = "https://www.dramexchange.com/"

print(f"🔍 Exploring DRAMExchange homepage for public data")
print("=" * 70)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

try:
    response = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Get all text
    text = soup.get_text()
    
    # Look for specific sections that might have public data
    print("Looking for potential public data sections:")
    print("-" * 40)
    
    # Check for DXI (DRAMeXchange Index)
    dxi_patterns = [r'DXI.*?\d+\.?\d*', r'DRAMeXchange.*?Index.*?\d+\.?\d*', r'index.*?\d+\.?\d*']
    for pattern in dxi_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        if matches:
            print(f"✅ Found DXI/Index mention:")
            for match in matches[:2]:
                print(f"  • {match[:100]}...")
    
    # Look for market indicators
    indicator_terms = ['market indicator', 'price indicator', 'trend', 'index', 'benchmark']
    for term in indicator_terms:
        if term in text.lower():
            # Get context around the term
            idx = text.lower().find(term)
            if idx != -1:
                context = text[max(0, idx-50):min(len(text), idx+100)]
                print(f"✅ Found '{term}' mention:")
                print(f"  • {context}")
    
    # Look for any numbers that could be market data
    print()
    print("Looking for numerical market data:")
    print("-" * 40)
    
    # Look for percentage changes (common in market data)
    changes = re.findall(r'[+-]\d+\.?\d*%', text)
    if changes:
        print(f"✅ Found {len(changes)} percentage changes:")
        for change in changes[:5]:
            print(f"  • {change}")
    
    # Look for numbers with 2-4 decimal places (could be prices)
    precise_numbers = re.findall(r'\b\d+\.\d{2,4}\b', text)
    if precise_numbers:
        print(f"✅ Found {len(precise_numbers)} precise numbers (possible prices):")
        for num in precise_numbers[:5]:
            print(f"  • {num}")
    
    # Check for any tables with data
    tables = soup.find_all('table')
    print()
    print(f"Tables found: {len(tables)}")
    
    if tables:
        for i, table in enumerate(tables[:3]):  # Check first 3 tables
            rows = table.find_all('tr')
            print(f"  Table {i+1}: {len(rows)} rows")
            
            # Check if table has numerical data
            has_numbers = False
            for row in rows[:2]:  # Check first 2 rows
                cells = row.find_all(['td', 'th'])
                for cell in cells:
                    cell_text = cell.get_text(strip=True)
                    if re.search(r'\d', cell_text):  # Has numbers
                        has_numbers = True
                        print(f"    • Cell with numbers: {cell_text[:50]}")
            
            if not has_numbers:
                print(f"    • No numerical data found")
    
    # Look for charts or graphs
    print()
    print("Looking for charts/graphs:")
    print("-" * 40)
    
    # Check images
    images = soup.find_all('img')
    chart_images = []
    for img in images:
        src = img.get('src', '').lower()
        alt = img.get('alt', '').lower()
        if any(term in src or term in alt for term in ['chart', 'graph', 'trend', 'price', 'index']):
            chart_images.append(img)
    
    print(f"Found {len(chart_images)} potential chart images")
    for img in chart_images[:3]:
        src = img.get('src', '')[:100]
        alt = img.get('alt', '')[:100]
        print(f"  • src: {src}")
        print(f"    alt: {alt}")
    
    # Check for iframes (embedded content)
    iframes = soup.find_all('iframe')
    print(f"Found {len(iframes)} iframes (possible embedded charts)")
    
    # Look for JavaScript data (might have embedded charts)
    scripts = soup.find_all('script')
    data_scripts = []
    for script in scripts:
        script_text = script.get_text()
        if any(term in script_text.lower() for term in ['chart', 'graph', 'data', 'series', 'point']):
            data_scripts.append(script)
    
    print(f"Found {len(data_scripts)} scripts with chart/data keywords")
    
    print()
    print("=" * 70)
    print("Summary:")
    print(f"• Homepage accessible without login")
    print(f"• Mentions DRAM, NAND, Flash many times")
    print(f"• Has {len(tables)} tables")
    print(f"• Has {len(chart_images)} potential chart images")
    print(f"• Has {len(changes)} percentage changes")
    print(f"• Has {len(precise_numbers)} precise numbers")
    
    if changes or precise_numbers:
        print("✅ POTENTIAL PUBLIC DATA FOUND!")
        print("   The homepage might have some public market indicators")
    else:
        print("❌ No obvious public price data found")
        print("   Might need to look for specific public indices or charts")
    
except Exception as e:
    print(f"Error: {e}")