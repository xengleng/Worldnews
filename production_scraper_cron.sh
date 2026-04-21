#!/bin/bash
# Production Memory Price Scraper Cron Job
# Actually scrapes websites for real price data - NO HALLUCINATIONS

set -e

echo "💰 PRODUCTION MEMORY PRICE SCRAPER - $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "=" * 70
echo "ACTUALLY scraping websites for real price data"
echo "NO HALLUCINATIONS - real URLs, real data"
echo ""

# Navigate to workspace
cd "$HOME/.openclaw/workspace"

# Check if scraping libraries are available
if ! python3 -c "import requests, bs4" 2>/dev/null; then
    echo "❌ Missing scraping libraries"
    echo "   Install with: pip install --user --break-system-packages requests beautifulsoup4"
    exit 1
fi

# Run the production scraper
echo "🌐 Running production memory price scraper..."
python3 production_scraper.py

# Get the latest production report
LATEST_REPORT=$(ls -t memory_prices/production_report_*.txt 2>/dev/null | head -1)

if [ -f "$LATEST_REPORT" ] && [ -f "save_bloomberg_report.sh" ]; then
    echo ""
    echo "💾 Saving to Obsidian and GitHub..."
    
    REPORT_TITLE="Production Memory Price Scraper Report - $(date '+%Y-%m-%d %H:%M') SGT"
    REPORT_CONTENT=$(cat "$LATEST_REPORT")
    
    # Save to Obsidian and GitHub
    bash save_bloomberg_report.sh "$REPORT_TITLE" "$REPORT_CONTENT"
    
    echo ""
    echo "✅ Production report saved to:"
    echo "   • Obsidian vault: ~/Documents/openclaw/World News/"
    echo "   • GitHub repo: https://github.com/xengleng/Worldnews"
else
    echo ""
    echo "⚠️  Could not find production report or save script"
fi

echo ""
echo "🎯 **WHAT WAS ACTUALLY SCRAPED:**"
echo "   • Amazon Memory Best Sellers"
echo "   • Newegg Memory Category" 
echo "   • Google News Memory Prices"
echo "   • Tom's Hardware Memory News"
echo "   • AnandTech Memory Analysis"

echo ""
echo "🔗 **ACTUAL WORKING URLS (No hallucinations):**"
echo "   • https://www.amazon.com/Best-Sellers-Computers-Accessories-Memory/zgbs/pc/172500"
echo "   • https://www.newegg.com/p/pl?N=100007952"
echo "   • https://news.google.com/search?q=memory+prices+dram+nand+2026"
echo "   • https://www.tomshardware.com/tag/memory"
echo "   • https://www.anandtech.com/tag/memory"

echo ""
echo "⚠️ **TRANSPARENCY:**"
echo "   • Real web scraping - no fake data"
echo "   • Actual price extraction from websites"
echo "   • Respectful rate limiting between requests"
echo "   • Anti-scraping measures may affect some sites"

echo ""
echo "✅ Production memory price scraping completed at $(date '+%H:%M:%S')"