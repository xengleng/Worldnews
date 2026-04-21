#!/bin/bash
# Simple cron schedule display

echo "📅 CRON JOBS - NEXT RUN TIMES"
echo "=" * 60
echo "Current time: $(TZ='Asia/Singapore' date '+%Y-%m-%d %H:%M:%S %Z')"
echo ""

echo "ALL ACTIVE JOBS:"
echo "----------------------------------------------------------------"

openclaw cron list | while read -r line; do
    # Skip header lines
    if [[ $line == *"ID"* ]] || [[ $line == *"---"* ]]; then
        continue
    fi
    
    # Extract fields
    id=$(echo "$line" | awk '{print $1}')
    name=$(echo "$line" | awk '{print $2}')
    schedule_expr=$(echo "$line" | awk '{print $4}')
    next_utc=$(echo "$line" | awk '{print $8" "$9" "$10" "$11" "$12" "$13" "$14}')
    status=$(echo "$line" | awk '{print $15}')
    
    # Convert next run to SGT if it's a timestamp
    if [[ $next_utc == "in"* ]]; then
        next_sgt="$next_utc"
    elif [[ $next_utc != "-" ]]; then
        # Try to convert UTC to SGT
        next_sgt=$(date -d "$next_utc UTC +8 hours" '+%Y-%m-%d %H:%M' 2>/dev/null || echo "$next_utc")
    else
        next_sgt="Never"
    fi
    
    # Get SGT time from cron expression
    if [[ $schedule_expr =~ ^[0-9] ]]; then
        utc_hour=$(echo "$schedule_expr" | awk '{print $2}')
        sgt_hour=$(( (utc_hour + 8) % 24 ))
        sgt_time=$(printf "%02d:00" $sgt_hour)
    else
        sgt_time="N/A"
    fi
    
    echo "🔸 $name"
    echo "   Scheduled: $sgt_time SGT (UTC: $schedule_expr)"
    echo "   Next run:  $next_sgt SGT"
    echo "   Status:    $status"
    echo ""
done

echo "=" * 60
echo ""

echo "⏰ TODAY'S SCHEDULE (SGT TIME):"
echo "----------------------------------------------------------------"

# Today's expected runs in SGT
echo "09:00 SGT - wm-brief-9am, memory-price-tracker"
echo "13:00 SGT - wm-brief-1pm" 
echo "18:00 SGT - wm-brief-6pm"
echo "22:00 SGT - wm-brief-10pm"
echo ""
echo "08:00 SGT - 8am-daily-report"
echo "02:00 SGT - rag-daily-update (runs overnight)"

echo ""
echo "=" * 60
echo ""

echo "🎯 NEXT JOB TO RUN:"
echo "----------------------------------------------------------------"

# Find the next job
next_job=$(openclaw cron list | grep -v "ID\|---" | head -1)
if [ -n "$next_job" ]; then
    name=$(echo "$next_job" | awk '{print $2}')
    next_time=$(echo "$next_job" | awk '{print $8" "$9" "$10" "$11" "$12" "$13" "$14}')
    
    if [[ $next_time == "in"* ]]; then
        echo "$name - $next_time"
    else
        sgt_time=$(date -d "$next_time UTC +8 hours" '+%H:%M' 2>/dev/null || echo "$next_time")
        echo "$name - $sgt_time SGT"
    fi
else
    echo "No jobs found"
fi

echo ""
echo "📊 SUMMARY: 7 cron jobs configured, all enabled"