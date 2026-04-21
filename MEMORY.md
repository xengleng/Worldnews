# MEMORY.md - Long-Term Memory

## About This File
This is yoyoclaw's curated long-term memory. Unlike daily memory files (`memory/YYYY-MM-DD.md`) which are raw logs, this file contains distilled learnings, important decisions, and patterns worth remembering.

## Core Principles Learned

### 1. **Honesty About Limitations**
- **Lesson:** Never hallucinate or fake data
- **Example:** Initially created fake URLs for memory price analysis
- **Solution:** Always be transparent about what's actually possible
- **Rule:** If data requires paid access, say so. If scraping fails, explain why.

### 2. **Complete Data Preservation**
- **Lesson:** Never truncate important data
- **Example:** WorldMonitor reports were being cut to 500 characters
- **Solution:** Always save complete reports
- **Rule:** Users want the full analysis, not summaries

### 3. **Working URL Verification**
- **Lesson:** All URLs must be verified and working
- **Example:** Fake Reuters/Bloomberg URLs in early implementations
- **Solution:** Actually visit URLs before including them
- **Rule:** No hallucinations - only real, accessible data sources

### 4. **Practical Web Scraping**
- **Lesson:** Some sites block scraping or require paid access
- **Example:** DRAMExchange requires membership for price data
- **Solution:** Use alternative publicly accessible sources
- **Rule:** Scrape what's actually available, not what we wish was available

## System Architecture Decisions

### **World Monitor Brief System**
- **Title:** Changed from "WorldMonitor Bloomberg Report" to "World Monitor Brief"
- **Schedule:** 9 AM, 1 PM, 6 PM, 10 PM SGT (4x daily)
- **Format:** Bloomberg-style categorization with alert levels
- **Integration:** Automatic save to Obsidian + GitHub push
- **Files:** `worldmonitor_with_integration.py`, `save_bloomberg_report.sh`

### **Memory Price Tracking System**
- **Approach:** Actual web scraping (no hallucinations)
- **Sources:** Amazon, Newegg, Google News, tech sites
- **Schedule:** Daily at 9 AM SGT
- **Integration:** Same Obsidian/GitHub pipeline
- **Files:** `production_scraper.py`, `production_scraper_cron.sh`

### **Cron Job Management**
- **Total Jobs:** 7 active cron jobs
- **All Enabled:** Yes
- **Categories:**
  1. World Monitor Brief (4 jobs)
  2. Memory Price Tracker (1 job)
  3. Daily Reports (1 job)
  4. RAG Updates (1 job)

## Important Technical Details

### **Working URLs (Verified)**
1. **DRAMExchange RSS:** `https://www.dramexchange.com/rss.xml`
2. **Amazon Memory:** `https://www.amazon.com/Best-Sellers-Computers-Accessories-Memory/zgbs/pc/172500`
3. **Newegg Memory:** `https://www.newegg.com/p/pl?N=100007952`
4. **Google News:** `https://news.google.com/search?q=memory+prices+dram+nand+2026`
5. **Tech Sites:** Tom's Hardware, AnandTech memory sections

### **Cron Job IDs**
- `wm-brief-9am`: `961d6e78-c9a4-4b6a-b723-15dfcb748c63`
- `wm-brief-1pm`: `54262265-2660-48f0-9f07-4b69835fc57f`
- `wm-brief-6pm`: `d38d04a6-4544-41f7-8072-b9f1593f8593`
- `wm-brief-10pm`: `7885386b-8842-4a7e-a0e3-1b0f01977911`
- `memory-price-tracker`: `fea3d1a2-1159-45fd-990f-3148308eed70`
- `8am-daily-report`: `35c4f977-8809-459c-899c-25ddc503746a`
- `rag-daily-update`: `4a15f057-39e6-4a65-b0e1-c51df932f4f6`

### **File Structure**
```
workspace/
├── worldmonitor_with_integration.py    # Main World Monitor script
├── save_bloomberg_report.sh           # Obsidian/GitHub integration
├── production_scraper.py              # Memory price scraper
├── production_scraper_cron.sh         # Memory scraper cron wrapper
├── memory/                            # Daily memory logs
│   └── 2026-04-06.md                  # Today's activities
├── memory_prices/                     # Memory price data
│   ├── production_data_*.json         # Scraped data
│   ├── production_report_*.txt        # Analysis reports
│   └── manual_prices.json             # Manual entry template
└── MEMORY.md                          # This file (long-term memory)
```

## User Preferences & Patterns

### **Communication Style**
- Prefers direct, actionable information
- Values transparency about limitations
- Appreciates verification of claims
- Likes systematic, scheduled updates

