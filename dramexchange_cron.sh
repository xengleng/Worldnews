#!/bin/bash
# DRAMExchange Memory Price Tracker - Daily Cron Job

set -e

echo "💰 DRAMExchange Memory Price Tracker"
echo "=========================================="
echo "Time: $(TZ='Asia/Singapore' date '+%Y-%m-%d %H:%M:%S %Z')"
echo ""

# Navigate to workspace
cd /home/yeoel/.openclaw/workspace

# Check if Python script exists
if [ ! -f "dramexchange_scraper_complete.py" ]; then
    echo "❌ Error: dramexchange_scraper_complete.py not found"
    exit 1
fi

# Run the scraper
echo "🌐 Running DRAMExchange scraper..."
python3 dramexchange_scraper_complete.py

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ DRAMExchange price tracking completed successfully"
    echo ""
    echo "📊 Next steps:"
    echo "   • Check Obsidian vault for report"
    echo "   • Review memory_prices/ directory for JSON data"
    echo "   • Monitor for any scraping errors"
else
    echo ""
    echo "❌ DRAMExchange scraper failed"
    echo "   Check logs for details"
    exit 1
fi

echo ""
echo "=========================================="
echo "💰 Daily memory price tracking complete"
echo "Time: $(TZ='Asia/Singapore' date '+%Y-%m-%d %H:%M:%S %Z')"