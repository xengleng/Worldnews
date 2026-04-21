#!/bin/bash
# Daily update for flat‑file RAG
# Run via cron or heartbeat

cd "$(dirname "$0")"

echo "[$(date)] Starting RAG update..."

# Run the update script
python update_rag_from_memory_v2.py 2>&1 | tee -a memory/rag_update.log

# Check if any updates were made
if grep -q "Added.*sections to" memory/rag_update.log || grep -q "Run.*python rag_flat.py --rebuild" memory/rag_update.log; then
    echo "[$(date)] New content found or rebuild recommended, rebuilding index..."
    python rag_flat.py --rebuild 2>&1 | tee -a memory/rag_update.log
    echo "[$(date)] Index rebuilt."
else
    echo "[$(date)] No new content, index unchanged."
fi

# Update last run timestamp
echo "[$(date)] Updating last run timestamp..."
date +%s > memory/rag_last_update.txt

echo "[$(date)] RAG update complete."