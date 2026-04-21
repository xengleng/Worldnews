#!/bin/bash
# Enhanced Memory Price Tracking Cron Job
# Runs daily at 9 AM SGT with market news analysis

set -e

echo "💾 Enhanced Memory Price Analysis - $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "=" * 70

# Navigate to workspace
cd "$HOME/.openclaw/workspace"

# Run the enhanced price tracker
echo "📊 Running enhanced memory price analysis..."
python3 enhanced_memory_tracker.py

# Get the latest enhanced report
LATEST_REPORT=$(ls -t memory_prices/enhanced_analysis_*.txt 2>/dev/null | head -1)

if [ -f "$LATEST_REPORT" ] && [ -f "save_bloomberg_report.sh" ]; then
    echo ""
    echo "💾 Saving to Obsidian and GitHub..."
    
    REPORT_TITLE="Enhanced Memory Price Analysis - $(date '+%Y-%m-%d %H:%M') SGT"
    REPORT_CONTENT=$(cat "$LATEST_REPORT")
    
    # Save to Obsidian and GitHub
    bash save_bloomberg_report.sh "$REPORT_TITLE" "$REPORT_CONTENT"
    
    echo ""
    echo "✅ Enhanced analysis saved to:"
    echo "   • Obsidian vault: ~/Documents/openclaw/World News/"
    echo "   • GitHub repo: https://github.com/xengleng/Worldnews"
else
    echo ""
    echo "⚠️  Could not find enhanced report or save script"
    echo "   Report: $LATEST_REPORT"
    echo "   Save script: $(ls save_bloomberg_report.sh 2>/dev/null || echo 'Not found')"
fi

echo ""
echo "🎯 **ANALYSIS FEATURES:**"
echo "   • Price tracking from DRAMExchange.com"
echo "   • Market news correlation with URLs"
echo "   • Investment implications"
echo "   • Risk assessment"
echo "   • Daily updates at 9 AM SGT"

echo ""
echo "✅ Enhanced memory price analysis completed at $(date '+%H:%M:%S')"