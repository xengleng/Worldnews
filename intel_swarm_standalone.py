#!/usr/bin/env python3
"""
Intel Swarm Standalone Orchestrator v2
Self-contained: runs all 3 domain analyses + synthesis in one process.
No sub-agents needed — uses direct API calls.
"""
import sys
import json
import os
import subprocess
import re
from datetime import datetime

# ─── CONFIG ──────────────────────────────────────────────────────────────────
WORKSPACE = "/home/yeoel/.openclaw/workspace"
RESULTS_DIR = f"{WORKSPACE}/intel_swarm/results"
REPORTS_DIR = f"{WORKSPACE}/intel_swarm/reports"
SCRATCH_DIR = f"{WORKSPACE}/intel_swarm/scratch"
OBSIDIAN_DIR = "/home/yeoel/Documents/openclaw/Worldnews/Daily Intel"

RUN_TS = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y%m%d_%H%M")
SGT_TS = datetime.now().strftime("%Y-%m-%d %I:%M %p SGT")
UTC_TS = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

API_BASE = "https://api.minimaxi.com/v1"
API_KEY = os.environ.get("MINIMAXI_API_KEY", "")

# ─── LLM CALL ─────────────────────────────────────────────────────────────────
def llm(prompt: str, model: str = "MiniMax-M2.7", max_tokens: int = 2000) -> str:
    import urllib.request, urllib.error
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.2
    }).encode()
    req = urllib.request.Request(
        f"{API_BASE}/chat/completions",
        data=payload,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read())["choices"][0]["message"]["content"]

# ─── READ SOURCE DATA ─────────────────────────────────────────────────────────
def get_latest_bloomberg():
    import glob
    files = sorted(glob.glob(f"{WORKSPACE}/bloomberg_data_*.json"))
    if not files:
        return "No Bloomberg data available."
    with open(files[-1]) as f:
        data = json.load(f)
    articles = data.get("categorized_articles", [])
    lines = []
    for a in articles:
        lvl = a.get("alert_level", 1)
        tag = {1:"LOW",2:"MED",3:"HIGH",4:"CRIT"}.get(lvl, str(lvl))
        lines.append(f"[{tag}] {a.get('title','')} | {a.get('source','')} | {a.get('url','')}")
    return "\n".join(lines[:30])

def read_json(path):
    try:
        with open(path) as f:
            return f.read()
    except:
        return f"File not found: {path}"

# ─── DOMAIN ANALYSIS ─────────────────────────────────────────────────────────
DOMAIN_PROMPTS = {
    "geopolitics": """You are a Geopolitical Intelligence Analyst. Based on today's Bloomberg news data below, identify the 10 most significant geopolitical developments.

Return ONLY a JSON object with this structure (no markdown, no extra text):
{
  "report_type": "GEOPOLITICAL_INTEL",
  "domain": "geopolitics",
  "report_ts": "{TS}",
  "executive_summary": "2-3 sentence summary of the most critical geopolitical developments today",
  "key_insights": [
    {{
      "insight": "specific geopolitical development",
      "location": "country/region",
      "actors": ["actor1", "actor2"],
      "alert_level": "HIGH|MEDIUM|LOW",
      "source": "source name",
      "url": "url or 'N/A'"
    }}
  ],
  "blind_spot": "Geopolitical development that is underreported but significant",
  "url": "source url or 'N/A'"
}

NEWS DATA:
{{news_data}}

Respond with ONLY the JSON object.""",

    "finance": """You are a Financial Intelligence Analyst. Based on today's Bloomberg news data below, identify the 10 most significant financial/market developments.

Return ONLY a JSON object with this structure (no markdown, no extra text):
{{
  "report_type": "FINANCIAL_INTEL",
  "domain": "finance",
  "report_ts": "{TS}",
  "executive_summary": "2-3 sentence summary of the most critical financial developments today",
  "key_insights": [
    {{
      "insight": "specific financial/market development",
      "asset_class": "equities/bonds/commodities/forex/crypto",
      "alert_level": "HIGH|MEDIUM|LOW",
      "source": "source name",
      "url": "url or 'N/A'"
    }}
  ],
  "blind_spot": "Financial development that is underreported but significant",
  "url": "source url or 'N/A'"
}}

NEWS DATA:
{{news_data}}

Respond with ONLY the JSON object.""",

    "climate": """You are a Climate & Disaster Intelligence Analyst. Based on today's Bloomberg news data below, identify the most significant climate-related events and natural disasters.

Return ONLY a JSON object with this structure (no markdown, no extra text):
{{
  "report_type": "CLIMATE_INTEL",
  "domain": "climate",
  "report_ts": "{TS}",
  "executive_summary": "2-3 sentence summary of the most critical climate/disaster events today",
  "key_insights": [
    {{
      "insight": "specific climate or disaster event",
      "location": "country/region",
      "alert_level": "HIGH|MEDIUM|LOW",
      "source": "source name",
      "url": "url or 'N/A'"
    }}
  ],
  "blind_spot": "Climate/disaster development that is underreported but significant",
  "url": "source url or 'N/A'"
}}

NEWS DATA:
{{news_data}}

Respond with ONLY the JSON object."""
}

