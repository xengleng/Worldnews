# Projects & Decisions

## Stock Monitoring System
- Built incremental features: gold, Singapore stocks, forex pairs
- Added FedWatch integration for expert analysis
- Evolved from simple reports to macro‑driven structure

## Report Evolution
1. Basic stock report
2. Added forex calculations (SGD/MYR direct)
3. Added gold and Singapore stocks
4. Integrated FedWatch monitoring
5. Restructured as macro‑driven reports

## Home Loan Analysis
- Created mortgage comparison tool
- Sample output: `home_loan_sample_20260404.txt`

## RAG Setup
- Topic‑based flat files (finance, tech, projects)
- Lightweight FAISS + sentence‑transformers
- Avoid compaction, keep files separate

## From 2026-04-04

### **Next Report:**

The updated monitoring will be included in the **next daily report at 8:00 AM Singapore time** (April 5, 2026).

### **Next Report:**

### **New Report Structure:**

### **Next Report: Tomorrow 8:00 AM**

### **📊 New Report Structure:**

- `daily_report_with_homeloan.py` - Main integrated report
- `home_loan_analysis.py` - Standalone home loan analysis
- `home_loan_sample_20260404.txt` - Sample output
- `full_report_20260404_1337.txt` - Complete integrated sample

**Your daily 8 AM report will now include professional home loan rate analysis alongside market insights, providing a complete financial picture for Singapore homeowners and investors.**
user: Conversation info (untrusted metadata):
```json
{
  "message_id": "332",
  "sender_id": "1580782173",
  "sender": "YEO",
  "timestamp": "Sat 2026-04-04 14:37 GMT+8"
}
```

Sender (untrusted metadata):
```json
{
  "label": "YEO (1580782173)",
  "id": "1580782173",
  "name": "YEO"
}
```

Can you read out “i am
Invest bot”?
assistant: [[tts:male]]I am Invest Bot.[[/tts]]


## From 2026-04-05

## 📈 **Example Output** (from test run):
```
📰 WORLDMONITOR NEWS UPDATE
Time: 2026-04-05 08:26 SGT
Articles: 15 new items

**GEOPOLITICS**
1. Iran says US-Israeli attacks on Mahshahr Petrochemical Zone...
   Source: Al Jazeera
   Link: https://...

**TECH**
1. Demand for autism care is soaring
   Source: Hacker News
   Link: https://...
```

The system is now fully automated! You'll start receiving updates on schedule. Want me to adjust any feed selections or timing?
user: System: [2026-04-05 08:26:24 GMT+8] Exec completed (young-sa, code 0) :: -concept/06-mobile-devices/02-mdvm/">https://bmi.usercontent.opencod... Link: https://bmi.usercontent.opencode.de/eudi-wallet/wallet-development-documentation-public/latest/archit…

Conversation info (untrusted metadata):
```json
{
  "message_id": "523",
  "sender_id": "1580782173",
  "sender": "YEO",
  "timestamp": "Sun 2026-04-05 08:42 GMT+8"
}
```

Sender (untrusted metadata):
```json
{
  "label": "YEO (1580782173)",
  "id": "1580782173",
  "name": "YEO"
}
```

Run a full report on worldmonitor now.
assistant: [[reply_to_current]] I'll run a comprehensive analysis of the WorldMonitor codebase now to give you a full report on its architecture, data sources, and potential integration points.
assistant: [[reply_to_current]] The analysis timed out. Let me run a quicker manual analysis of WorldMonitor's key components.
assistant: Let me read the key documentation files.


## From 2026-04-06

## 📋 **Complete Scheduled System**

### 📊 **Market Reports**

| Job | Schedule | Purpose |
|-----|----------|---------|
| `8am-daily-report` | 8 AM daily | Market report with RAG insights |
| `test-830am-report` | 8:30 AM today | Test verification |

**Starting today:**
1. **8:30 AM** – Test report (verification)
2. **9 PM** – First WorldMonitor news update
3. **3 AM** – Second news update

**Starting tomorrow:**
1. **2 AM** – RAG knowledge base update
2. **8 AM** – Daily market report with RAG
3. **9 AM** – WorldMonitor news
4. **3 PM** – WorldMonitor news  
5. **9 PM** – WorldMonitor news
6. **3 AM** – WorldMonitor news

**Total:** 6 scheduled updates per day (4 news + 1 market report + 1 maintenance).


## From 2026-04-07

### **Evidence:**
1. **9 AM World Monitor Brief:** ❌ NOT sent automatically
2. **9 AM Memory Price Tracker:** ❌ NOT sent automatically  
3. **Existing reports from today:**
   - 01:01 SGT: World Monitor Brief (middle of night - wrong time)
   - 05:00 SGT: World Monitor Brief (early morning - wrong time)
   - 01:00 SGT: Memory Price Report (middle of night - wrong time)


## From 2026-04-13

### Scheduled Updates That Day
| Time | Report |
|------|--------|
| 9:00 AM | World Monitor Brief |
| 1:00 PM | World Monitor Brief |
| 6:00 PM | World Monitor Brief |
| 10:00 PM | World Monitor Brief |


## From 2026-04-19

### Intel Swarm Pipeline
1. `intel_swarm_prep.py` → scrapes RSS feeds → `intel_swarm/results/{domain}_{TS}_raw.json`
2. Spawns 3 sub-agents (geopolitics, finance, climate) via `sessions_spawn`
3. Synthesizer combines → `master_{TS}.json` + `intel_report_{TS}.md`
4. Saves to Obsidian + GitHub push
5. Cron: `intel_swarm/orchestrator_isolated.py` for isolated sessions

## User Preferences
- YEO values: Direct communication, working systems, no hallucinations
- YEO hates: Scout finding important news but not reporting it (today's complaint)
- YEO prefers: MiniMax over DeepSeek
- No filler words — just help
