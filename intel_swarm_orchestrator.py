#!/usr/bin/env python3
"""
Intelligence Swarm Orchestrator
Lead Orchestrator for the yoyoclaw Intelligence System

Schedules: 9AM, 3PM, 9PM SGT (1:00, 7:00, 13:00 UTC)
Spawns 4 parallel sub-agents → collects → synthesizes → saves → GitHub push → Telegram alert
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
import hashlib
import sys
import os

WORKSPACE = Path("/home/yeoel/.openclaw/workspace")
INTEL_DIR = WORKSPACE / "intel_swarm"
RESULTS_DIR = INTEL_DIR / "results"
SCRATCH_DIR = INTEL_DIR / "scratch"
AGENT_PROMPTS_DIR = INTEL_DIR / "prompts"
FINAL_REPORTS_DIR = INTEL_DIR / "reports"

# Timestamps
RUN_TS = datetime.utcnow().strftime("%Y%m%d_%H%M")
SGT_TS = datetime.now().strftime("%Y-%m-%d %I:%M %p SGT")
UTC_TS = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

# Ensure directories
for d in [RESULTS_DIR, SCRATCH_DIR, AGENT_PROMPTS_DIR, FINAL_REPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────
# Domain → WorldMonitor feed categories
# ─────────────────────────────────────────────
FEED_MAP = {
    "geopolitics": {
        "politics": [
            {"name": "BBC World", "url": "https://feeds.bbci.co.uk/news/world/rss.xml"},
            {"name": "Guardian World", "url": "https://www.theguardian.com/world/rss"},
            {"name": "Reuters World", "url": "https://news.google.com/rss/search?q=site:reuters.com+world&hl=en-US&gl=US&ceid=US:en"},
            {"name": "CNN World", "url": "https://news.google.com/rss/search?q=site:cnn.com+world+news+when:1d&hl=en-US&gl=US&ceid=US:en"},
            {"name": "AP News", "url": "https://news.google.com/rss/search?q=site:apnews.com&hl=en-US&gl=US&ceid=US:en"},
        ],
        "us": [
            {"name": "Reuters US", "url": "https://news.google.com/rss/search?q=site:reuters.com+US&hl=en-US&gl=US&ceid=US:en"},
            {"name": "NPR News", "url": "https://feeds.npr.org/1001/rss.xml"},
            {"name": "Politico", "url": "https://rss.politico.com/politics-news.xml"},
            {"name": "The Hill", "url": "https://thehill.com/news/feed"},
        ],
        "europe": [
            {"name": "France 24", "url": "https://www.france24.com/en/rss"},
            {"name": "EuroNews", "url": "https://www.euronews.com/rss?format=xml"},
            {"name": "DW News", "url": "https://rss.dw.com/xml/rss-en-all"},
            {"name": "Le Monde", "url": "https://www.lemonde.fr/en/rss/une.xml"},
            {"name": "BBC Russia", "url": "https://feeds.bbci.co.uk/russian/rss.xml"},
        ],
        "middleeast": [
            {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml"},
            {"name": "BBC Middle East", "url": "https://feeds.bbci.co.uk/news/world/middle_east/rss.xml"},
            {"name": "Guardian ME", "url": "https://www.theguardian.com/world/middleeast/rss"},
            {"name": "Oryx OSINT", "url": "https://www.oryxspioenkop.com/feeds/posts/default?alt=rss"},
        ],
        "asia": [
            {"name": "BBC Asia", "url": "https://feeds.bbci.co.uk/news/world/asia/rss.xml"},
            {"name": "SCMP", "url": "https://www.scmp.com/rss/91/feed/"},
            {"name": "CNA", "url": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml"},
            {"name": "Nikkei Asia", "url": "https://news.google.com/rss/search?q=site:asia.nikkei.com&hl=en-US&gl=US&ceid=US:en"},
        ],
        "africa": [
            {"name": "BBC Africa", "url": "https://feeds.bbci.co.uk/news/world/africa/rss.xml"},
            {"name": "News24", "url": "https://feeds.news24.com/articles/news24/TopStories/rss"},
            {"name": "Premium Times", "url": "https://www.premiumtimesng.com/feed"},
            {"name": "InSight Crime", "url": "https://insightcrime.org/feed/"},
        ],
        "latam": [
            {"name": "BBC Latin America", "url": "https://feeds.bbci.co.uk/news/world/latin_america/rss.xml"},
            {"name": "Reuters LatAm", "url": "https://news.google.com/rss/search?q=site:reuters.com+latam&hl=en-US&gl=US&ceid=US:en"},
            {"name": "Infobae Americas", "url": "https://www.infobae.com/arc/outboundfeeds/rss/"},
        ],
        "crisis": [
            {"name": "CrisisWatch", "url": "https://www.crisisgroup.org/rss"},
            {"name": "UNHCR", "url": "https://news.google.com/rss/search?q=site:unhcr.org+refugees&hl=en-US&gl=US&ceid=US:en"},
            {"name": "IAEA", "url": "https://www.iaea.org/feeds/topnews"},
        ],
        "intel": [
            {"name": "Defense One", "url": "https://www.defenseone.com/rss/all/"},
            {"name": "The War Zone", "url": "https://www.twz.com/feed"},
            {"name": "Foreign Policy", "url": "https://foreignpolicy.com/feed/"},
            {"name": "Foreign Affairs", "url": "https://www.foreignaffairs.com/rss.xml"},
            {"name": "RUSI", "url": "https://news.google.com/rss/search?q=site:rusi.org&hl=en-US&gl=US&ceid=US:en"},
            {"name": "Bellingcat", "url": "https://news.google.com/rss/search?q=site:bellingcat.com&hl=en-US&gl=US&ceid=US:en"},
            {"name": "Krebs Security", "url": "https://krebsonsecurity.com/feed/"},
        ],
    },
    "finance": {
        "markets": [
            {"name": "CNBC", "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html"},
            {"name": "MarketWatch", "url": "https://news.google.com/rss/search?q=site:marketwatch.com+markets&hl=en-US&gl=US&ceid=US:en"},
            {"name": "Yahoo Finance", "url": "https://finance.yahoo.com/rss/topstories"},
            {"name": "Reuters Markets", "url": "https://news.google.com/rss/search?q=site:reuters.com+markets+stocks&hl=en-US&gl=US&ceid=US:en"},
            {"name": "Bloomberg Markets", "url": "https://news.google.com/rss/search?q=site:bloomberg.com+markets&hl=en-US&gl=US&ceid=US:en"},
        ],
        "forex": [
            {"name": "Central Bank Rates", "url": "https://news.google.com/rss/search?q=(central+bank+OR+interest+rate+OR+rate+decision+OR+monetary+policy)&hl=en-US&gl=US&ceid=US:en"},
            {"name": "Dollar Watch", "url": "https://news.google.com/rss/search?q=(dollar+index+OR+DXY+OR+US+dollar)&hl=en-US&gl=US&ceid=US:en"},
        ],
        "bonds": [
            {"name": "Bond Market", "url": "https://news.google.com/rss/search?q=(bond+market+OR+treasury+yields+OR+fixed+income)&hl=en-US&gl=US&ceid=US:en"},
            {"name": "Treasury Watch", "url": "https://news.google.com/rss/search?q=(US+Treasury+OR+10-year+yield+OR+2-year+yield)&hl=en-US&gl=US&ceid=US:en"},
        ],
        "commodities": [
            {"name": "Oil & Gas", "url": "https://news.google.com/rss/search?q=(oil+price+OR+OPEC+OR+crude+oil+OR+WTI+OR+Brent)&hl=en-US&gl=US&ceid=US:en"},
            {"name": "Gold & Metals", "url": "https://news.google.com/rss/search?q=(gold+price+OR+silver+price+OR+copper+OR+precious+metals)&hl=en-US&gl=US&ceid=US:en"},
            {"name": "Commodity Trading", "url": "https://news.google.com/rss/search?q=(commodity+trading+OR+futures+market+OR+CME+OR+NYMEX)&hl=en-US&gl=US&ceid=US:en"},
        ],
        "crypto": [
            {"name": "CoinDesk", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/"},
            {"name": "Cointelegraph", "url": "https://cointelegraph.com/rss"},
            {"name": "The Block", "url": "https://news.google.com/rss/search?q=site:theblock.co&hl=en-US&gl=US&ceid=US:en"},
            {"name": "Crypto News", "url": "https://news.google.com/rss/search?q=(bitcoin+OR+ethereum+OR+crypto+OR+digital+assets)&hl=en-US&gl=US&ceid=US:en"},
            {"name": "Bloomberg Crypto", "url": "https://news.google.com/rss/search?q=bloomberg+crypto&hl=en-US&gl=US&ceid=US:en"},
        ],
        "centralbanks": [
            {"name": "Federal Reserve", "url": "https://www.federalreserve.gov/feeds/press_all.xml"},
            {"name": "ECB Watch", "url": "https://news.google.com/rss/search?q=(European+Central+Bank+OR+ECB+OR+Lagarde)+monetary&hl=en-US&gl=US&ceid=US:en"},
            {"name": "BoJ Watch", "url": "https://news.google.com/rss/search?q=(Bank+of+Japan+OR+BoJ)+monetary&hl=en-US&gl=US&ceid=US:en"},
            {"name": "BoE Watch", "url": "https://news.google.com/rss/search?q=(Bank+of+England+OR+BoE)+monetary&hl=en-US&gl=US&ceid=US:en"},
        ],
        "economic": [
            {"name": "Economic Data", "url": "https://news.google.com/rss/search?q=(CPI+OR+inflation+OR+GDP+OR+jobs+report+OR+PMI)&hl=en-US&gl=US&ceid=US:en"},
            {"name": "Trade & Tariffs", "url": "https://news.google.com/rss/search?q=(tariff+OR+trade+war+OR+trade+deficit+OR+sanctions)&hl=en-US&gl=US&ceid=US:en"},
            {"name": "SEC", "url": "https://www.sec.gov/news/pressreleases.rss"},
        ],
        "fintech": [
            {"name": "Fintech News", "url": "https://news.google.com/rss/search?q=(fintech+OR+neobank+OR+digital+banking)&hl=en-US&gl=US&ceid=US:en"},
            {"name": "Blockchain Finance", "url": "https://news.google.com/rss/search?q=(blockchain+finance+OR+tokenization+OR+CBDC)&hl=en-US&gl=US&ceid=US:en"},
        ],
    },
    "climate": {
        "climate": [
            {"name": "Climate News", "url": "https://news.google.com/rss/search?q=climate+change+extreme+weather+when:2d&hl=en-US&gl=US&ceid=US:en"},
            {"name": "WMO", "url": "https://public.wmo.int/en/media/rss"},
            {"name": "Climate Home News", "url": "https://www.climatechangenews.com/feed/"},
            {"name": "Carbon Brief", "url": "https://www.carbonbrief.org/feed"},
            {"name": "Yale Climate Connections", "url": "https://news.google.com/rss/search?q=site:climateconnections.org&hl=en-US&gl=US&ceid=US:en"},
        ],
        "disasters": [
            {"name": "USGS Earthquakes", "url": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_month.csv"},
            {"name": "EDRG Disasters", "url": "https://news.google.com/rss/search?q=(earthquake+OR+flood+OR+hurricane+OR+wildfire+OR+typhoon)+when:3d&hl=en-US&gl=US&ceid=US:en"},
            {"name": "FEMA", "url": "https://www.fema.gov/outbreaks/disasters.rss"},
            {"name": "WHO Emergencies", "url": "https://www.who.int/feeds/entity/csr/don/en/rss.xml"},
            {"name": "ReliefWeb", "url": "https://relief.intoday.in/rss/"},
        ],
        "water": [
            {"name": "Water Crisis", "url": "https://news.google.com/rss/search?q=(water+crisis+OR+drought+OR+flooding+OR+groundwater)&hl=en-US&gl=US&ceid=US:en"},
            {"name": "River Levels", "url": "https://news.google.com/rss/search?q=(river+levels+OR+flood+warning+OR+dam+discharge)&hl=en-US&gl=US&ceid=US:en"},
        ],
        "wildfire": [
            {"name": "FIRMS Fire", "url": "https://news.google.com/rss/search?q=(wildfire+OR+bushfire+OR+forest+fire+OR+controlled+burn)&hl=en-US&gl=US&ceid=US:en"},
            {"name": "Fire Aviation", "url": "https://news.google.com/rss/search?q=(fire+aviation+OR+aerial+firefighting+OR+fire+crew)&hl=en-US&gl=US&ceid=US:en"},
        ],
    },
}

# Expert/analysis sources for synthesizer
ANALYSIS_SOURCES = {
    "thinktanks": [
        {"name": "Foreign Policy", "url": "https://foreignpolicy.com/feed/"},
        {"name": "Atlantic Council", "url": "https://www.atlanticcouncil.org/feed/"},
        {"name": "Brookings", "url": "https://news.google.com/rss/search?q=site:brookings.edu&hl=en-US&gl=US&ceid=US:en"},
        {"name": "CSIS", "url": "https://news.google.com/rss/search?q=site:csis.org&hl=en-US&gl=US&ceid=US:en"},
        {"name": "RAND", "url": "https://www.rand.org/pubs/articles.xml"},
        {"name": "Carnegie", "url": "https://news.google.com/rss/search?q=site:carnegieendowment.org&hl=en-US&gl=US&ceid=US:en"},
        {"name": "War on the Rocks", "url": "https://warontherocks.com/feed"},
        {"name": "Responsible Statecraft", "url": "https://responsiblestatecraft.org/feed/"},
        {"name": "Lowy Institute", "url": "https://news.google.com/rss/search?q=site:lowyinstitute.org&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Chatham House", "url": "https://news.google.com/rss/search?q=site:chathamhouse.org&hl=en-US&gl=US&ceid=US:en"},
    ],
    "gov": [
        {"name": "White House", "url": "https://news.google.com/rss/search?q=site:whitehouse.gov&hl=en-US&gl=US&ceid=US:en"},
        {"name": "State Dept", "url": "https://news.google.com/rss/search?q=site:state.gov&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Pentagon", "url": "https://news.google.com/rss/search?q=site:defense.gov&hl=en-US&gl=US&ceid=US:en"},
        {"name": "Treasury", "url": "https://news.google.com/rss/search?q=site:treasury.gov&hl=en-US&gl=US&ceid=US:en"},
        {"name": "CISA", "url": "https://www.cisa.gov/cybersecurity-advisories/all.xml"},
        {"name": "UN News", "url": "https://news.un.org/feed/subscribe/en/news/all/rss.xml"},
    ],
}

AGENT_TAGS = {
    "geopolitics": "🌍",
    "finance": "💹",
    "climate": "🌡️",
    "synthesizer": "🧠",
}

def build_agent_prompt(domain: str, feeds: dict, run_ts: str, scratch_dir: Path) -> str:
    """Build the prompt for a sub-agent."""
    feed_lines = []
    for cat, items in feeds.items():
        feed_lines.append(f"\n### {cat.upper()}")
        for f in items:
            feed_lines.append(f"- [{f['name']}]({f['url']})")
    
    prompt = f"""You are Agent {AGENT_TAGS[domain]} ({domain.upper()}) in the yoyoclaw Intelligence Swarm.

