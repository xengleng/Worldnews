#!/bin/bash
# Memory Price Tracking Cron Job
# Runs daily at 9 AM SGT to track DRAM/NAND flash prices

set -e

echo "💾 Memory Price Tracking - $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "=" * 50

# Navigate to workspace
cd "$HOME/.openclaw/workspace"

# Run the price tracker
python3 simple_memory_tracker.py

# Check if we should also update Obsidian/GitHub
if [ -f "save_bloomberg_report.sh" ]; then
    echo ""
    echo "💾 Saving to Obsidian and GitHub..."
    
    # Get the latest report
    LATEST_REPORT=$(ls -t memory_prices/price_report_*.txt | head -1)
    
    if [ -f "$LATEST_REPORT" ]; then
        REPORT_TITLE="Memory Price Report - $(date '+%Y-%m-%d %H:%M') SGT"
        REPORT_CONTENT=$(cat "$LATEST_REPORT")
        
        # Save to Obsidian and GitHub
        bash save_bloomberg_report.sh "$REPORT_TITLE" "$REPORT_CONTENT"
    fi
fi

echo ""
echo "✅ Memory price tracking completed at $(date '+%H:%M:%S')"