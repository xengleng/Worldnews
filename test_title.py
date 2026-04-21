#!/usr/bin/env python3
from datetime import datetime

# Test the new title format
report_title = f"World Monitor Brief - {datetime.now().strftime('%Y-%m-%d %H:%M')} SGT"
print(f"New title: {report_title}")

# Also check the save_bloomberg_report.sh would create correct filename
date_str = datetime.now().strftime('%Y-%m-%d')
safe_title = report_title.replace(' ', '_').replace(':', '').replace('-', '')
safe_title = ''.join(c for c in safe_title if c.isalnum() or c in '_-')
filename = f"{date_str}_{safe_title}.md"
print(f"Filename would be: {filename}")

# Show next run times
print("\nNext World Monitor Brief runs:")
print("• 9 AM SGT (1 AM UTC)")
print("• 1 PM SGT (5 AM UTC)")
print("• 6 PM SGT (10 AM UTC)")
print("• 10 PM SGT (2 PM UTC)")

current_time = datetime.now()
print(f"\nCurrent time: {current_time.strftime('%Y-%m-%d %H:%M')} SGT")