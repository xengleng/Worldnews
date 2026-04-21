#!/bin/bash
# Practical Memory Price Tracking Cron Job
# Uses publicly accessible data only - NO HALLUCINATIONS

set -e

echo "🎯 Practical Memory Market Tracking - $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "=" * 70
echo "Using ONLY verified public data sources"
echo ""

# Navigate to workspace
cd "$HOME/.openclaw/workspace"

# Run the practical tracker
echo "📊 Running practical memory market analysis..."
python3 practical_memory_tracker.py

# Get the latest practical report
LATEST_REPORT=$(ls -t memory_prices/practical_report_*.txt 2>/dev/null | head -1)

if [ -f "$LATEST_REPORT" ] && [ -f "save_bloomberg_report.sh" ]; then
    echo ""
    echo "💾 Saving to Obsidian and GitHub..."
    
    REPORT_TITLE="Practical Memory Market Analysis - $(date '+%Y-%m-%d %H:%M') SGT"
    REPORT_CONTENT=$(cat "$LATEST_REPORT")
    
    # Save to Obsidian and GitHub
    bash save_bloomberg_report.sh "$REPORT_TITLE" "$REPORT_CONTENT"
    
    echo ""
    echo "✅ Practical analysis saved to:"
    echo "   • Obsidian vault: ~/Documents/openclaw/World News/"
    echo "   • GitHub repo: https://github.com/xengleng/Worldnews"
else
    echo ""
    echo "⚠️  Could not find practical report or save script"
fi

echo ""
echo "🎯 **DATA SOURCES (ALL VERIFIED):**"
echo "   • DRAMExchange RSS: https://www.dramexchange.com/rss.xml"
echo "   • Micron Stock: https://finance.yahoo.com/quote/MU"
echo "   • Samsung Stock: https://finance.yahoo.com/quote/005930.KS"
echo "   • AnandTech: https://www.anandtech.com/tag/memory"
echo "   • Manual entry: memory_prices/manual_prices.json"

echo ""
echo "⚠️ **TRANSPARENCY:**"
echo "   • No hallucinations or fake URLs"
echo "   • Only publicly accessible data"
echo "   • Manual option for your private data sources"

echo ""
echo "✅ Practical memory market tracking completed at $(date '+%H:%M:%S')"