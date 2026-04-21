#!/usr/bin/env python3
"""
List all active cron jobs with details
"""

import json
import subprocess
from datetime import datetime

# Get cron jobs
result = subprocess.run(['openclaw', 'cron', 'list', '--json'], 
                       capture_output=True, text=True)

if result.returncode != 0:
    print("Error getting cron jobs:", result.stderr)
    exit(1)

try:
    data = json.loads(result.stdout)
    # Extract jobs from the response
    jobs = data.get('jobs', [])
except json.JSONDecodeError:
    print("Error parsing JSON")
    exit(1)

print("📅 ACTIVE CRON JOBS")
print("=" * 100)
print(f"{'NAME':25} {'SCHEDULE':20} {'NEXT RUN (SGT)':20} {'ENABLED':10} {'DESCRIPTION'}")
print("-" * 100)

# Sort by next run time
jobs = sorted(jobs, key=lambda x: x.get('state', {}).get('nextRunAtMs', 0))

for job in jobs:
    name = job.get('name', 'Unknown')
    enabled = job.get('enabled', False)
    
    # Schedule info
    schedule = job.get('schedule', {})
    expr = schedule.get('expr', 'N/A')
    tz = schedule.get('tz', 'UTC')
    
    # Next run
    next_run_ms = job.get('state', {}).get('nextRunAtMs', 0)
    if next_run_ms:
        next_run_dt = datetime.fromtimestamp(next_run_ms / 1000)
        next_run_str = next_run_dt.strftime('%Y-%m-%d %H:%M')
    else:
        next_run_str = 'N/A'
    
    # Get description from payload
    payload = job.get('payload', {})
    description = payload.get('message', 'No description')
    
    # Truncate description if too long
    if len(description) > 50:
        description = description[:47] + '...'
    
    status = '✅' if enabled else '❌'
    
    print(f"{name:25} {expr:10} {tz:10} {next_run_str:20} {status:10} {description}")

print("\n" + "=" * 100)

# Summary
total_jobs = len(jobs)
enabled_jobs = sum(1 for j in jobs if j.get('enabled', False))
disabled_jobs = total_jobs - enabled_jobs

print(f"📊 SUMMARY: {total_jobs} total jobs ({enabled_jobs} enabled, {disabled_jobs} disabled)")

# Group by category
print("\n📋 CATEGORIES:")
categories = {
    'World Monitor Brief': [j for j in jobs if 'wm-brief' in j.get('name', '')],
    'Memory Tracking': [j for j in jobs if 'memory' in j.get('name', '').lower()],
    'Daily Reports': [j for j in jobs if 'report' in j.get('name', '').lower()],
    'Other': []
}

# Add remaining jobs to Other
for job in jobs:
    assigned = False
    for category in ['World Monitor Brief', 'Memory Tracking', 'Daily Reports']:
        if job in categories[category]:
            assigned = True
            break
    if not assigned:
        categories['Other'].append(job)

for category, job_list in categories.items():
    if job_list:
        print(f"  • {category}: {len(job_list)} jobs")

# Show next 24 hours schedule
print("\n⏰ NEXT 24 HOURS SCHEDULE:")
print("-" * 50)

now = datetime.now()
next_24h = []

for job in jobs:
    if not job.get('enabled', False):
        continue
    
    next_run_ms = job.get('state', {}).get('nextRunAtMs', 0)
    if next_run_ms:
        next_run_dt = datetime.fromtimestamp(next_run_ms / 1000)
        hours_diff = (next_run_dt - now).total_seconds() / 3600
        
        if 0 <= hours_diff <= 24:
            next_24h.append((next_run_dt, job))

# Sort by time
next_24h.sort(key=lambda x: x[0])

if next_24h:
    for next_time, job in next_24h:
        time_str = next_time.strftime('%H:%M')
        hours_from_now = (next_time - now).total_seconds() / 3600
        hours_str = f"in {hours_from_now:.1f}h" if hours_from_now > 0 else "NOW"
        
        print(f"  {time_str} SGT ({hours_str:8}) - {job.get('name')}")
else:
    print("  No jobs scheduled in next 24 hours")