## YOUR MISSION
You are a specialized intelligence analyst covering **{domain}**. Your task:
1. Fetch and parse the RSS feeds listed below (use web_fetch or exec curl/wget)
2. Extract the most significant items from the last 6-12 hours
3. Identify patterns, expert opinions, and blind spots
4. Output a structured JSON report

## RSS FEEDS TO MONITOR
{"".join(feed_lines)}

## OUTPUT SCHEMA
Return a JSON object with this exact structure:
```json
{{
  "agent": "{domain}",
  "timestamp": "{run_ts}",
  "run_ts_utc": "{datetime.utcnow().isoformat()}Z",
  "insights": [
    {{
      "headline": "string",
      "summary": "string (2-3 sentences)",
      "category": "string",
      "alert_level": "LOW|MEDIUM|HIGH|CRITICAL",
      "source_names": ["string"],
      "source_urls": ["string (verified URLs only)"],
      "published": "string (date if available)"
    }}
  ],
  "expert_opinions": {{
    "positive": ["string (bullish/constructive views from experts)"],
    "negative": ["string (bearish/concerning views from experts)"],
    "sources": ["string (expert names/organizations)"]
  }},
  "sources": [
    {{
      "name": "string",
      "url": "string (exact URL, must be real)",
      "category": "string",
      "item_count": "number (items found)"
    }}
  ],
  "patterns": [
    "string (observed trend or cross-source pattern)"
  ],
  "blind_spots": [
    "string (topics being ignored by mainstream media)"
  ]
}}
```

