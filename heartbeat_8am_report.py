#!/usr/bin/env python3
"""
Heartbeat check for 8 AM report.
Run during heartbeats between 08:00-08:30.
"""

import os
import time
from datetime import datetime, date
from pathlib import Path

LAST_REPORT_FILE = Path(__file__).parent / "memory" / "last_report_date.txt"

def should_send_report() -> bool:
    """Check if we should send the 8 AM report."""
    now = datetime.now()
    
    # Check time window (08:00-08:30)
    if not (8 <= now.hour < 8.5):  # 8:00 to 8:30
        return False
    
    # Check if already sent today
    if LAST_REPORT_FILE.exists():
        try:
            last_date_str = LAST_REPORT_FILE.read_text().strip()
            last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
            if last_date == date.today():
                return False
        except:
            pass
    
    return True

def send_report():
    """Generate and send the 8 AM report."""
    print("⏰ It's 8 AM! Generating daily report...")
    
    # Generate report
    import subprocess
    result = subprocess.run(
        ["/usr/bin/python", "8am_report_now.py"],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(__file__)
    )
    
    if result.returncode == 0:
        # Find the generated report file
        report_files = list(Path(".").glob("8am_report_*.txt"))
        if report_files:
            latest = max(report_files, key=os.path.getctime)
            content = latest.read_text(encoding="utf-8")
            
            # Send via Telegram (you'd integrate with OpenClaw messaging)
            print(f"✅ Report generated: {latest.name}")
            print("📤 Would send via Telegram here")
            
            # For now, just show preview
            lines = content.split("\n")
            print("\n--- REPORT PREVIEW ---")
            for line in lines[:20]:
                print(line)
            print("... (truncated)")
        else:
            print("❌ No report file generated")
    else:
        print(f"❌ Report generation failed: {result.stderr}")
    
    # Mark as sent
    LAST_REPORT_FILE.write_text(date.today().isoformat())
    print(f"📅 Marked report as sent for {date.today()}")

if __name__ == "__main__":
    if should_send_report():
        send_report()
    else:
        now = datetime.now()
        if LAST_REPORT_FILE.exists():
            last = LAST_REPORT_FILE.read_text().strip()
            print(f"Report already sent today ({last}). Next: tomorrow 8 AM.")
        else:
            print(f"Not in 8 AM window (current time: {now.strftime('%H:%M')})")