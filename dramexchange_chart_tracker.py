#!/usr/bin/env python3
"""
DRAMExchange Chart Tracker
Downloads publicly accessible chart images from DRAMExchange
Shows visual price trends even without login
"""

import requests
from datetime import datetime
from pathlib import Path
import sys

DATA_DIR = Path(__file__).parent / "memory_prices"
CHARTS_DIR = DATA_DIR / "dramexchange_charts"

# Publicly accessible DRAMExchange charts
DRAMEXCHANGE_CHARTS = [
    {
        "name": "DRAM Spot Price Chart",
        "url": "https://chart.dramexchange.com/getimage.php?type=dx&item=dram&id=47&class=spot&size=s",
        "category": "dram_spot",
        "description": "DRAM spot price trend chart"
    },
    {
        "name": "Flash Spot Price Chart", 
        "url": "https://chart.dramexchange.com/getimage.php?type=dx&item=flash&id=48&class=spot&size=s",
        "category": "flash_spot",
        "description": "NAND Flash spot price trend chart"
    },
    {
        "name": "DRAM Contract Price Chart",
        "url": "https://chart.dramexchange.com/getimage.php?type=dx&item=dram&id=47&class=contract&size=s",
        "category": "dram_contract",
        "description": "DRAM contract price trend chart"
    },
    {
        "name": "Flash Contract Price Chart",
        "url": "https://chart.dramexchange.com/getimage.php?type=dx&item=flash&id=48&class=contract&size=s",
        "category": "flash_contract",
        "description": "NAND Flash contract price trend chart"
    }
]

def download_chart(chart_info):
    """Download a chart image from DRAMExchange."""
    name = chart_info["name"]
    url = chart_info["url"]
    category = chart_info["category"]
    
    print(f"   • {name}: {url}")
    
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
                "error": f"HTTP {response.status_code}",
                "scraped_at": datetime.now().isoformat()
            }
        
        # Check if it's actually an image
        content_type = response.headers.get('content-type', '').lower()
        if 'image' not in content_type:
            return {
                "success": False,
                "name": name,
                "url": url,
                "category": category,
                "error": f"Not an image: {content_type}",
                "scraped_at": datetime.now().isoformat()
            }
        
        # Save the chart image
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
            "size_bytes": len(response.content),
            "content_type": content_type,
            "scraped_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "name": name,
            "url": url,
            "category": category,
            "error": str(e),
            "scraped_at": datetime.now().isoformat()
        }

def generate_chart_report(results):
    """Generate report about downloaded charts."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    lines = []
    lines.append("📊 **DRAMEXCHANGE CHART REPORT**")
    lines.append(f"Time: {timestamp} SGT")
    lines.append("")
    lines.append("## 📈 **PUBLICLY ACCESSIBLE CHARTS**")
    lines.append("")
    lines.append("DRAMExchange provides public chart images showing price trends")
    lines.append("These charts are accessible without login")
    lines.append("")
    
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    if successful:
        lines.append(f"✅ **Successfully downloaded: {len(successful)}/{len(results)} charts**")
        lines.append("")
        
        for result in successful:
            lines.append(f"### {result['name']}")
            lines.append(f"**Category:** {result['category']}")
            lines.append(f"**URL:** {result['url']}")
            lines.append(f"**Saved as:** {result['filename']}")
            lines.append(f"**File size:** {result['size_bytes']:,} bytes")
            lines.append(f"**Content type:** {result['content_type']}")
            lines.append("")
    else:
        lines.append("⚠️ **No charts successfully downloaded**")
        lines.append("")
    
    if failed:
        lines.append("## ❌ **FAILED DOWNLOADS**")
        lines.append("")
        for result in failed:
            lines.append(f"• {result['name']}: {result.get('error', 'Unknown error')}")
        lines.append("")
    
    lines.append("## 🔍 **HOW TO USE THESE CHARTS**")
    lines.append("")
    lines.append("1. **Visual trend analysis** - See price direction (up/down)")
    lines.append("2. **Historical comparison** - Compare with previous days' charts")
    lines.append("3. **Market sentiment** - Visual indicators of market movement")
    lines.append("4. **Chart patterns** - Identify support/resistance levels visually")
    lines.append("")
    lines.append("## ⚠️ **LIMITATIONS**")
    lines.append("")
    lines.append("• **Images only** - No raw numerical data")
    lines.append("• **Visual analysis** - Requires manual interpretation")
    lines.append("• **No exact prices** - Shows trends, not precise values")
    lines.append("• **Chart size** - Small images (s size parameter)")
    lines.append("")
    lines.append("## 🔗 **CHART URLS**")
    lines.append("")
    for chart in DRAMEXCHANGE_CHARTS:
        lines.append(f"• {chart['url']}")
    
    lines.append("")
    lines.append("---")
    lines.append("Generated: DRAMExchange Chart Tracker")
    lines.append(f"Timestamp: {datetime.now().isoformat()}")
    lines.append(f"Charts saved to: {CHARTS_DIR}")
    
    return "\n".join(lines)

def main():
    """Main chart tracker."""
    print("📊 DRAMExchange Chart Tracker")
    print("=" * 60)
    print("Downloading publicly accessible chart images")
    print("Shows visual price trends without login")
    print("")
    
    # Create directories
    DATA_DIR.mkdir(exist_ok=True)
    CHARTS_DIR.mkdir(exist_ok=True)
    
    # Download charts
    print("🌐 Downloading DRAMExchange charts...")
    results = []
    
    for chart in DRAMEXCHANGE_CHARTS:
        result = download_chart(chart)
        results.append(result)
        
        if result["success"]:
            print(f"     ✅ Downloaded {result['filename']} ({result['size_bytes']:,} bytes)")
        else:
            print(f"     ❌ Failed: {result.get('error', 'Unknown')}")
    
    # Generate report
    report = generate_chart_report(results)
    
    # Print summary
    print("\n" + "=" * 60)
    successful = [r for r in results if r["success"]]
    print(f"📊 Summary: {len(successful)}/{len(results)} charts downloaded")
    print(f"💾 Saved to: {CHARTS_DIR}")
    print("=" * 60)
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    report_file = DATA_DIR / f"dramexchange_chart_report_{timestamp}.txt"
    report_file.write_text(report)
    
    print(f"\n📄 Report saved to: {report_file}")
    
    # Save to Obsidian
    try:
        obsidian_dir = Path.home() / "Documents" / "openclaw" / "World News"
        obsidian_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{datetime.now().strftime('%Y-%m-%d')}_DRAMExchange_Charts_-_{timestamp}_SGT.md"
        filepath = obsidian_dir / filename
        filepath.write_text(report)
        print(f"📁 Report saved to Obsidian: {filepath}")
    except Exception as e:
        print(f"❌ Failed to save to Obsidian: {e}")
    
    # Summary
    print("\n✅ **DRAMEXCHANGE CHART TRACKER COMPLETE:**")
    print(f"   • Charts attempted: {len(results)}")
    print(f"   • Successful: {len(successful)}")
    print(f"   • Chart directory: {CHARTS_DIR}")
    
    if successful:
        print("\n📈 **DOWNLOADED CHARTS:**")
        for result in successful:
            print(f"   • {result['name']}: {result['filename']}")

if __name__ == "__main__":
    main()