## RULES
- Use web_fetch or exec curl to get feed content
- Verify URLs are REAL and working before including them
- NEVER fabricate sources or headlines
- If a feed returns no results, omit it from sources array
- Focus on items from last 6-12 hours
- Limit insights to 8-12 most significant items
- alert_level criteria:
  - CRITICAL: War, invasion, major disaster, market crash, coup, nuclear event
  - HIGH: Sanctions, major policy shifts, significant market moves, large protests
  - MEDIUM: Economic data surprises, diplomatic tensions, notable events
  - LOW: Routine developments
- Save your JSON to: {scratch_dir}/{domain}_{run_ts}.json

## EXECUTION
Process all feeds concurrently where possible. Return the complete JSON result.
"""
    return prompt

def build_synthesizer_prompt(run_ts: str, results_dir: Path, scratch_dir: Path, analysis_feeds: dict) -> str:
    """Build the synthesizer agent prompt."""
    prompt = f"""You are Agent 🧠 (SYNTHESIZER) in the yoyoclaw Intelligence Swarm.

## YOUR MISSION
You are the Chief Analyst who:
1. Reads all 3 domain reports (geopolitics, finance, climate) from the results directory
2. Performs cross-domain correlation and gap analysis
3. Produces the Master Intelligence Report

## RESULTS TO SYNTHESIZE
Read these files:
- {results_dir}/geopolitics_{run_ts}.json
- {results_dir}/finance_{run_ts}.json
- {results_dir}/climate_{run_ts}.json

