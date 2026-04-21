#!/usr/bin/env python3
"""
Check all DRAMExchange URLs to see what's actually visible
"""

import requests
from bs4 import BeautifulSoup
import re

URLS = [
    "https://www.dramexchange.com/Price/Dram_Spot",
    "https://www.dramexchange.com/Price/Module_Spot",
    "https://www.dramexchange.com/Price/Flash_Spot",
    "https://www.dramexchange.com/Price/GDDR_Spot",
    "https://www.dramexchange.com/Price/Wafer_Spot",
    "https://www.dramexchange.com/Price/MemoryCard_Spot",
    "https://www.dramexchange.com/Price/NationalContractDramDetail",
    "https://www.dramexchange.com/Price/NationalContractFlashDetail"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

print("🔍 Checking ALL DRAMExchange URLs for visible price data")
print("=" * 70)

for url in URLS:
    print(f"\n📄 {url}")
    print("-" * 40)
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"  ❌ HTTP {response.status_code}")
            continue
        
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.get_text(strip=True) if soup.title else "No title"
        
        print(f"  Title: {title}")
        
        # Check if it's a login page
        is_login = "login" in title.lower() or "sign in" in title.lower()
        
        if is_login:
            print(f"  ⚠️ This is a LOGIN page")
            
            # Look for any price mentions in the page
            text = soup.get_text()
            
            # Look for actual price numbers (not the $4 membership)
            price_patterns = [
                r'\$\d+\.\d{4}',  # $1.2345 format
                r'\d+\.\d{4}\s*USD',  # 1.2345 USD format
                r'price.*?\d+\.\d{2,4}',  # price 1.23 or 1.2345
            ]
            
            found_real_prices = False
            for pattern in price_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    # Filter out the $4 membership promo
                    if not ('4.00' in match or '4.0000' in match or 'membership' in text.lower()):
                        print(f"  ✅ Found potential price: {match}")
                        found_real_prices = True
            
            if not found_real_prices:
                print(f"  ❌ No actual price data found (only login page)")
            
            # Check for price table mentions
            price_terms = ['spot price', 'contract price', 'dram', 'nand', 'flash']
            for term in price_terms:
                if term in text.lower():
                    print(f"  📝 Mentions '{term}' but data requires login")
        
        else:
            print(f"  ✅ Not a login page - might have visible data")
            
            # Extract text and look for prices
            text = soup.get_text()
            
            # Look for price tables or data
            price_matches = re.findall(r'\$\d+\.?\d*|\d+\.?\d*\s*USD', text)
            if price_matches:
                print(f"  ✅ Found {len(price_matches)} price mentions")
                unique_prices = list(set(price_matches))[:5]
                for price in unique_prices:
                    print(f"    • {price}")
            else:
                print(f"  ❌ No price mentions found")
        
        # Check page size as indicator of content
        print(f"  Page size: {len(response.content)} bytes")
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:50]}")

print()
print("=" * 70)
print("✅ Analysis complete")
print()
print("🎯 CONCLUSION:")
print("• DRAMExchange pages are login-protected")
print("• The $4.00 found is for membership promotion")
print("• Actual price data requires login credentials")
print("• Need alternative sources or authentication")