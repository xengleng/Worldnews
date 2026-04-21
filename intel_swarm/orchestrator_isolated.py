#!/usr/bin/env python3
"""
Intel Swarm Standalone Orchestrator — Isolated Session Version
Uses DeepSeek API (has working API key) for all LLM calls.
No sub-agents needed — fully self-contained.
"""
import sys
import json
import os
import subprocess
import re
import glob
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

MINIMAX_API_KEY = os.environ.get("MINIMAXI_API_KEY", "")
if not MINIMAX_API_KEY:
    token_file = f"{WORKSPACE}/intel_swarm/.api_key"
    if os.path.exists(token_file):
        with open(token_file) as f:
            MINIMAX_API_KEY = f.read().strip()

MINIMAX_URL = "https://api.minimax.io/v1/chat/completions"
MODEL = "MiniMax-M2.7"

# ─── LLM CALL ─────────────────────────────────────────────────────────────────
def llm(prompt: str, model: str = MODEL, max_tokens: int = 2500) -> str:
    import urllib.request, urllib.error
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.2
    }).encode()
    req = urllib.request.Request(
        MINIMAX_URL,
        data=payload,
        headers={"Authorization": f"Bearer {MINIMAX_API_KEY}", "Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=150) as resp:
            return json.loads(resp.read())["choices"][0]["message"]["content"]
    except Exception as e:
        return f"ERROR: {e}"

# ─── READ SOURCE DATA ─────────────────────────────────────────────────────────
def get_latest_bloomberg():
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

def read_file(path):
    try:
        with open(path) as f:
            return f.read()
    except:
        return f"File not found: {path}"

# ─── DOMAIN ANALYSIS ─────────────────────────────────────────────────────────
DOMAIN_PROMPTS = {
    "geopolitics": """You are a Geopolitical Intelligence Analyst. Based on today's news data below, identify the 10 most significant geopolitical developments worldwide.

Return ONLY a valid JSON object with this exact structure (no markdown, no text before or after):
{{
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
}}

NEWS DATA:
{news_data}

Respond with ONLY the JSON object.""",

    "finance": """You are a Financial Intelligence Analyst. Based on today's news data below, identify the 10 most significant financial and market developments worldwide.

Return ONLY a valid JSON object with this exact structure (no markdown, no text before or after):
{{
  "report_type": "FINANCIAL_INTEL",
  "domain": "finance",
  "report_ts": "{TS}",
  "executive_summary": "2-3 sentence summary of the most critical financial developments today",
  "key_insights": [
    {{
      "insight": "specific financial/market development",
      "asset_class": "equities/bonds/commodities/forex/crypto/energy",
      "alert_level": "HIGH|MEDIUM|LOW",
      "source": "source name",
      "url": "url or 'N/A'"
    }}
  ],
  "blind_spot": "Financial development that is underreported but significant",
  "url": "source url or 'N/A'"
}}

NEWS DATA:
{news_data}

Respond with ONLY the JSON object.""",

    "climate": """You are a Climate and Disaster Intelligence Analyst. Based on today's news data below, identify the most significant climate-related events, natural disasters, and environmental developments.

Return ONLY a valid JSON object with this exact structure (no markdown, no text before or after):
{{
  "report_type": "CLIMATE_INTEL",
  "domain": "climate",
  "report_ts": "{TS}",
  "executive_summary": "2-3 sentence summary of the most critical climate and disaster events today",
  "key_insights": [
    {{
      "insight": "specific climate or disaster event",
      "location": "country/region",
      "alert_level": "HIGH|MEDIUM|LOW",
      "source": "source name",
      "url": "url or 'N/A'"
    }}
  ],
  "blind_spot": "Climate or disaster development that is underreported but significant",
  "url": "source url or 'N/A'"
}}

NEWS DATA:
{news_data}

Respond with ONLY the JSON object."""
}

def parse_json_response(raw: str) -> dict:
    """Extract JSON from LLM response."""
    # Remove thinking tags first
    clean = re.sub(r'<thinking[\s\S]*?</thinking>', '', raw)
    clean = re.sub(r'<think>[\s\S]*?</think>', '', clean)
    
    # Try to find JSON block
    match = re.search(r'\{[\s\S]+\}', clean)
    if match:
        try:
            return json.loads(match.group())
        except:
            pass
    return {"error": "Failed to parse JSON", "raw": clean[:300]}

def run_domain(domain: str, news_data: str) -> dict:
    prompt = DOMAIN_PROMPTS[domain].format(TS=RUN_TS, news_data=news_data)
    raw = llm(prompt, max_tokens=2500)
    result = parse_json_response(raw)
    if "error" not in result:
        return result  # clean result, no _raw added
    result["_raw"] = raw[:200]  # only add _raw on parse failure
    return result

# ─── SYNTHESIS ────────────────────────────────────────────────────────────────
SYNTHESIZER_PROMPT = """You are the Chief Intelligence Synthesizer. Read the 3 domain intelligence reports below and produce a MASTER INTELLIGENCE REPORT.

GEOPOLITICS REPORT:
{geo_json}

FINANCE REPORT:
{fin_json}

CLIMATE REPORT:
{climate_json}

Produce a MASTER INTELLIGENCE REPORT as a JSON object. Return ONLY the JSON object (no markdown, no text before or after the JSON).

JSON structure:
{{
  "report_type": "MASTER_INTELLIGENCE_REPORT",
  "report_ts": "{TS}",
  "crisis_line": "One-line headline: most critical development right now. Use 🚨 for CRITICAL, ⚠️ for HIGH, 🟡 for MEDIUM, 🟢 for LOW. Max 60 chars.",
  "executive_summary": "3-4 sentence executive summary of the global situation",
  "key_themes": [
    {{
      "theme": "theme name",
      "description": "2-3 sentence description of this development",
      "confidence": "HIGH|MEDIUM|LOW",
      "alert_level": "CRITICAL|HIGH|MEDIUM|LOW",
      "evidence": ["source1 name", "source2 name"]
    }}
  ],
  "alpha_opportunities": [
    {{
      "angle": "specific investment or strategic action angle",
      "rationale": "why this matters and what the catalyst is",
      "timeframe": "short-term|medium-term|long-term",
      "risk": "HIGH|MEDIUM|LOW"
    }}
  ],
  "alerts_summary": {{
    "CRITICAL": ["alert1", "alert2"],
    "HIGH": ["alert1", "alert2"],
    "MEDIUM": ["alert1"],
    "LOW": []
  }},
  "telegram_summary": "2-3 sentence crisis summary for Telegram. Be direct and punchy. Include the crisis_line content and top 2-3 most important developments. This goes directly to the user.",
  "reference_index": [
    {{"source": "source name", "url": "url"}}
  ]
}}

Respond with ONLY the JSON object."""

def synthesize(geo: dict, fin: dict, climate: dict) -> dict:
    prompt = SYNTHESIZER_PROMPT.format(
        TS=RUN_TS,
        geo_json=json.dumps(geo, indent=2)[:4000],
        fin_json=json.dumps(fin, indent=2)[:4000],
        climate_json=json.dumps(climate, indent=2)[:4000]
    )
    raw = llm(prompt, max_tokens=3000)
    result = parse_json_response(raw)
    if "error" not in result:
        return result
    # Fallback: return error info
    return {**result, "raw": raw[:300]}

# ─── MARKDOWN GENERATOR ───────────────────────────────────────────────────────
def generate_markdown(master: dict, geo: dict, fin: dict, climate: dict) -> str:
    alerts = master.get("alerts_summary", {})
    
    # Collect all sources
    refs = []
    for domain_data in [geo, fin, climate]:
        if isinstance(domain_data, dict):
            for insight in domain_data.get("key_insights", []):
                if insight.get("url") and insight["url"] != "N/A" and insight["url"] != "ERROR":
                    src = insight.get("source", "source")
                    url = insight.get("url", "")
                    if src and url:
                        refs.append({"source": src, "url": url})
    
    for ref in master.get("reference_index", []):
        if ref.get("url"):
            refs.append(ref)
    
    # Deduplicate refs by URL
    seen = set()
    unique_refs = []
    for r in refs:
        if r["url"] not in seen:
            seen.add(r["url"])
            unique_refs.append(r)
    refs = unique_refs[:15]
    
    themes_md = ""
    for t in master.get("key_themes", []):
        lvl = t.get("alert_level", "MEDIUM")
        emoji = {"CRITICAL": "🚨", "HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(lvl, "🟡")
        conf = t.get("confidence", "MEDIUM")
        evidence = ", ".join(t.get("evidence", [])[:3])
        themes_md += f"\n### {emoji} {t.get('theme', 'Unknown')}\n{t.get('description', '')}\n"
        if evidence:
            themes_md += f"_Evidence: {evidence}_\n"
    
    alpha_md = ""
    for a in master.get("alpha_opportunities", []):
        risk = a.get("risk", "MEDIUM")
        emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(risk, "🟡")
        alpha_md += f"\n### {emoji} {a.get('angle', '')}\n"
        alpha_md += f"**Rationale:** {a.get('rationale', '')}\n"
        alpha_md += f"**Timeframe:** {a.get('timeframe', '')} | **Risk:** {risk}\n"
    
    if not alpha_md:
        alpha_md = "_No alpha opportunities identified._"
    
    def alert_list(key):
        items = alerts.get(key, [])
        if not items:
            return f"_None._"
        emojis = {"CRITICAL": "🚨", "HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
        return "\n".join([f"- {emojis.get(key,'•')} {x}" for x in items])
    
    crit_md = alert_list("CRITICAL")
    high_md = alert_list("HIGH")
    med_md = alert_list("MEDIUM")
    low_md = alert_list("LOW")
    
    refs_md = "\n".join([f"- [{r['source']}]({r['url']})" for r in refs]) or "_No sources._"
    
    crisis = master.get("crisis_line", "⚠️ Situation evolving — monitor closely")
    
    return f"""---
title: Intelligence Report — {SGT_TS}
date: {RUN_TS}
type: intelligence-report
tags: [intel, daily-brief, world-monitor]
---

# 🧠 Master Intelligence Report
**Generated:** {SGT_TS} | {UTC_TS}
**Report ID:** `intel_{RUN_TS}`
**Crisis Line:** {crisis}

---

## Executive Summary
{master.get('executive_summary', 'No summary available.')}

---

## Key Themes
{themes_md}

## Alpha Opportunities
{alpha_md}

## Alerts Summary

### 🚨 CRITICAL
{crit_md}

### 🔴 HIGH
{high_md}

### 🟡 MEDIUM
{med_md}

### 🟢 LOW
{low_md}

## Telegram Summary
> {master.get('telegram_summary', crisis)}

## Reference Index
{refs_md}
"""

# ─── SAVE & DISTRIBUTE ────────────────────────────────────────────────────────
def save_and_push(master_obj: dict, markdown: str):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    master_path = f"{RESULTS_DIR}/master_{RUN_TS}.json"
    md_path = f"{REPORTS_DIR}/intel_report_{RUN_TS}.md"
    
    with open(master_path, "w") as f:
        json.dump(master_obj, f, indent=2)
    print(f"✅ Saved: {master_path}")
    
    with open(md_path, "w") as f:
        f.write(markdown)
    print(f"✅ Saved: {md_path}")
    
    # Copy to Obsidian
    os.makedirs(OBSIDIAN_DIR, exist_ok=True)
    obsidian_path = f"{OBSIDIAN_DIR}/Intel-Report-{RUN_TS}.md"
    with open(obsidian_path, "w") as f:
        f.write(markdown)
    print(f"✅ Obsidian: {obsidian_path}")
    
    # GitHub commit + push
    try:
        subprocess.run(["git", "add", f"intel_swarm/reports/intel_report_{RUN_TS}.md", f"intel_swarm/results/master_{RUN_TS}.json"], 
                     cwd=WORKSPACE, capture_output=True, check=True)
        result = subprocess.run(["git", "commit", "-m", f"Intel Report {RUN_TS} — {SGT_TS}"], 
                               cwd=WORKSPACE, capture_output=True, text=True, check=True)
        print(f"✅ Git commit: {result.stdout.strip()}")
        
        push_result = subprocess.run(["git", "push"], cwd=WORKSPACE, capture_output=True, text=True)
        if push_result.returncode == 0:
            print("✅ GitHub pushed")
        else:
            print(f"⚠️ Git push failed (may be no changes): {push_result.stderr.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Git error: {e.stderr if e.stderr else str(e)}")
    
    return md_path

# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"=== Intel Swarm Standalone (MiniMax) | TS: {RUN_TS} | {SGT_TS} ===")
    print(f"MiniMax API key: {'✅ set' if MINIMAX_API_KEY else '❌ MISSING'}")
    
    # Check for existing domain files (from sub-agent run)
    geo_path = f"{RESULTS_DIR}/geopolitics_{RUN_TS}.json"
    fin_path = f"{RESULTS_DIR}/finance_{RUN_TS}.json"
    climate_path = f"{RESULTS_DIR}/climate_{RUN_TS}.json"
    
    if os.path.exists(geo_path) and os.path.exists(fin_path) and os.path.exists(climate_path):
        print("\n📁 Found existing domain files from sub-agent run — skipping domain analysis")
        geo = json.loads(read_file(geo_path))
        fin = json.loads(read_file(fin_path))
        climate = json.loads(read_file(climate_path))
    else:
        news = get_latest_bloomberg()
        
        print("\n📡 Running Geopolitics analysis...")
        geo = run_domain("geopolitics", news)
        with open(f"{RESULTS_DIR}/geopolitics_{RUN_TS}.json", "w") as f:
            json.dump(geo, f, indent=2)
        insights = geo.get("key_insights", []) if isinstance(geo, dict) else []
        print(f"  → {len(insights)} insights | errors: {'yes' if 'error' in geo else 'no'}")
        
        print("\n📡 Running Finance analysis...")
        fin = run_domain("finance", news)
        with open(f"{RESULTS_DIR}/finance_{RUN_TS}.json", "w") as f:
            json.dump(fin, f, indent=2)
        insights = fin.get("key_insights", []) if isinstance(fin, dict) else []
        print(f"  → {len(insights)} insights | errors: {'_raw' in fin}")
        
        print("\n📡 Running Climate analysis...")
        climate = run_domain("climate", news)
        with open(f"{RESULTS_DIR}/climate_{RUN_TS}.json", "w") as f:
            json.dump(climate, f, indent=2)
        insights = climate.get("key_insights", []) if isinstance(climate, dict) else []
        print(f"  → {len(insights)} insights | errors: {'_raw' in climate}")
    
    print("\n🧠 Synthesizing master report...")
    master = synthesize(geo, fin, climate)
    
    if "error" in master and len(master) == 1:
        print(f"  ⚠️ Synthesis failed: {master.get('error')}")
        print(f"  Raw: {master.get('raw','')[:200]}")
        sys.exit(1)
    
    master_json_str = json.dumps(master, indent=2)
    
    print("\n📝 Generating markdown...")
    md = generate_markdown(master, geo, fin, climate)
    
    print("\n💾 Saving and pushing...")
    md_path = save_and_push(master, md)
    
    print(f"\n=== ✅ DONE | TS: {RUN_TS} ===")
    print(f"\nCrisis: {master.get('crisis_line', 'N/A')}")
    print(f"\nTelegram Summary:")
    print(f"> {master.get('telegram_summary', 'N/A')}")
    
    # ── ASCR Bridge: sync to InvestBot ───────────────────────────────────────
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, f"{WORKSPACE}/intel_swarm/ascr_bridge.py"],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            print(f"\n🔗 ASCR Bridge: ✅ Synced to InvestBot")
        else:
            print(f"\n🔗 ASCR Bridge: ⚠️ {result.stderr[:100]}")
    except Exception as e:
        print(f"\n🔗 ASCR Bridge: ⚠️ {e}")