## ANALYSIS SOURCES (also fetch these)
- Think tanks and policy shops: for unconventional angles
- Government/military sources: for official statements and posture changes

## OUTPUT SCHEMA — Master Intelligence Report
```json
{{
  "report_type": "MASTER_INTELLIGENCE_REPORT",
  "timestamp": "{RUN_TS}",
  "sgt_time": "{SGT_TS}",
  "utc_time": "{UTC_TS}",
  "executive_summary": "string (3-5 sentences, high-level strategic overview)",
  "key_themes": [
    {{
      "theme": "string (theme name)",
      "description": "string (2-3 sentences)",
      "supporting_evidence": ["string"],
      "confidence": "HIGH|MEDIUM|LOW"
    }}
  ],
  "alpha_opportunities": [
    {{
      "angle": "string (unique investment/signal not covered elsewhere)",
      "rationale": "string",
      "timeframe": "SHORT|MEDIUM|LONG",
      "risk": "HIGH|MEDIUM|LOW"
    }}
  ],
  "cross_domain_patterns": [
    "string (patterns spanning geopolitics, finance, climate)"
  ],
  "blind_spots": [
    "string (information gaps or underreported topics)"
  ],
  "reference_index": [
    {{
      "name": "string",
      "url": "string",
      "used_by": "string (which agents cited this)"
    }}
  ],
  "alerts_summary": {{
    "critical": ["string (headlines)"],
    "high": ["string (headlines)"],
    "medium": ["string (headlines)"],
    "low": ["string (headlines)"]
  }}
}}
```

