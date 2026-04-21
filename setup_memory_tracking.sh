#!/bin/bash
# Setup Memory Price Tracking System

set -e

echo "💾 Setting up Memory Price Tracking System"
echo "=" * 50

# Check Python dependencies
echo "Checking Python dependencies..."
python3 -c "import requests, beautifulsoup4" 2>/dev/null || {
    echo "Installing required Python packages..."
    pip3 install requests beautifulsoup4 lxml
}

# Create data directory
DATA_DIR="$HOME/.openclaw/workspace/memory_prices"
echo "Creating data directory: $DATA_DIR"
mkdir -p "$DATA_DIR"

# Make scripts executable
chmod +x memory_price_tracker.py

# Create cron job for daily tracking
echo ""
echo "⏰ Setting up daily tracking cron job..."
CRON_JOB="0 1 * * * cd $HOME/.openclaw/workspace && python3 memory_price_tracker.py"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "memory_price_tracker.py"; then
    echo "✅ Cron job already exists"
else
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✅ Daily cron job added (9 AM SGT)"
fi

# Create initial data files
echo ""
echo "📊 Creating initial data files..."
python3 -c "
import json
from datetime import datetime
from pathlib import Path

data_dir = Path('$DATA_DIR')
data_dir.mkdir(exist_ok=True)

# Create initial JSON structure
initial_data = {
    'metadata': {
        'created': datetime.now().isoformat(),
        'last_updated': None,
        'source': 'DRAMExchange.com',
        'currency': 'USD',
        'description': 'Memory price tracking database'
    },
    'price_history': {}
}

json_file = data_dir / 'historical_prices.json'
with open(json_file, 'w') as f:
    json.dump(initial_data, f, indent=2)

print(f'✅ Created: {json_file}')
"

# Create README
README_FILE="$DATA_DIR/README.md"
cat > "$README_FILE" << EOF
# Memory Price Tracking System

## Overview
This system tracks memory prices from DRAMExchange.com including:
- DRAM Spot Prices (DDR5, DDR4, DDR3)
- NAND Flash Spot Prices (SLC, MLC)
- Module Spot Prices
- SSD Street Prices
- Memory Card Prices

## Files
- \`historical_prices.json\` - Complete price history in JSON format
- \`price_history.csv\` - CSV export of all price data
- \`price_report_*.txt\` - Daily price reports
- \`trends_analysis_*.json\` - Trend analysis

## Usage
\`\`\`bash
# Run manually
python3 memory_price_tracker.py

# View latest report
ls -la memory_prices/price_report_*.txt | tail -1

# View historical data
cat memory_prices/historical_prices.json | jq '.metadata'
\`\`\`

## Schedule
- **Daily at 9 AM SGT** - Automatic price tracking
- Manual runs anytime with \`python3 memory_price_tracker.py\`

## Data Structure
Each price record includes:
- timestamp
- item name
- daily high/low
- session high/low/avg
- change percentage
- category

## Source
Data sourced from: https://www.dramexchange.com/

Last updated: $(date)
EOF

echo "✅ Created: $README_FILE"

# Run initial tracking
echo ""
echo "🚀 Running initial price tracking..."
python3 memory_price_tracker.py

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 **System Overview:**"
echo "   • Data directory: $DATA_DIR"
echo "   • Daily cron: 9 AM SGT (1 AM UTC)"
echo "   • Tracked: DRAM, NAND Flash, SSD, Memory Cards"
echo "   • Formats: JSON + CSV + Text reports"
echo ""
echo "📊 **Next Steps:**"
echo "   1. Check initial report: cat $DATA_DIR/price_report_*.txt"
echo "   2. View data: cat $DATA_DIR/historical_prices.json | jq '.metadata'"
echo "   3. Manual run: python3 memory_price_tracker.py"
echo ""
echo "🔧 **Maintenance:**"
echo "   • Reports auto-cleanup after 30 days"
echo "   • CSV file grows continuously"
echo "   • JSON file keeps all history"