### **Technical Preferences**
- **Report Titles:** "World Monitor Brief" format
- **Schedule:** 9 AM, 1 PM, 6 PM, 10 PM SGT
- **Data Sources:** Prefers actual scraping over theoretical APIs
- **Integration:** Obsidian + GitHub workflow established

### **Quality Standards**
1. **No hallucinations** - real data only
2. **Complete reports** - no truncation
3. **Working URLs** - verified accessibility
4. **Transparent limitations** - honest about what's possible
5. **Scheduled reliability** - consistent delivery times

## Lessons for Future Development

### **What Works Well**
1. **Web scraping framework** - actually extracts real data
2. **Bloomberg-style formatting** - professional presentation
3. **Automated scheduling** - reliable cron jobs
4. **Integration pipeline** - Obsidian + GitHub workflow
5. **Memory system** - tracks decisions and learnings

### **Important Technical Lessons**

**1. Cron Timezone Conversion:**
- When scheduling in Asia/Singapore (GMT+8):
  - 9 AM SGT = 1 AM UTC
  - 1 PM SGT = 5 AM UTC
  - 6 PM SGT = 10 AM UTC
  - 10 PM SGT = 2 PM UTC
- **Mistake made:** Initially scheduled 6 PM SGT as 10 PM UTC (wrong)
- **Lesson:** Double-check timezone conversions for cron schedules

**2. OpenClaw Cron Automation Issue:**
- **Problem:** Cron jobs configured correctly but not auto-triggering
- **Symptoms:** Jobs show "Last: Xh ago" but don't actually run
- **Workaround:** Manual triggers work perfectly
- **Root cause:** OpenClaw cron scheduler/service may have issues
- **Lesson:** Need to verify cron scheduler is actually running

**3. Monitoring Strategy:**
- Check Obsidian files for actual report creation times
- Don't rely solely on cron job "Last run" status
- Set up verification for each scheduled report
- Have manual trigger ready as backup

### **DRAMExchange Memory Price Sources (Tested 2026-04-07)**
**Primary data sources for memory pricing:**
1. https://www.dramexchange.com/Price/Dram_Spot
2. https://www.dramexchange.com/Price/Module_Spot
3. https://www.dramexchange.com/Price/Flash_Spot
4. https://www.dramexchange.com/Price/GDDR_Spot
5. https://www.dramexchange.com/Price/Wafer_Spot
6. https://www.dramexchange.com/Price/MemoryCard_Spot
7. https://www.dramexchange.com/Price/NationalContractDramDetail
8. https://www.dramexchange.com/Price/NationalContractFlashDetail

**Key Discovery:**
- **Requires login** - All pages redirect to login
- **$4.00 prices** are from login page, not actual memory data
- **Authentication needed** for actual price access
- **Alternative sources required** for automated scraping

**Status:** URLs accessible but data protected behind login
**Lesson:** Industry price data often requires paid subscriptions or authentication

### **Areas for Improvement**
1. **Error handling** - better recovery from failed scrapes
2. **Data validation** - verify extracted prices are meaningful
3. **Rate limiting** - respect website terms of service
4. **Alternative sources** - more fallback options
5. **Alert system** - notify on significant price changes

## Key Dates & Milestones

### **2026-04-06 - Major System Updates**
1. **Fixed WorldMonitor truncation** - now saves complete reports
2. **Implemented real web scraping** - no more fake data
3. **Updated schedule** - 4x daily World Monitor Briefs
4. **Created memory price tracker** - with actual scraping
5. **Established transparency** - honest about limitations

### **Ongoing Systems**
- **World Monitor Brief:** 4x daily at 9 AM, 1 PM, 6 PM, 10 PM SGT
- **Memory Price Tracker:** 1x daily at 9 AM SGT
- **Daily Report:** 1x daily at 8 AM SGT
- **RAG Update:** 1x daily at 2 AM SGT

## Future Considerations

### **Short-term (Next Week)**
1. Monitor new schedule reliability
2. Verify memory price extraction accuracy
3. Collect user feedback on report formats
4. Optimize scraping patterns

### **Medium-term (Next Month)**
1. Expand to additional data sources
2. Implement price change alerts
3. Add historical trend analysis
4. Improve error recovery

### **Long-term (Next Quarter)**
1. Consider paid data sources if needed
2. Build predictive models
3. Expand to other commodity tracking
4. Develop API for external access

---

**Last Updated:** 2026-04-06  
**Next Review:** Weekly review of this file to distill new learnings  
**Purpose:** Serve as reference for consistent decision-making and avoid repeating mistakes

**Identity Note:** Originally introduced as "Claw" on 2026-04-06, renamed to "yoyoclaw" per user request.