## RED-TEAMING CHECKS
Before finalizing:
1. Remove duplicate claims across agents
2. Resolve conflicts (if two agents disagree, note both and assign confidence)
3. Verify all URLs are real and accessible
4. Flag any unsubstantiated claims

## SAVE OUTPUT
Save the final Master Intelligence Report JSON to:
{results_dir}/synthesizer_{run_ts}.json
"""
    return prompt

def spawn_subagents(run_ts: str):
    """Spawn all 4 sub-agents in parallel."""
    import uuid
    
    agents = [
        ("geopolitics", FEED_MAP["geopolitics"]),
        ("finance", FEED_MAP["finance"]),
        ("climate", FEED_MAP["climate"]),
    ]
    
    session_ids = {}
    
    for domain, feeds in agents:
        prompt = build_agent_prompt(domain, feeds, run_ts, SCRATCH_DIR)
        result_file = SCRATCH_DIR / f"{domain}_{run_ts}.json"
        
        # Write prompt to file for sub-agent to pick up
        prompt_file = SCRATCH_DIR / f"prompt_{domain}_{run_ts}.txt"
        prompt_file.write_text(prompt)
        
        task = f"""Read the file at {prompt_file} and follow its instructions exactly.

Execute your analysis, save results to {result_file}, then confirm completion.
"""
        # Spawn sub-agent
        try:
            result = sessions_spawn(
                task=task,
                label=f"intel-{domain}-{run_ts}",
                runtime="subagent",
                run_timeout_seconds=300,
                mode="run",
            )
            # sessions_spawn returns a dict with session info
            if isinstance(result, dict):
                session_ids[domain] = result.get("sessionId", result.get("session_key", ""))
            else:
                session_ids[domain] = str(result)
            print(f"  [{AGENT_TAGS[domain]}] Spawned {domain} agent")
        except Exception as e:
            print(f"  [{AGENT_TAGS[domain]}] ERROR spawning {domain}: {e}")
            session_ids[domain] = None
    
    return session_ids

def collect_results(run_ts: str, timeout_seconds: int = 300) -> dict:
    """Poll for sub-agent results."""
    import time
    
    agents = ["geopolitics", "finance", "climate"]
    results = {}
    start = time.time()
    
    while time.time() - start < timeout_seconds:
        done = []
        for domain in agents:
            result_file = SCRATCH_DIR / f"{domain}_{run_ts}.json"
            if result_file.exists():
                try:
                    data = json.loads(result_file.read_text())
                    results[domain] = data
                    done.append(domain)
                    print(f"  [{AGENT_TAGS[domain]}] ✓ Results received")
                except Exception as e:
                    print(f"  [{AGENT_TAGS[domain]}] Error reading {result_file}: {e}")
        
        if len(done) == len(agents):
            break
        
        remaining = [d for d in agents if d not in done]
        print(f"  Waiting for: {', '.join(remaining)}...")
        time.sleep(15)
    
    missing = [d for d in agents if d not in results]
    if missing:
        print(f"  TIMEOUT: Missing results from: {', '.join(missing)}")
    
    return results

def synthesize_and_save(run_ts: str, agent_results: dict) -> str:
    """Run synthesizer to create the final report."""
    # Save agent results to results dir
    for domain, data in agent_results.items():
        out_file = RESULTS_DIR / f"{domain}_{run_ts}.json"
        out_file.write_text(json.dumps(data, indent=2))
        print(f"  [{AGENT_TAGS[domain]}] Saved to {out_file.name}")
    
    # Now run synthesizer
    print(f"\n  [{AGENT_TAGS['synthesizer']}] Running synthesizer...")
    
    synth_prompt = build_synthesizer_prompt(run_ts, RESULTS_DIR, SCRATCH_DIR, ANALYSIS_SOURCES)
    synth_prompt_file = SCRATCH_DIR / f"prompt_synthesizer_{run_ts}.txt"
    synth_prompt_file.write_text(synth_prompt)
    
    result_file = RESULTS_DIR / f"master_{run_ts}.json"
    
    task = f"""Read the file at {synth_prompt_file} and follow its instructions exactly.

