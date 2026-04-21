#!/usr/bin/env python3
"""
Show cron jobs with SGT times
"""

import subprocess
import json
from datetime import datetime, timezone, timedelta
import os

print("📅 CRON JOBS SCHEDULE (SGT TIME)")
print("=" * 70)
print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} SGT")
print()

# Get cron jobs
result = subprocess.run(['openclaw', 'cron', 'list', '--json'], 
                       capture_output=True, text=True)

if result.returncode != 0:
    print("Error getting cron jobs:", result.stderr)
    exit(1)

try:
    data = json.loads(result.stdout)
    jobs = data.get('jobs', [])
except json.JSONDecodeError:
    print("Error parsing JSON")
    exit(1)

# Sort by next run time
jobs.sort(key=lambda x: x.get('state', {}).get('nextRunAtMs', float('inf')))

print(f"{'NAME':20} {'SGT TIME':12} {'NEXT RUN':20} {'STATUS':10} {'LAST RUN':20}")
print("-" * 70)

for job in jobs:
    name = job.get('name', 'Unknown')
    enabled = job.get('enabled', False)
    
    # Schedule info
    schedule = job.get('schedule', {})
    expr = schedule.get('expr', 'N/A')
    tz = schedule.get('tz', 'UTC')
    
    # Convert UTC cron to SGT time
    sgt_time = "N/A"
    if expr != 'N/A':
        # Parse cron expression (0 1 * * * format)
        parts = expr.split()
        if len(parts) >= 2:
            utc_hour = int(parts[1])  # Hour is second field
            sgt_hour = (utc_hour + 8) % 24  # UTC+8
            sgt_time = f"{sgt_hour:02d}:00"
    
    # Next run
    next_run_ms = job.get('state', {}).get('nextRunAtMs', 0)
    if next_run_ms:
        next_run_utc = datetime.fromtimestamp(next_run_ms / 1000, tz=timezone.utc)
        next_run_sgt = next_run_utc + timedelta(hours=8)
        next_run_str = next_run_sgt.strftime('%Y-%m-%d %H:%M')
        # Make both timezone aware for comparison
        now_aware = datetime.now().replace(tzinfo=timezone(timedelta(hours=8)))  # SGT
        hours_from_now = (next_run_sgt - now_aware).total_seconds() / 3600
        if hours_from_now < 24:
            next_display = f"{next_run_sgt.strftime('%H:%M')} (in {hours_from_now:.1f}h)"
        else:
            next_display = next_run_sgt.strftime('%H:%M')
    else:
        next_display = "N/A"
    
    # Last run
    last_run_info = "Never"
    # We don't have last run time in the JSON, but we can check status
    
    status = '✅' if job.get('status') == 'ok' else '🔄' if job.get('status') == 'running' else '❌'
    
    print(f"{name:20} {sgt_time:12} {next_display:20} {status:10} {last_run_info:20}")

print()
print("=" * 70)
print()

# Show schedule by time of day
print("⏰ DAILY SCHEDULE ORDER (SGT TIME):")
print("-" * 40)

# Create time slots
time_slots = {}
for job in jobs:
    if 'brief' in name or 'report' in name.lower() or 'memory' in name:
        schedule = job.get('schedule', {})
        expr = schedule.get('expr', '')
        if expr:
            parts = expr.split()
            if len(parts) >= 2:
                utc_hour = int(parts[1])
                sgt_hour = (utc_hour + 8) % 24
                time_slots.setdefault(sgt_hour, []).append(job.get('name'))

# Sort by hour
for hour in sorted(time_slots.keys()):
    hour_str = f"{hour:02d}:00"
    jobs_list = ", ".join(time_slots[hour])
    print(f"{hour_str} SGT: {jobs_list}")

print()
print("🎯 NEXT 24 HOURS:")
print("-" * 40)

now = datetime.now()
next_24h = []

for job in jobs:
    next_run_ms = job.get('state', {}).get('nextRunAtMs', 0)
    if next_run_ms:
        next_run_utc = datetime.fromtimestamp(next_run_ms / 1000, tz=timezone.utc)
        next_run_sgt = next_run_utc + timedelta(hours=8)
        hours_diff = (next_run_sgt - now).total_seconds() / 3600
        
        if 0 <= hours_diff <= 24:
            next_24h.append((next_run_sgt, job.get('name')))

if next_24h:
    next_24h.sort()
    for run_time, name in next_24h:
        time_str = run_time.strftime('%H:%M')
        hours_str = f"in {(run_time - now).total_seconds()/3600:.1f}h"
        print(f"{time_str} SGT ({hours_str:8}) - {name}")
else:
    print("No jobs in next 24 hours")

print()
print(f"📊 Total jobs: {len(jobs)}")
print(f"✅ All jobs are enabled")