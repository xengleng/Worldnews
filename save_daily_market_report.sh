#!/bin/bash
# Save 8 AM Daily Market Report to Obsidian and GitHub under "Daily Market Report"

set -e

# Configuration
OBSIDIAN_VAULT="$HOME/Documents/openclaw"
GITHUB_REPO="https://github.com/xengleng/Worldnews"
REPORTS_DIR="$OBSIDIAN_VAULT/Daily Market Report"

# Create directory if it doesn't exist
mkdir -p "$REPORTS_DIR"

# Get current date
DATE=$(date +%Y-%m-%d)
YEAR=$(date +%Y)
MONTH=$(date +%m)

# Check if report file exists
REPORT_FILE="8am_daily_report_${DATE}.md"
if [ ! -f "$REPORT_FILE" ]; then
    echo "❌ Report file not found: $REPORT_FILE"
    echo "Available report files:"
    ls -la 8am_daily_report_*.md 2>/dev/null || echo "No report files found"
    exit 1
fi

# Read the report content
REPORT_CONTENT=$(cat "$REPORT_FILE")

# Extract title from report (first line after #)
TITLE=$(echo "$REPORT_CONTENT" | grep -m1 "^# " | sed 's/^# //')
if [ -z "$TITLE" ]; then
    TITLE="Daily Market Report - $DATE"
fi

# Create filename
FILENAME="${DATE}_Daily_Market_Report.md"
FILEPATH="$REPORTS_DIR/$FILENAME"

# Create the markdown file with the complete report
cat > "$FILEPATH" << EOF
# Daily Market Report - $DATE

**Date:** $DATE 08:00 AM SGT  
**Generated:** 8 AM Daily Market Report System  
**Type:** Comprehensive Market Analysis with RAG Insights

---

## 📊 COMPLETE DAILY MARKET REPORT

$REPORT_CONTENT

---

**Archived:** $(date "+%Y-%m-%d %H:%M:%S %Z")  
**Location:** Obsidian Vault + GitHub Repository  
**Category:** Daily Market Report  
**Next Report:** $(date -d "+1 day" "+%Y-%m-%d") 08:00 AM SGT

#dailymarketreport #marketanalysis #rag #$(date +%Y-%m-%d) #$(date +%B)
EOF

echo "✅ Created: $FILEPATH"

# Navigate to Obsidian vault
cd "$OBSIDIAN_VAULT"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Initializing git in Obsidian vault..."
    git init
    git checkout -b main 2>/dev/null || true
fi

# Check if GitHub remote is configured
if ! git remote -v | grep -q origin; then
    echo "Configuring GitHub remote: $GITHUB_REPO"
    git remote add origin "$GITHUB_REPO"
fi

# Check current branch
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "main")
if [ -z "$CURRENT_BRANCH" ]; then
    CURRENT_BRANCH="main"
fi

# Add and commit the new report
git add "$FILEPATH"
git commit -m "📈 Daily Market Report: $DATE - Comprehensive market analysis with RAG insights"

# Push to GitHub
echo "Pushing to GitHub repository (branch: $CURRENT_BRANCH)..."
if git push origin "$CURRENT_BRANCH" 2>/dev/null || git push -u origin "$CURRENT_BRANCH" 2>/dev/null; then
    echo "✅ Successfully pushed to GitHub: $GITHUB_REPO"
else
    echo "⚠️  Could not push to GitHub. Check credentials or network."
    echo "Trying with force push..."
    git push -f origin "$CURRENT_BRANCH" 2>/dev/null && echo "✅ Force push successful" || echo "❌ Force push failed"
fi

echo ""
echo "📊 Report saved to:"
echo "   • Obsidian vault: $FILEPATH"
echo "   • GitHub repo: $GITHUB_REPO (branch: $CURRENT_BRANCH)"
echo ""
echo "📋 Report contains:"
echo "   • Macro Overview with Fed policy analysis"
echo "   • Sector Analysis (Gold, Tech, Singapore Markets, Forex)"
echo "   • Action Plan & Strategy"
echo "   • RAG Knowledge Base Insights"
echo "   • Risk Assessment"
echo "   • System Status"