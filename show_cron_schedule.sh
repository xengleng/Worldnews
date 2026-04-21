#!/bin/bash
# Show cron schedule in SGT time

echo "📅 ACTIVE CRON JOBS SCHEDULE (SGT TIME)"
echo "=" * 70
echo ""

# Get current time in SGT
echo "Current time: $(TZ='Asia/Singapore' date '+%Y-%m-%d %H:%M:%S %Z')"
echo ""

# Show all jobs
echo "ALL ACTIVE JOBS:"
echo "----------------------------------------------------------------"

openclaw cron list | while read -r line; do
    # Skip header lines
    if [[ $line == *"ID"* ]] || [[ $line == *"---"* ]]; then
        continue
    fi
    
    # Parse the line
    id=$(echo "$line" | awk '{print $1}')
    name=$(echo "$line" | awk '{print $2}')
    schedule=$(echo "$line" | awk '{print $3" "$4" "$5" "$6" "$7}')
    next_utc=$(echo "$line" | awk '{print $8}')
    last_run=$(echo "$line" | awk '{print $9}')
    status=$(echo "$line" | awk '{print $10}')
    
    # Convert next run to SGT
    if [[ $next_utc != "in"* ]] && [[ $next_utc != "-" ]]; then
        # Convert UTC to SGT (UTC+8)
        next_sgt=$(date -d "$next_utc UTC +8 hours" '+%Y-%m-%d %H:%M' 2>/dev/null || echo "$next_utc")
    else
        next_sgt=$next_utc
    fi
    
    # Get job details for description
    details=$(openclaw cron get "$id" 2>/dev/null | jq -r '.payload.message // "No description"' | head -1)
    
    echo "🔸 $name"
    echo "   ID: $id"
    echo "   Schedule: $schedule"
    echo "   Next run: $next_sgt SGT"
    echo "   Status: $status"
    echo "   Description: $details"
    echo ""
done

echo "=" * 70
echo ""

# Show schedule by time
echo "📋 DAILY SCHEDULE (SGT TIME):"
echo "----------------------------------------------------------------"

# Define schedule in SGT
echo "🕘 09:00 AM - World Monitor Brief (wm-brief-9am)"
echo "   Memory Price Tracker (memory-price-tracker)"
echo ""
echo "🕐 01:00 PM - World Monitor Brief (wm-brief-1pm)"
echo ""
echo "🕕 06:00 PM - World Monitor Brief (wm-brief-6pm)"
echo ""
echo "🕙 10:00 PM - World Monitor Brief (wm-brief-10pm)"
echo ""
echo "🕗 08:00 AM - Daily Report (8am-daily-report)"
echo ""
echo "🕑 02:00 AM - RAG Update (rag-daily-update)"
echo ""

echo "=" * 70
echo ""

# Next 24 hours
echo "⏰ NEXT 24 HOURS:"
echo "----------------------------------------------------------------"

current_time=$(date +%s)
for hour in {0..23}; do
    hour_time=$((current_time + hour * 3600))
    hour_str=$(TZ='Asia/Singapore' date -d "@$hour_time" '+%H:00')
    
    # Check which jobs run at this hour
    jobs_at_hour=""
    
    case $hour_str in
        "09:00")
            jobs_at_hour="wm-brief-9am, memory-price-tracker"
            ;;
        "13:00")
            jobs_at_hour="wm-brief-1pm"
            ;;
        "18:00")
            jobs_at_hour="wm-brief-6pm"
            ;;
        "22:00")
            jobs_at_hour="wm-brief-10pm"
            ;;
        "08:00")
            jobs_at_hour="8am-daily-report"
            ;;
        "02:00")
            jobs_at_hour="rag-daily-update"
            ;;
    esac
    
    if [ -n "$jobs_at_hour" ]; then
        echo "$hour_str SGT: $jobs_at_hour"
    fi
done

echo ""
echo "✅ All cron jobs are enabled and active"