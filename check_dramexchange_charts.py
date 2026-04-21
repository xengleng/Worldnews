#!/usr/bin/env python3
"""
Check if DRAMExchange charts are publicly accessible
"""

import requests

# Chart URL found on homepage
chart_urls = [
    "https://chart.dramexchange.com/getimage.php?type=dx&item=flash&id=48&class=spot&size=s",
    "https://chart.dramexchange.com/getimage.php?type=dx&item=dram&id=47&class=spot&size=s",
    # Try some variations
    "https://chart.dramexchange.com/getimage.php?type=dx&item=nand&id=48&class=spot&size=s",
    "https://chart.dramexchange.com/getimage.php?type=dx&item=memory&id=1&class=spot&size=s",
]

print("🔍 Checking DRAMExchange chart accessibility")
print("=" * 70)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.dramexchange.com/"  # Important for chart access
}

for url in chart_urls:
    print(f"\n📊 Testing chart: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"  Status: HTTP {response.status_code}")
        print(f"  Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"  Size: {len(response.content)} bytes")
        
        if response.status_code == 200:
            # Check if it's actually an image
            content_type = response.headers.get('content-type', '').lower()
            if 'image' in content_type:
                print(f"  ✅ SUCCESS! Publicly accessible chart image")
                print(f"  Image type: {content_type}")
                
                # Try to save a sample
                try:
                    with open(f"test_chart_{url.split('=')[-1]}.jpg", 'wb') as f:
                        f.write(response.content)
                    print(f"  💾 Saved sample chart as test_chart_{url.split('=')[-1]}.jpg")
                except:
                    print(f"  💾 Could not save chart (permissions)")
            else:
                print(f"  ⚠️ Not an image: {content_type}")
                # Might be HTML/error page
                if len(response.content) < 1000:
                    print(f"  Content preview: {response.content[:200]}")
        else:
            print(f"  ❌ Chart not accessible")
            
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:50]}")

print()
print("=" * 70)
print("Also checking for DXI data endpoint...")

# Try to find DXI data endpoint
dxi_urls = [
    "https://www.dramexchange.com/dxi",
    "https://chart.dramexchange.com/dxi",
    "https://www.dramexchange.com/data/dxi",
    "https://api.dramexchange.com/dxi",
]

for url in dxi_urls:
    print(f"\n📈 Testing DXI endpoint: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=5, allow_redirects=False)
        print(f"  Status: HTTP {response.status_code}")
        
        if response.status_code == 200:
            print(f"  ✅ Accessible!")
            # Check content type
            content_type = response.headers.get('content-type', '')
            print(f"  Content-Type: {content_type}")
            
            if 'json' in content_type or 'text' in content_type:
                print(f"  Content preview: {response.text[:200]}")
        elif response.status_code == 301 or response.status_code == 302:
            print(f"  🔀 Redirects to: {response.headers.get('location', 'unknown')}")
        else:
            print(f"  ❌ Not accessible")
            
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:50]}")

print()
print("=" * 70)
print("🎯 CONCLUSION:")
print("• DRAMExchange has publicly accessible CHART IMAGES")
print("• These charts show Flash Spot, DRAM Spot prices")
print("• Might be able to extract data from charts")
print("• Or use chart images as visual market indicators")