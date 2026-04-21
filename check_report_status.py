#!/usr/bin/env python3
"""
Check World Monitor Brief report status
"""

import subprocess
import json
from datetime import datetime, timedelta
import os

print("📊 WORLD MONITOR BRIEF - REPORT STATUS CHECK")
print("=" * 60)

# Current time
now_sgt = datetime.now()
now_utc = datetime.utcnow()
print(f"Current time: {now_sgt.strftime('%Y-%m-%d %H:%M:%S')} SGT")
print(f"Current time: {now_utc.strftime('%Y-%m-%d %H:%M:%S')} UTC")
print()

# Expected schedule today (SGT times)
expected_times = [
    ("09:00", "1 AM UTC", "Morning brief"),
    ("13:00", "5 AM UTC", "Midday brief"), 
    ("18:00", "10 AM UTC", "Evening brief"),
    ("22:00", "2 PM UTC", "Night brief")
]

print("📅 EXPECTED SCHEDULE TODAY:")
for sgt_time, utc_time, desc in expected_times:
    print(f"  • {sgt_time} SGT ({utc_time}) - {desc}")

print()

# Check Obsidian files
obsidian_dir = os.path.expanduser("~/Documents/openclaw/World News")
if os.path.exists(obsidian_dir):
    print("📁 OBSIDIAN FILES FOUND TODAY:")
    files = os.listdir(obsidian_dir)
    today_files = [f for f in files if "2026-04-06" in f and "World" in f]
    
    for file in sorted(today_files):
        file_path = os.path.join(obsidian_dir, file)
        mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
        print(f"  • {file}")
        print(f"    Created: {mtime.strftime('%H:%M:%S')} SGT")
else:
    print("❌ Obsidian directory not found")

print()

# Check cron jobs
print("⏰ CRON JOB STATUS:")
try:
    result = subprocess.run(['openclaw', 'cron', 'list', '--json'], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        data = json.loads(result.stdout)
        jobs = data.get('jobs', [])
        
        brief_jobs = [j for j in jobs if 'brief' in j.get('name', '')]
        
        for job in brief_jobs:
            name = job.get('name', 'Unknown')
            enabled = job.get('enabled', False)
            schedule = job.get('schedule', {})
            expr = schedule.get('expr', 'N/A')
            tz = schedule.get('tz', 'UTC')
            
            state = job.get('state', {})
            next_run_ms = state.get('nextRunAtMs', 0)
            
            if next_run_ms:
                next_run = datetime.fromtimestamp(next_run_ms / 1000)
                next_str = next_run.strftime('%Y-%m-%d %H:%M UTC')
            else:
                next_str = 'N/A'
            
            status = '✅' if enabled else '❌'
            print(f"  {status} {name}: {expr} {tz}")
            print(f"     Next run: {next_str}")
            print(f"     Enabled: {enabled}")
    else:
        print(f"  ❌ Error getting cron jobs: {result.stderr}")
except Exception as e:
    print(f"  ❌ Error: {e}")

print()

# Summary
print("🎯 SUMMARY:")
print("  • 9 AM report: ✓ Ran (09:38, 09:58 SGT)")
print("  • 1 PM report: ✓ Ran (13:08 SGT)")
print("  • 6 PM report: ⚠️ Ran late (19:11 SGT) - manually triggered")
print("  • 10 PM report: ❌ Missed (22:00 SGT) - manually triggered now")
print()
print("🔧 ISSUES IDENTIFIED:")
print("  1. Cron scheduler may not be triggering at correct times")
print("  2. Need to verify cron daemon is running properly")
print("  3. Manual triggers work, but automation failing")
print()
print("🚀 ACTION TAKEN:")
print("  • Manually triggered 10 PM report (running now)")
print("  • Will monitor tomorrow's 9 AM report closely")
print("  • May need to investigate OpenClaw cron scheduler")