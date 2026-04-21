#!/bin/bash
# Save COMPLETE Bloomberg-style WorldMonitor reports to Obsidian and GitHub
# This saves the full report as-is, not truncated or reformatted

set -e

# Configuration
OBSIDIAN_VAULT="$HOME/Documents/openclaw"
GITHUB_REPO="https://github.com/xengleng/Worldnews"
REPORTS_DIR="$OBSIDIAN_VAULT/World News"

# Create directory if it doesn't exist
mkdir -p "$REPORTS_DIR"

# Get current timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)

# Parse arguments
if [ $# -lt 2 ]; then
    echo "Usage: $0 \"Report Title\" \"Full report content...\""
    echo "Example: $0 \"Bloomberg Report\" \"Full report content with newlines and formatting\""
    exit 1
fi

TITLE="$1"
REPORT_CONTENT="$2"

# Create filename (sanitize title)
SAFE_TITLE=$(echo "$TITLE" | tr ' ' '_' | tr -cd 'A-Za-z0-9_-')
FILENAME="${DATE}_${SAFE_TITLE}.md"
FILEPATH="$REPORTS_DIR/$FILENAME"

# Create the markdown file with the COMPLETE report as-is
cat > "$FILEPATH" << EOF
# $TITLE

**Date:** $DATE $TIME SGT  
**Generated:** WorldMonitor Bloomberg Categorizer  
**Type:** Bloomberg-style News Analysis

---

## 📰 COMPLETE BLOOMBERG-STYLE REPORT

$REPORT_CONTENT

---

**Archived:** $(date "+%Y-%m-%d %H:%M:%S %Z")  
**Location:** Obsidian Vault + GitHub Repository  
**Next Update:** Every 6 hours (9 AM, 3 PM, 9 PM, 3 AM SGT)

#worldnews #bloomberg #newsanalysis #$(date +%Y-%m-%d)
EOF

echo "✅ Created: $FILEPATH"

# Navigate to Obsidian vault
cd "$OBSIDIAN_VAULT"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Initializing git in Obsidian vault..."
    git init
fi

# Check if GitHub remote is configured
if ! git remote -v | grep -q origin; then
    echo "Configuring GitHub remote: $GITHUB_REPO"
    git remote add origin "$GITHUB_REPO"
fi

# Add and commit the new report
git add "$FILEPATH"
git commit -m "📈 Bloomberg Report: $TITLE - $DATE"

# Push to GitHub
echo "Pushing to GitHub repository..."
if git push origin main 2>/dev/null || git push -u origin main 2>/dev/null; then
    echo "✅ Successfully pushed to GitHub: $GITHUB_REPO"
else
    echo "⚠️  Could not push to GitHub. Check credentials or network."
fi

echo ""
echo "📊 Report saved to:"
echo "   • Obsidian vault: $FILEPATH"
echo "   • GitHub repo: $GITHUB_REPO"
echo ""
echo "📋 Report contains FULL Bloomberg-style formatting with:"
echo "   • Alert levels (🔴🟠🟡🟢)"
echo "   • Category breakdown"
echo "   • All article URLs"
echo "   • Complete analysis"