Read the agent results, produce the Master Intelligence Report, and save to {result_file}.
"""
    
    try:
        # Run synthesizer synchronously in this session
        synth_result = sessions_spawn(
            task=task,
            label=f"intel-synth-{run_ts}",
            runtime="subagent",
            run_timeout_seconds=300,
            mode="run",
        )
        
        if result_file.exists():
            data = json.loads(result_file.read_text())
            print(f"  [{AGENT_TAGS['synthesizer']}] ✓ Master report generated")
            return str(result_file)
        else:
            print(f"  [{AGENT_TAGS['synthesizer']}] ✗ Report file not created")
            return None
    except Exception as e:
        print(f"  [{AGENT_TAGS['synthesizer']}] ERROR: {e}")
        return None

def generate_markdown_report(json_file: Path) -> Path:
    """Convert JSON report to human-readable Markdown."""
    data = json.loads(json_file.read_text())
    run_ts = data.get("timestamp", json_file.stem.replace("master_", ""))
    
    md = f"""---
title: Intelligence Report — {SGT_TS}
date: {RUN_TS}
type: intelligence-report
tags: [intel, daily-brief, world-monitor]
---

# 🧠 Master Intelligence Report
**Generated:** {SGT_TS} | {UTC_TS}  
**Report ID:** `intel_{run_ts}`