def run_domain(domain: str, news_data: str) -> dict:
    prompt = DOMAIN_PROMPTS[domain].format(TS=RUN_TS, news_data=news_data)
    raw = llm(prompt, max_tokens=2500)
    # Extract JSON
    match = re.search(r'\{[\s\S]+\}', raw)
    if match:
        try:
            return json.loads(match.group())
        except:
            return {"error": f"Failed to parse {domain} JSON", "raw": raw[:500]}
    return {"error": f"No JSON found in {domain} response", "raw": raw[:500]}

# ─── SYNTHESIS ────────────────────────────────────────────────────────────────
SYNTHESIZER_PROMPT = """You are the Chief Intelligence Synthesizer. Read the 3 domain intelligence reports below and produce a MASTER INTELLIGENCE REPORT.

Domain Reports:
{domain_reports}

Return ONLY a JSON object (no markdown, no text outside):
{{
  "report_type": "MASTER_INTELLIGENCE_REPORT",
  "report_ts": "{TS}",
  "crisis_line": "One-line headline: most critical development right now (50 chars max, use ✅/❌/⚠️/🚨 markers)",
  "executive_summary": "3-4 sentence executive summary of the global situation",
  "key_themes": [
    {{
      "theme": "theme name",
      "description": "2-3 sentence description",
      "confidence": "HIGH|MEDIUM|LOW",
      "alert_level": "CRITICAL|HIGH|MEDIUM|LOW",
      "evidence": ["source1", "source2"]
    }}
  ],
  "alpha_opportunities": [
    {{
      "angle": "specific investment or action angle",
      "rationale": "why this matters now",
      "timeframe": "short-term/medium-term/long-term",
      "risk": "HIGH|MEDIUM|LOW"
    }}
  ],
  "alerts_summary": {{
    "CRITICAL": ["alert1", "alert2"],
    "HIGH": ["alert1", "alert2"],
    "MEDIUM": ["alert1"],
    "LOW": []
  }},
  "telegram_summary": "2-3 sentence crisis summary for Telegram. Include the crisis_line and top 2-3 most important developments. Be direct and punchy.",
  "reference_index": [
    {{"source": "name", "url": "url"}}
  ]
}}

Respond with ONLY the JSON object."""

def synthesize(geo: dict, fin: dict, climate: dict) -> dict:
    combined = f"GEOPOLITICS:\n{json.dumps(geo, indent=2)}\n\nFINANCE:\n{json.dumps(fin, indent=2)}\n\nCLIMATE:\n{json.dumps(climate, indent=2)}"
    prompt = SYNTHESIZER_PROMPT.format(TS=RUN_TS, domain_reports=combined)
    raw = llm(prompt, max_tokens=3000)
    match = re.search(r'\{[\s\S]+\}', raw)
    if match:
        try:
            return json.loads(match.group())
        except:
            return {"error": "Failed to parse synthesis JSON", "raw": raw[:500]}
    return {"error": "No JSON found in synthesis", "raw": raw[:500]}

