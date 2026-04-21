#!/bin/bash
# Save DRAMExchange price reports to Obsidian vault

set -e

# Configuration
OBSIDIAN_VAULT="$HOME/Documents/openclaw"
REPORTS_DIR="$OBSIDIAN_VAULT/Memory Prices"

# Create directory if it doesn't exist
mkdir -p "$REPORTS_DIR"

# Get current timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)

# Parse arguments
if [ $# -lt 2 ]; then
    echo "Usage: $0 \"Report Title\" \"Full report content...\""
    echo "Example: $0 \"DRAMExchange Daily Report\" \"Full report content...\""
    exit 1
fi

TITLE="$1"
REPORT_CONTENT="$2"

# Create filename (sanitize title)
SAFE_TITLE=$(echo "$TITLE" | tr ' ' '_' | tr -cd 'A-Za-z0-9_-')
FILENAME="${DATE}_${SAFE_TITLE}.md"
FILEPATH="$REPORTS_DIR/$FILENAME"

# Create the markdown file with the COMPLETE report
cat > "$FILEPATH" << EOF
# $TITLE

**Date:** $DATE $TIME SGT  
**Generated:** OpenClaw DRAMExchange Tracker  
**Source:** https://www.dramexchange.com/

---

$REPORT_CONTENT

---

**Archived:** $(date "+%Y-%m-%d %H:%M:%S %Z")  
**Location:** Obsidian Vault - Memory Prices  
**Next Update:** Daily at 9 AM SGT

#dramexchange #memoryprices #dram #nand #flash #marketanalysis #$(date +%Y-%m-%d)
EOF

echo "✅ Created: $FILEPATH"

# Also save to workspace memory_prices directory for backup
WORKSPACE_DIR="$HOME/.openclaw/workspace/memory_prices"
mkdir -p "$WORKSPACE_DIR"
WORKSPACE_FILE="${WORKSPACE_DIR}/dramexchange_report_${TIMESTAMP}.txt"
cp "$FILEPATH" "$WORKSPACE_FILE"
echo "✅ Backup saved to: $WORKSPACE_FILE"

echo ""
echo "📊 Report saved to:"
echo "   • Obsidian vault: $FILEPATH"
echo "   • Workspace backup: $WORKSPACE_FILE"