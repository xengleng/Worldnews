#!/usr/bin/env python3
"""
Test DRAMExchange URLs for accessibility
"""

import requests
from datetime import datetime

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

print("🔍 Testing DRAMExchange URL Accessibility")
print("=" * 60)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} SGT")
print()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

for url in URLS:
    print(f"Testing: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"  ✅ HTTP {response.status_code} - Accessible")
            print(f"  Content-Type: {response.headers.get('content-type', 'N/A')}")
            print(f"  Size: {len(response.content)} bytes")
            
            # Check if it looks like a price page
            content_preview = response.text[:200].replace('\n', ' ').strip()
            print(f"  Preview: {content_preview}...")
        else:
            print(f"  ⚠️ HTTP {response.status_code} - May require login or have restrictions")
        
    except requests.exceptions.Timeout:
        print(f"  ❌ Timeout - Site may be slow or blocking")
    except requests.exceptions.ConnectionError:
        print(f"  ❌ Connection Error - Cannot reach site")
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:50]}")
    
    print()

print("=" * 60)
print("✅ URL testing complete")
print(f"Total URLs tested: {len(URLS)}")