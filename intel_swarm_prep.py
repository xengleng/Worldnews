#!/usr/bin/env python3
"""
Intelligence Swarm Orchestrator — Task Generator
================================================
This script does NOT run LLMs directly. It:
1. Parses RSS feeds for all 3 domains
2. Saves raw intelligence data to scratch/
3. Prints the synthesizer task to stdout

The actual LLM reasoning (sub-agent spawning, synthesis, red-teaming)
is handled by the AI agent that reads these files.

Usage (manual):
  python intel_swarm_prep.py

Usage (cron — feeds into agent):
  python intel_swarm_prep.py > /tmp/intel_task.txt
  # Agent reads /tmp/intel_task.txt and runs the full swarm
"""

import json
import feedparser
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import time
import re

WORKSPACE = Path("/home/yeoel/.openclaw/workspace")
SCRATCH_DIR = WORKSPACE / "intel_swarm" / "scratch"
RESULTS_DIR = WORKSPACE / "intel_swarm" / "results"
SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

RUN_TS = datetime.utcnow().strftime("%Y%m%d_%H%M")
SGT_TS = datetime.now().strftime("%Y-%m-%d %I:%M %p SGT")
UTC_TS = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

# ─────────────────────────────────────────────
# FEEDS — WorldMonitor source categories
# ─────────────────────────────────────────────
NEWSAPI_KEY = "3a37ab6fc0aa41b48bfa1ce7ff264782"
NEWSAPI_BASE = "https://newsapi.org/v2"