---

## Executive Summary

{data.get("executive_summary", "No summary available.")}

---

## Key Themes & Patterns

"""
    for i, theme in enumerate(data.get("key_themes", []), 1):
        md += f"""### {i}. {theme.get("theme", "Unknown Theme")} [{theme.get("confidence", "N/A")}]

{theme.get("description", "")}

**Supporting Evidence:**
"""
        for ev in theme.get("supporting_evidence", []):
            md += f"- {ev}\n"
        md += "\n"

    md += """---

## Alpha Opportunities

"""
    for op in data.get("alpha_opportunities", []):
        md += f"""### ▸ {op.get("angle", "Unknown")}

**Rationale:** {op.get("rationale", "")}  
**Timeframe:** {op.get("timeframe", "N/A")} | **Risk:** {op.get("risk", "N/A")}

"""

    md += """---

## Cross-Domain Patterns

"""
    for p in data.get("cross_domain_patterns", []):
        md += f"- {p}\n"
    md += "\n"

    md += """---

## Blind Spots

"""
    for b in data.get("blind_spots", []):
        md += f"- {b}\n"
    md += "\n"

    md += """---

## Alerts Summary

"""
    alerts = data.get("alerts_summary", {})
    for level in ["critical", "high", "medium", "low"]:
        items = alerts.get(level, [])
        if items:
            emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(level, "⚪")
            md += f"### {emoji} {level.upper()} ({len(items)})\n"
            for item in items:
                md += f"- {item}\n"
            md += "\n"

    md += """---

## Reference Index

| Source | URL | Cited By |
|--------|-----|----------|
"""
    for ref in data.get("reference_index", []):
        name = ref.get("name", "Unknown")
        url = ref.get("url", "#")
        cited_by = ref.get("used_by", "Unknown")
        md += f"| {name} | [Link]({url}) | {cited_by} |\n"

    md += f"""

---

