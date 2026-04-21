#!/usr/bin/env python3
"""
Heartbeat‑triggered RAG update.
Checks if last update was >12 hours ago, runs update if needed.
"""

import os
import time
from pathlib import Path

LAST_RUN_FILE = Path(__file__).parent / "memory" / "rag_last_update.txt"
UPDATE_SCRIPT = Path(__file__).parent / "rag_daily_update.sh"

def should_update() -> bool:
    if not LAST_RUN_FILE.exists():
        return True
    
    try:
        last = float(LAST_RUN_FILE.read_text().strip())
        now = time.time()
        # Update if >12 hours (43200 seconds)
        return (now - last) > 43200
    except:
        return True

def run_update():
    print("RAG update overdue, running...")
    os.system(str(UPDATE_SCRIPT))
    LAST_RUN_FILE.write_text(str(time.time()))

if __name__ == "__main__":
    if should_update():
        run_update()
    else:
        print("RAG update not yet due.")