# ─── MARKDOWN GENERATOR ──────────────────────────────────────────────────────
def generate_markdown(master: dict, geo: dict, fin: dict, climate: dict) -> str:
    alerts = master.get("alerts_summary", {})
    crisis = master.get("crisis_line", "⚠️ Situation evolving")
    
    # Build reference index
    refs = []
    for domain_data in [geo, fin, climate]:
        for insight in domain_data.get("key_insights", []):
            if insight.get("url") and insight["url"] != "N/A":
                refs.append({"source": insight.get("source",""), "url": insight["url"]})
    for ref in master.get("reference_index", []):
        refs.append(ref)
    
    themes_md = ""
    for t in master.get("key_themes", []):
        emoji = {"CRITICAL": "🚨", "HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(t.get("alert_level", "MEDIUM"), "🟡")
        themes_md += f"\n### {emoji} {t.get('theme','')}\n{t.get('description','')}\n"
    
    alpha_md = ""
    for a in master.get("alpha_opportunities", []):
        risk_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(a.get("risk", "MEDIUM"), "🟡")
        alpha_md += f"\n### {risk_emoji} {a.get('angle','')}\n**Rationale:** {a.get('rationale','')}\n**Timeframe:** {a.get('timeframe','')} | **Risk:** {a.get('risk','')}\n"
    
    crit_md = "\n".join([f"- 🚨 {x}" for x in alerts.get("CRITICAL", [])])
    high_md = "\n".join([f"- 🔴 {x}" for x in alerts.get("HIGH", [])])
    med_md = "\n".join([f"- 🟡 {x}" for x in alerts.get("MEDIUM", [])])
    low_md = "\n".join([f"- 🟢 {x}" for x in alerts.get("LOW", [])])
    
    refs_md = "\n".join([f"- [{r['source']}]({r['url']})" for r in refs[:10]])
    
    return f"""---
title: Intelligence Report — {SGT_TS}
date: {RUN_TS}
type: intelligence-report
tags: [intel, daily-brief, world-monitor]
---

# 🧠 Master Intelligence Report
**Generated:** {SGT_TS} | {UTC_TS}
**Report ID:** `intel_{RUN_TS}`

---

## Executive Summary
{master.get('executive_summary', '')}

---

## Key Themes
{themes_md}

## Alpha Opportunities
{alpha_md if alpha_md else "_No alpha opportunities identified._"}

## Alerts Summary

### 🚨 CRITICAL
{crit_md if crit_md else "_None._"}

### 🔴 HIGH
{high_md if high_md else "_None._"}

### 🟡 MEDIUM
{med_md if med_md else "_None._"}

### 🟢 LOW
{low_md if low_md else "_None._"}

## Telegram Summary
> {master.get('telegram_summary', '')}

## Reference Index
{refs_md}
"""

# ─── SAVE & DISTRIBUTE ────────────────────────────────────────────────────────
def save_and_push(master_json: str, markdown: str):
    # Save files
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    master_path = f"{RESULTS_DIR}/master_{RUN_TS}.json"
    md_path = f"{REPORTS_DIR}/intel_report_{RUN_TS}.md"
    
    with open(master_path, "w") as f:
        f.write(master_json)
    
    with open(md_path, "w") as f:
        f.write(markdown)
    
    print(f"✅ Saved: {master_path}")
    print(f"✅ Saved: {md_path}")
    
    # Obsidian copy
    os.makedirs(OBSIDIAN_DIR, exist_ok=True)
    obsidian_path = f"{OBSIDIAN_DIR}/Intel-Report-{RUN_TS}.md"
    with open(obsidian_path, "w") as f:
        f.write(markdown)
    print(f"✅ Obsidian: {obsidian_path}")
    
    # GitHub
    try:
        subprocess.run(["git", "add", f"intel_swarm/reports/intel_report_{RUN_TS}.md", f"intel_swarm/results/master_{RUN_TS}.json"], 
                     cwd=WORKSPACE, check=True)
        subprocess.run(["git", "commit", "-m", f"Intel Report {RUN_TS} — {SGT_TS}"], cwd=WORKSPACE, check=True)
        subprocess.run(["git", "push"], cwd=WORKSPACE, check=True)
        print("✅ GitHub pushed")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Git error: {e}")

# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"=== Intel Swarm Standalone v2 | TS: {RUN_TS} | {SGT_TS} ===")
    
    news = get_latest_bloomberg()
    
    print("\n📡 Running Geopolitics analysis...")
    geo = run_domain("geopolitics", news)
    with open(f"{RESULTS_DIR}/geopolitics_{RUN_TS}.json", "w") as f:
        json.dump(geo, f, indent=2)
    print(f"✅ Geopolitics: {len(geo.get('key_insights',[]))} insights")
    
    print("\n📡 Running Finance analysis...")
    fin = run_domain("finance", news)
    with open(f"{RESULTS_DIR}/finance_{RUN_TS}.json", "w") as f:
        json.dump(fin, f, indent=2)
    print(f"✅ Finance: {len(fin.get('key_insights',[]))} insights")
    
    print("\n📡 Running Climate analysis...")
    climate = run_domain("climate", news)
    with open(f"{RESULTS_DIR}/climate_{RUN_TS}.json", "w") as f:
        json.dump(climate, f, indent=2)
    print(f"✅ Climate: {len(climate.get('key_insights',[]))} insights")
    
    print("\n🧠 Synthesizing master report...")
    master = synthesize(geo, fin, climate)
    master_json = json.dumps(master, indent=2)
    
    print("\n📝 Generating markdown...")
    md = generate_markdown(master, geo, fin, climate)
    
    print("\n💾 Saving and pushing...")
    save_and_push(master_json, md)
    
    print(f"\n=== DONE | TS: {RUN_TS} ===")
    print(f"Telegram Summary:\n> {master.get('telegram_summary', '')}")