*Report generated by yoyoclaw Intelligence Swarm · {UTC_TS}*
*Source: WorldMonitor Feed Network · koala73/worldmonitor*
"""

    md_file = FINAL_REPORTS_DIR / f"intel_report_{run_ts}.md"
    md_file.write_text(md)
    print(f"  📄 Markdown report saved: {md_file.name}")
    return md_file

def save_to_obsidian(md_file: Path) -> bool:
    """Save report to Obsidian vault."""
    # Check if obsidian-cli is available
    obsidian_vault_check = subprocess.run(
        ["obsidian-cli", "print-default", "--path-only"],
        capture_output=True, text=True
    )
    
    if obsidian_vault_check.returncode != 0:
        print("  ⚠️ obsidian-cli not available, skipping Obsidian save")
        return False
    
    vault_path = obsidian_vault_check.stdout.strip()
    if not vault_path:
        print("  ⚠️ No default Obsidian vault set")
        return False
    
    # Target: Worldnews/Daily Intel/
    target_name = f"Worldnews/Daily Intel/Intel Report {SGT_TS.replace(':', '-')}"
    target_name = target_name.replace(" ", "-")
    
    try:
        # Copy file to vault
        import shutil
        obsidian_dir = Path(vault_path)
        target_dir = obsidian_dir / "Worldnews" / "Daily Intel"
        target_dir.mkdir(parents=True, exist_ok=True)
        
        target_file = target_dir / md_file.name
        shutil.copy2(md_file, target_file)
        print(f"  💎 Saved to Obsidian: {target_file.relative_to(obsidian_dir)}")
        return True
    except Exception as e:
        print(f"  ⚠️ Obsidian save failed: {e}")
        return False

def github_push(md_file: Path) -> bool:
    """Git add, commit, and push the report."""
    try:
        # Check if git repo exists
        git_dir = WORKSPACE / ".git"
        if not git_dir.exists():
            print("  ⚠️ Not a git repository, skipping GitHub push")
            return False
        
        # Git add
        subprocess.run(["git", "add", str(md_file), str(md_file.with_suffix('.json'))], 
                      cwd=WORKSPACE, capture_output=True)
        
        # Check if anything to commit
        status = subprocess.run(["git", "status", "--porcelain"], cwd=WORKSPACE, capture_output=True, text=True)
        if not status.stdout.strip():
            print("  ✓ No changes to commit")
            return True
        
        # Commit
        commit_msg = f"Intel Report {RUN_TS} — {SGT_TS}"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=WORKSPACE, capture_output=True)
        
        # Push
        push = subprocess.run(["git", "push"], cwd=WORKSPACE, capture_output=True, text=True, timeout=60)
        if push.returncode == 0:
            print(f"  ✅ GitHub push successful")
            return True
        else:
            print(f"  ⚠️ GitHub push failed: {push.stderr}")
            return False
    except Exception as e:
        print(f"  ⚠️ GitHub push error: {e}")
        return False

def send_telegram_alert(md_file: Path, report_json: Path) -> bool:
    """Send completion summary via Telegram."""
    try:
        data = json.loads(report_json.read_text())
        alerts = data.get("alerts_summary", {})
        
        critical_count = len(alerts.get("critical", []))
        high_count = len(alerts.get("high", []))
        
        summary = data.get("executive_summary", "Report generated successfully.")
        # Truncate to fit Telegram
        if len(summary) > 300:
            summary = summary[:297] + "..."
        
        alert_banner = ""
        if critical_count > 0:
            alert_banner = f"🔴 CRITICAL ALERTS: {critical_count}"
        elif high_count > 0:
            alert_banner = f"🟠 HIGH ALERTS: {high_count}"
        
        msg = f"""🧠 Intelligence Report Ready

{alert_banner}
**Time:** {SGT_TS}

📋 *Summary:*
{summary}

📁 *Report:* Intel Report {RUN_TS}
"""
        
        # Send via sessions_send to main session
        # Actually, we should use the Telegram skill or send via the bot
        # For now, just log - Telegram sending requires the notification system
        print(f"  📱 Telegram alert prepared (not sent — implement via notification system)")
        print(f"     Message preview: {msg[:100]}...")
        return True
    except Exception as e:
        print(f"  ⚠️ Telegram alert error: {e}")
        return False

def main():
    print(f"\n{'='*60}")
    print(f"🧠 YOYOCLAW INTELLIGENCE SWARM — {SGT_TS}")
    print(f"{'='*60}\n")
    
    print(f"[1/5] 🕷️ Spawning sub-agents...")
    session_ids = spawn_subagents(RUN_TS)
    
    print(f"\n[2/5] ⏳ Collecting results (timeout: 5 min)...")
    agent_results = collect_results(RUN_TS, timeout_seconds=300)
    
    if len(agent_results) < 3:
        print(f"\n  ⚠️ Only {len(agent_results)}/3 agents completed. Proceeding with available results.")
    
    print(f"\n[3/5] 🧠 Synthesizing & red-teaming...")
    report_json = synthesize_and_save(RUN_TS, agent_results)
    
    if not report_json:
        print("  ✗ Synthesis failed")
        sys.exit(1)
    
    print(f"\n[4/5] 📄 Generating markdown report...")
    md_file = generate_markdown_report(Path(report_json))
    
    print(f"\n[5/5] 💾 Saving to Obsidian & GitHub...")
    obsidian_ok = save_to_obsidian(md_file)
    github_ok = github_push(md_file)
    
    send_telegram_alert(md_file, Path(report_json))
    
    print(f"\n{'='*60}")
    print(f"✅ INTELLIGENCE SWARM COMPLETE — {SGT_TS}")
    print(f"{'='*60}")
    print(f"   Master: {md_file.name}")
    print(f"   Obsidian: {'✓' if obsidian_ok else '✗'}")
    print(f"   GitHub:   {'✓' if github_ok else '✗'}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