FEEDS = {
    "geopolitics": [
        {"name": "BBC World", "url": "https://feeds.bbci.co.uk/news/world/rss.xml", "cat": "politics"},
        {"name": "Reuters World", "url": "https://news.google.com/rss/search?q=site:reuters.com+world&hl=en-US&gl=US&ceid=US:en", "cat": "politics"},
        {"name": "CNN World", "url": "https://news.google.com/rss/search?q=site:cnn.com+world+news+when:1d&hl=en-US&gl=US&ceid=US:en", "cat": "politics"},
        {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml", "cat": "middleeast"},
        {"name": "Defense One", "url": "https://www.defenseone.com/rss/all/", "cat": "intel"},
        {"name": "Foreign Policy", "url": "https://foreignpolicy.com/feed/", "cat": "intel"},
        {"name": "CNA", "url": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml", "cat": "asia"},
        {"name": "SCMP", "url": "https://www.scmp.com/rss/91/feed/", "cat": "asia"},
        {"name": "BBC Africa", "url": "https://feeds.bbci.co.uk/news/world/africa/rss.xml", "cat": "africa"},
        {"name": "CrisisWatch", "url": "https://www.crisisgroup.org/rss", "cat": "crisis"},
        {"name": "Oryx OSINT", "url": "https://www.oryxspioenkop.com/feeds/posts/default?alt=rss", "cat": "intel"},
        {"name": "RUSI", "url": "https://news.google.com/rss/search?q=site:rusi.org&hl=en-US&gl=US&ceid=US:en", "cat": "intel"},
        {"name": "Krebs Security", "url": "https://krebsonsecurity.com/feed/", "cat": "cyber"},
        {"name": "NewsAPI US", "url": f"{NEWSAPI_BASE}/top-headlines?country=us&category=general&pageSize=15&apiKey={NEWSAPI_KEY}", "cat": "politics"},
        {"name": "NewsAPI UK", "url": f"{NEWSAPI_BASE}/top-headlines?country=gb&category=general&pageSize=15&apiKey={NEWSAPI_KEY}", "cat": "politics"},
        {"name": "NewsAPI China", "url": f"{NEWSAPI_BASE}/top-headlines?country=cn&category=general&pageSize=15&apiKey={NEWSAPI_KEY}", "cat": "asia"},
        {"name": "NewsAPI Russia", "url": f"{NEWSAPI_BASE}/top-headlines?country=ru&category=general&pageSize=15&apiKey={NEWSAPI_KEY}", "cat": "politics"},
    ],
    "finance": [
        {"name": "CNBC", "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html", "cat": "markets"},
        {"name": "Yahoo Finance", "url": "https://finance.yahoo.com/rss/topstories", "cat": "markets"},
        {"name": "MarketWatch", "url": "https://news.google.com/rss/search?q=site:marketwatch.com+markets&hl=en-US&gl=US&ceid=US:en", "cat": "markets"},
        {"name": "Bloomberg Markets", "url": "https://news.google.com/rss/search?q=site:bloomberg.com+markets&hl=en-US&gl=US&ceid=US:en", "cat": "markets"},
        {"name": "Reuters Markets", "url": "https://news.google.com/rss/search?q=site:reuters.com+markets&hl=en-US&gl=US&ceid=US:en", "cat": "markets"},
        {"name": "Federal Reserve", "url": "https://www.federalreserve.gov/feeds/press_all.xml", "cat": "centralbanks"},
        {"name": "CoinDesk", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/", "cat": "crypto"},
        {"name": "Cointelegraph", "url": "https://cointelegraph.com/rss", "cat": "crypto"},
        {"name": "Oil & Gas", "url": "https://news.google.com/rss/search?q=(oil+price+OR+OPEC+OR+crude+oil+OR+WTI+OR+Brent)&hl=en-US&gl=US&ceid=US:en", "cat": "commodities"},
        {"name": "Gold & Metals", "url": "https://news.google.com/rss/search?q=(gold+price+OR+silver+price+OR+copper+OR+precious+metals)&hl=en-US&gl=US&ceid=US:en", "cat": "commodities"},
        {"name": "Central Bank Rates", "url": "https://news.google.com/rss/search?q=(central+bank+OR+interest+rate+OR+rate+decision)&hl=en-US&gl=US&ceid=US:en", "cat": "centralbanks"},
        {"name": "Economic Data", "url": "https://news.google.com/rss/search?q=(CPI+OR+inflation+OR+GDP+OR+jobs+report)&hl=en-US&gl=US&ceid=US:en", "cat": "economic"},
        {"name": "Trade & Tariffs", "url": "https://news.google.com/rss/search?q=(tariff+OR+trade+war+OR+sanctions)&hl=en-US&gl=US&ceid=US:en", "cat": "trade"},
        {"name": "SEC", "url": "https://www.sec.gov/news/pressreleases.rss", "cat": "regulation"},
        {"name": "NewsAPI Business", "url": f"{NEWSAPI_BASE}/top-headlines?category=business&language=en&pageSize=15&apiKey={NEWSAPI_KEY}", "cat": "markets"},
    ],
    "climate": [
        {"name": "Climate News", "url": "https://news.google.com/rss/search?q=climate+change+extreme+weather&hl=en-US&gl=US&ceid=US:en", "cat": "climate"},
        {"name": "FEMA", "url": "https://www.fema.gov/outbreaks/disasters.rss", "cat": "disasters"},
        {"name": "ReliefWeb", "url": "https://reliefweb.int/updates/rss", "cat": "disasters"},
        {"name": "USGS Earthquakes", "url": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_month.csv", "cat": "disasters"},
        {"name": "WHO", "url": "https://www.who.int/feeds/entity/csr/don/en/rss.xml", "cat": "health"},
        {"name": "Wildfire News", "url": "https://news.google.com/rss/search?q=(wildfire+OR+bushfire+OR+forest+fire)&hl=en-US&gl=US&ceid=US:en", "cat": "disasters"},
        {"name": "Flood News", "url": "https://news.google.com/rss/search?q=(flood+OR+flooding+OR+hurricane+OR+typhoon)&hl=en-US&gl=US&ceid=US:en", "cat": "disasters"},
        {"name": "Drought News", "url": "https://news.google.com/rss/search?q=(drought+OR+water+crisis+OR+heatwave)&hl=en-US&gl=US&ceid=US:en", "cat": "climate"},
        {"name": "NewsAPI Science", "url": f"{NEWSAPI_BASE}/top-headlines?category=science&language=en&pageSize=15&apiKey={NEWSAPI_KEY}", "cat": "climate"},
    ],
}

ALERT_KEYWORDS = {
    "CRITICAL": ["war", "invasion", "nuclear", "coup", "assassination", "mass casualty", "market crash", "bankruptcy"],
    "HIGH": ["sanctions", "military", "airstrike", "protest", "earthquake", "flood", "hurricane", "rate cut", "rate hike"],
    "MEDIUM": ["diplomatic", "tension", "inflation", "GDP", "tariff", "cyberattack", "hack"],
}


def fetch_feed(url: str, timeout: int = 10) -> Optional[str]:
    """Fetch feed content via curl."""
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", str(timeout), "-L", "-A", 
             "Mozilla/5.0 (compatible; IntelSwarm/1.0)", url],
            capture_output=True, text=True, timeout=timeout + 5
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception as e:
        print(f"  ⚠ curl error for {url}: {e}", file=sys.stderr)
    return None


def parse_rss_items(xml_content: str, max_items: int = 15) -> list:
    """Parse RSS/Atom XML and extract items."""
    items = []
    try:
        feed = feedparser.parse(xml_content)
        for entry in feed.entries[:max_items]:
            # Extract title
            title = getattr(entry, 'title', '') or ''
            title = re.sub(r'<[^>]+>', '', title).strip()
            
            # Extract link
            link = getattr(entry, 'link', '') or ''
            if hasattr(entry, 'links'):
                for l in entry.links:
                    if l.get('type', '').startswith('text/html'):
                        link = l.get('href', link)
                        break
            
            # Extract published date
            published = getattr(entry, 'published', '') or getattr(entry, 'updated', '') or ''
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                from time import mktime
                try:
                    dt = datetime.fromtimestamp(mktime(entry.published_parsed))
                    published = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            
            # Extract summary/description
            summary = getattr(entry, 'summary', '') or getattr(entry, 'description', '') or ''
            summary = re.sub(r'<[^>]+>', '', summary).strip()
            if len(summary) > 300:
                summary = summary[:297] + "..."
            
            # Extract source name from feed
            source = getattr(feed.feed, 'title', '') or ''
            
            if title:
                items.append({
                    "title": title,
                    "link": link,
                    "published": published,
                    "summary": summary,
                    "source": source,
                })
    except Exception as e:
        print(f"  ⚠ Parse error: {e}", file=sys.stderr)
    return items


def assess_alert_level(title: str, summary: str) -> str:
    """Assess alert level based on keywords."""
    text = (title + " " + summary).lower()
    for level in ["CRITICAL", "HIGH", "MEDIUM"]:
        for kw in ALERT_KEYWORDS.get(level, []):
            if kw.lower() in text:
                return level
    return "LOW"


def parse_newsapi_items(json_content: str, max_items: int = 15) -> list:
    """Parse NewsAPI JSON response and extract items."""
    import json as json_lib
    items = []
    try:
        data = json_lib.loads(json_content)
        if data.get("status") != "ok":
            return items
        for article in data.get("articles", [])[:max_items]:
            title = article.get("title", "") or ""
            url = article.get("url", "") or ""
            desc = article.get("description", "") or ""
            source = article.get("source", {}).get("name", "NewsAPI") or "NewsAPI"
            published = article.get("publishedAt", "")[:16]
            if title and title != "[Removed]":
                items.append({
                    "title": title,
                    "link": url,
                    "published": published,
                    "summary": desc[:300] + "..." if len(desc) > 300 else desc,
                    "source": source,
                })
    except Exception as e:
        print(f"  ⚠ NewsAPI parse error: {e}", file=sys.stderr)
    return items


def is_newsapi_url(url: str) -> bool:
    return "newsapi.org" in url


def process_domain(domain: str, feeds: list) -> dict:
    """Process all feeds for a domain and return structured data."""
    print(f"\n[{domain.upper()}] Processing {len(feeds)} feeds...")
    
    all_items = []
    source_stats = {}
    
    for feed in feeds:
        url = feed["url"]
        cat = feed["cat"]
        name = feed["name"]
        
        # Skip CSV feeds (USGS earthquakes - different format)
        if url.endswith('.csv'):
            content = fetch_feed(url)
            if content:
                lines = content.strip().split('\n')
                for line in lines[:5]:
                    parts = line.split(',')
                    if len(parts) >= 5:
                        try:
                            all_items.append({
                                "title": f"M{parts[4]} - {parts[13] if len(parts) > 13 else 'Unknown'}",
                                "link": f"https://earthquake.usgs.gov/earthquakes/eventpage/{parts[13] if len(parts) > 13 else 'unknown'}",
                                "published": parts[0] if len(parts) > 0 else "",
                                "summary": f"Location: {parts[13] if len(parts) > 13 else 'Unknown'}, Depth: {parts[3]}km",
                                "source": "USGS",
                                "category": cat,
                            })
                        except:
                            pass
                source_stats[name] = len(lines) - 1
            continue
        
        # Handle NewsAPI JSON responses
        if is_newsapi_url(url):
            content = fetch_feed(url)
            if not content:
                print(f"  ⚠ No content: {name}")
                continue
            items = parse_newsapi_items(content)
            for item in items:
                item["category"] = cat
                item["alert_level"] = assess_alert_level(item["title"], item["summary"])
                all_items.append(item)
            source_stats[name] = len(items)
            print(f"  ✓ {name}: {len(items)} items")
            continue

        # Skip CSV feeds (USGS earthquakes - different format)
        if url.endswith('.csv'):
            content = fetch_feed(url)
            if content:
                lines = content.strip().split('\n')
                for line in lines[:5]:
                    parts = line.split(',')
                    if len(parts) >= 5:
                        try:
                            all_items.append({
                                "title": f"M{parts[4]} - {parts[13] if len(parts) > 13 else 'Unknown'}",
                                "link": f"https://earthquake.usgs.gov/earthquakes/eventpage/{parts[13] if len(parts) > 13 else 'unknown'}",
                                "published": parts[0] if len(parts) > 0 else "",
                                "summary": f"Location: {parts[13] if len(parts) > 13 else 'Unknown'}, Depth: {parts[3]}km",
                                "source": "USGS",
                                "category": cat,
                            })
                        except:
                            pass
                source_stats[name] = len(lines) - 1
            continue
        
        content = fetch_feed(url)
        if not content:
            print(f"  ⚠ No content: {name}")
            continue
        
        items = parse_rss_items(content)
        for item in items:
            item["category"] = cat
            item["alert_level"] = assess_alert_level(item["title"], item["summary"])
            all_items.append(item)
        
        source_stats[name] = len(items)
        print(f"  ✓ {name}: {len(items)} items")
    
    # Sort by alert level
    level_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    all_items.sort(key=lambda x: level_order.get(x.get("alert_level", "LOW"), 4))
    
    # Limit to top items
    all_items = all_items[:50]
    
    print(f"  → Total: {len(all_items)} items from {len(source_stats)} sources")
    
    return {
        "domain": domain,
        "timestamp": RUN_TS,
        "sgt_time": SGT_TS,
        "utc_time": UTC_TS,
        "total_items": len(all_items),
        "items": all_items,
        "sources": [{"name": k, "count": v} for k, v in source_stats.items()],
    }


def save_prepped_data(domain: str, data: dict):
    """Save prepped data to scratch directory."""
    out_file = SCRATCH_DIR / f"{domain}_{RUN_TS}_raw.json"
    out_file.write_text(json.dumps(data, indent=2))
    print(f"  💾 Saved: {out_file.name}")
    return out_file


def generate_agent_task(domain: str, data_file: Path) -> str:
    """Generate the LLM task for a domain agent."""
    
    prompt = f"""You are the Intelligence Analyst for **{domain.upper()}**.

## DATA AVAILABLE
Read the prepped intelligence data:
`{data_file}`

## YOUR TASK
1. Read the JSON data from `{data_file}`
2. Analyze the items — focus on what's significant from the last 6-12 hours
3. Identify:
   - Top insights (max 10, most important first)
   - Expert opinions (bullish vs bearish views)
   - Cross-source patterns
   - Blind spots / underreported topics
4. Output a structured JSON report to: `{RESULTS_DIR}/{domain}_{RUN_TS}.json`

## OUTPUT SCHEMA
```json
{{
  "agent": "{domain}",
  "timestamp": "{RUN_TS}",
  "run_ts_utc": "{datetime.utcnow().isoformat()}Z",
  "insights": [
    {{
      "headline": "string",
      "summary": "string (2-3 sentences)",
      "category": "string",
      "alert_level": "LOW|MEDIUM|HIGH|CRITICAL",
      "source_names": ["string"],
      "source_urls": ["string (verified URLs only)"],
      "published": "string"
    }}
  ],
  "expert_opinions": {{
    "positive": ["string"],
    "negative": ["string"],
    "sources": ["string"]
  }},
  "patterns": ["string"],
  "blind_spots": ["string"]
}}
```

## RULES
- Extract max 10 insights, most significant first
- Include ONLY real, verified URLs from the source data
- If items lack URLs, do NOT fabricate them — mark source_urls as []
- alert_level: CRITICAL=war/nuclear/coup/market crash, HIGH=military/sanctions/major disaster, MEDIUM=economic data/diplomatic tension, LOW=routine
- Save JSON to: `{RESULTS_DIR}/{domain}_{RUN_TS}.json`
"""
    return prompt


def generate_synthesizer_task() -> str:
    """Generate the synthesizer task."""
    return f"""You are the Chief Intelligence Synthesizer.

## RAW DATA FILES (read these)
- `{RESULTS_DIR}/geopolitics_{RUN_TS}.json`
- `{RESULTS_DIR}/finance_{RUN_TS}.json`
- `{RESULTS_DIR}/climate_{RUN_TS}.json`

## YOUR TASK
1. Read all 3 domain JSON reports
2. Cross-correlate insights across domains
3. Identify patterns that span multiple domains
4. Find "alpha" — angles or signals not covered elsewhere
5. Red-team: remove duplicates, resolve conflicts, validate URLs
6. Output Master Intelligence Report JSON

## OUTPUT SCHEMA
```json
{{
  "report_type": "MASTER_INTELLIGENCE_REPORT",
  "timestamp": "{RUN_TS}",
  "sgt_time": "{SGT_TS}",
  "utc_time": "{UTC_TS}",
  "executive_summary": "string (3-5 sentence strategic overview)",
  "key_themes": [
    {{
      "theme": "string",
      "description": "string",
      "supporting_evidence": ["string"],
      "confidence": "HIGH|MEDIUM|LOW"
    }}
  ],
  "alpha_opportunities": [
    {{
      "angle": "string",
      "rationale": "string",
      "timeframe": "SHORT|MEDIUM|LONG",
      "risk": "HIGH|MEDIUM|LOW"
    }}
  ],
  "cross_domain_patterns": ["string"],
  "blind_spots": ["string"],
  "reference_index": [
    {{"name": "string", "url": "string", "used_by": "string"}}
  ],
  "alerts_summary": {{
    "critical": ["string"],
    "high": ["string"],
    "medium": ["string"],
    "low": ["string"]
  }},
  "telegram_summary": {{
    "crisis_line": "string (1-line headline — MUST use ✅ for positive signals, ❌ for negative, ⚠️ for mixed. e.g. '✅ Ceasefire talks reportedly resuming' vs '❌ Naval blockade ongoing — ceasefire collapse risk HIGH')",
    "executive": "string (2-3 sentence strategic overview — note divergences and compound risks)",
    "critical_alerts": ["string (one per line, bullet format)"],
    "high_alerts": ["string (one per line, bullet format)"],
    "alpha": "string (1-2 alpha angles)"
  }}
}}
```

## SAVE TO
`{RESULTS_DIR}/master_{RUN_TS}.json`

## ALSO GENERATE MARKDOWN
After saving the JSON, also write a markdown version to:
`{RESULTS_DIR}/../reports/intel_report_{RUN_TS}.md`

Use this format:
```
---
title: Intelligence Report — {SGT_TS}
date: {RUN_TS}
type: intelligence-report
---

# 🧠 Master Intelligence Report
**Generated:** {SGT_TS} | {UTC_TS}

## Executive Summary
[executive_summary]

## Key Themes
[for each theme: ### theme name, description, evidence]

## Alpha Opportunities
[for each: ### angle, rationale, timeframe, risk]

## Alerts Summary
[CRITICAL/HIGH/MEDIUM/LOW sections]

## Telegram Summary (for Phase 3 delivery)
[telegram_summary.crisis_line]
[telegram_summary.executive]
CRITICAL: [bulleted]
HIGH: [bulleted]
Alpha: [telegram_summary.alpha]

## Reference Index
[table of sources]
```
"""


def main():
    print(f"\n{'='*60}")
    print(f"🧠 INTELLIGENCE SWARM PREP — {SGT_TS}")
    print(f"{'='*60}\n")
    
    # Step 1: Process all domains
    print("[1/3] 🕷️ Scraping RSS feeds...")
    domain_files = {}
    
    for domain, feeds in FEEDS.items():
        data = process_domain(domain, feeds)
        data_file = save_prepped_data(domain, data)
        domain_files[domain] = data_file
    
    # Step 2: Generate agent prompts
    print("\n[2/3] 📝 Generating agent tasks...")
    agent_tasks = {}
    for domain, data_file in domain_files.items():
        task = generate_agent_task(domain, data_file)
        task_file = SCRATCH_DIR / f"task_{domain}_{RUN_TS}.txt"
        task_file.write_text(task)
        agent_tasks[domain] = str(task_file)
        print(f"  ✓ {domain}: {task_file.name}")
    
    # Step 3: Generate synthesizer task
    synth_task = generate_synthesizer_task()
    synth_task_file = SCRATCH_DIR / f"task_synthesizer_{RUN_TS}.txt"
    synth_task_file.write_text(synth_task)
    print(f"  ✓ synthesizer: {synth_task_file.name}")
    
    # Summary for the agent
    print(f"\n{'='*60}")
    print("📋 SWARM READY — Next Steps")
    print(f"{'='*60}")
    print(f"""
Run the following 4 tasks (can run in parallel):
""")
    for domain, task_file in agent_tasks.items():
        print(f"  🐟 {domain.upper()}: sessions_spawn(task=read('{task_file}') + execute + save)")
    print(f"""
  🧠 SYNTHESIZER: sessions_spawn(task=read('{synth_task_file}') + execute + save)
""")
    print(f"Files will be saved to: {RESULTS_DIR}/")
    print(f"Markdown report: {RESULTS_DIR}/../reports/intel_report_{RUN_TS}.md")
    print(f"{'='*60}\n")
    
    # Write the full orchestrator task for sessions_spawn
    orchestrator_task = f"""
# YOYOCLAW INTELLIGENCE SWARM — ORCHESTRATOR TASK
# Run TS: {RUN_TS} | SGT: {SGT_TS} | UTC: {UTC_TS}

## MISSION
You are the Lead Intelligence Orchestrator. Execute this swarm in 3 phases.

---

### PHASE 1: PARALLEL ANALYSIS (spawn 3 sub-agents)

Spawn these 3 sub-agents in parallel (use sessions_spawn with mode="run", runtime="subagent"):

**Agent A — GEOPOLITICS** 🌍
Task file: {agent_tasks['geopolitics']}
Read the task file, execute, save to {RESULTS_DIR}/geopolitics_{RUN_TS}.json

**Agent B — FINANCE** 💹
Task file: {agent_tasks['finance']}
Read the task file, execute, save to {RESULTS_DIR}/finance_{RUN_TS}.json

**Agent C — CLIMATE** 🌡️
Task file: {agent_tasks['climate']}
Read the task file, execute, save to {RESULTS_DIR}/climate_{RUN_TS}.json

Wait for all 3 to complete (poll for result files).

---

### PHASE 2: SYNTHESIS

After all 3 agents complete, run the synthesizer:

**Agent D — SYNTHESIZER** 🧠
Task file: {synth_task_file}
Read the task file, execute, save:
- JSON: {RESULTS_DIR}/master_{RUN_TS}.json
- Markdown: {WORKSPACE}/intel_swarm/reports/intel_report_{RUN_TS}.md

---

### PHASE 3: DISTRIBUTION

1. Save the markdown report to Obsidian vault:
   Target: Worldnews/Daily Intel/Intel-Report-{RUN_TS}
   (Use obsidian-cli or direct file copy)

2. GitHub push:
   ```
   cd {WORKSPACE}
   git add intel_swarm/reports/intel_report_{RUN_TS}.md intel_swarm/results/master_{RUN_TS}.json
   git commit -m "Intel Report {RUN_TS} — {SGT_TS}"
   git push
   ```

3. Send Telegram summary to YEO:
   - Extract the "Telegram Summary" section from the markdown report you just generated
   - Send exactly that section as the Telegram message
   - Include: crisis_line, executive, CRITICAL bullets, HIGH bullets, alpha

---

Confirm completion with a brief status report.
"""
    
    orchestrator_file = SCRATCH_DIR / f"orchestrator_{RUN_TS}.txt"
    orchestrator_file.write_text(orchestrator_task)
    print(f"📄 Full orchestrator task: {orchestrator_file}")


if __name__ == "__main__":
    main()
