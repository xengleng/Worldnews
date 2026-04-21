#!/bin/bash
# Simple stock news monitor using curl and built-in tools

# Configuration
STOCKS="MRVL AMD NVIDIA FIG"
DATE=$(date '+%Y-%m-%d %H:%M')

echo "📈 Daily Stock News Report - $DATE"
echo "Monitoring: $STOCKS"
echo ""

# Function to fetch and parse RSS
fetch_rss() {
    local url="$1"
    local source="$2"
    local symbol="$3"
    
    curl -s "$url" 2>/dev/null | \
    grep -E "<title>|<link>|<pubDate>|<description>" | \
    sed 's/<[^>]*>//g' | \
    sed 's/^[ \t]*//' | \
    tail -n +2 | \
    paste -d '|' - - - - | \
    while IFS='|' read -r title link pubdate description; do
        echo "$source|$symbol|$title|$link|$pubdate|$description"
    done
}

# Check each stock
for symbol in $STOCKS; do
    echo "🔍 Checking $symbol..."
    
    # Yahoo Finance
    yahoo_url="https://feeds.finance.yahoo.com/rss/2.0/headline?s=$symbol&region=US&lang=en-US"
    fetch_rss "$yahoo_url" "Yahoo Finance" "$symbol" | head -3
    
    # Google News (simplified)
    case $symbol in
        MRVL) query="Marvell+Technology+stock" ;;
        AMD) query="AMD+stock+Advanced+Micro+Devices" ;;
        NVIDIA) query="NVIDIA+stock" ;;
        FIG) query="FIG+Partners+stock+OR+Fortress+Investment+Group" ;;
    esac
    
    google_url="https://news.google.com/rss/search?q=$query&hl=en-US&gl=US&ceid=US:en"
    fetch_rss "$google_url" "Google News" "$symbol" | head -2
    
    sleep 1
done

echo ""
echo "✅ Report generated at $DATE"
echo "Note: For detailed analysis, run the Python version with required packages."