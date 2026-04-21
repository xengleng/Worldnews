# HEARTBEAT.md - Periodic Tasks

## 8 AM Daily Report
- If time is between 08:00-08:30 and report not sent today, generate and send
- Track last report date in `memory/last_report_date.txt`

## RAG Update
- Run `./rag_daily_update.sh` if last run >12 hours ago
- Track last run in `memory/rag_last_update.txt`

## Email Check
- Check for urgent unread emails (if configured)

## Calendar
- Upcoming events in next 24h

## Weather
- Singapore weather if planning to go out