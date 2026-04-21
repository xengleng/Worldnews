#!/usr/bin/env python3
"""
Intel Swarm → ASCR Bridge
After each Intel Swarm run, this script:
1. Reads the master JSON report
2. Extracts CRITICAL/HIGH insights
3. Injects them as leads directly into ASCR leads DB (Option B)
4. Expands threat_vectors.txt with new Intel Swarm phrases (Option C)
5. Syncs new edges to the knowledge graph
"""
import sys
import json
import sqlite3
import re
import uuid
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/yeoel/.openclaw/workspace")
KG_DIR = Path("/home/yeoel/openclaw_radar/data")
ASCR_DB = KG_DIR / "radar_vault.db"
EDGES_NDJSON = KG_DIR / "edges.ndjson"
EDGES_GRAPH_V2 = KG_DIR / "edges_graph_v2.json"
THREAT_VECTORS = KG_DIR / "threat_vectors.txt"

# ─── Sector Mapping ────────────────────────────────────────────────────────────────
SECTOR_MAP = {
    "oil": "OIH", "energy": "OIH", "fuel": "OIH", "gas": "UNG",
    "military": "ITA", "defense": "ITA", "war": "ITA", "strike": "ITA",
    "flood": "IACL", "climate": "IACL", "wildfire": "IACL", "hurricane": "IACL", "disaster": "IACL",
    "silver": "SLV", "gold": "GLD", "precious": "GLD", "copper": "CPER",
    "sp500": "SPY", "equities": "SPY", "nasdaq": "QQQ", "market": "SPY", "stocks": "SPY",
    "credit": "LQD", "bonds": "AGG", "dollar": "UUP", "forex": "UUP",
    "shipping": "GDX", "tanker": "GDX", "freight": "GDX", "logistics": "GDX",
    "chip": "SMH", "semiconductor": "SMH", "tech": "QQQ", "ai": "ARKK", "data center": "ARKK",
    "fertilizer": "DJP", "agriculture": "DJP", "food": "DJP", "crop": "DJP",
    "cyber": "CIBR", "hack": "CIBR", "ransomware": "CIBR",
    "recession": "SH", "slowdown": "SH", "contraction": "SH",
    "inflation": "TIP", "rates": "TBF", "rate": "TBF", "central bank": "TBF",
    "china": "FXI", "taiwan": "SMH", "korea": "EWY", "japan": "EWJ",
    "europe": "VGK", "germany": "EWG", "uk": "EWU", "france": "EWQ",
    "russia": "RSX", "brazil": "EWZ", "india": "EPI", "africa": "AFK",
    "banking": "KBE", "financial": "KBE", "loan": "KBE",
    "healthcare": "XLV", "pharma": "XLV", "biotech": "IBB",
    "retail": "XRT", "consumer": "XRT",
    "real estate": "IYR", "property": "IYR",
    "infrastructure": "IGF", "construction": "IGF",
    "nuclear": "NCR", "radiation": "NCR",
    "refinery": "XOM", "pipeline": "AMLP",
}

ALERT_TICKER = "WM_GLOBAL"

def infer_ticker(text: str) -> str:
    text_lower = text.lower()
    for keyword, ticker in SECTOR_MAP.items():
        if keyword in text_lower:
            return ticker
    return "SPY"  # Default

def infer_tier(alert_level: str) -> int:
    mapping = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    return mapping.get(alert_level.upper(), 2)

def load_threat_phrases() -> set:
    phrases = set()
    if THREAT_VECTORS.exists():
        with open(THREAT_VECTORS) as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                parts = line.rstrip().split('\t')
                if parts:
                    phrases.add(parts[0].lower())
    return phrases

def load_existing_edges() -> set:
    edges = set()
    if EDGES_NDJSON.exists():
        with open(EDGES_NDJSON) as f:
            for line in f:
                try:
                    e = json.loads(line)
                    edges.add((e.get("source",""), e.get("target",""), e.get("relation","")))
                except:
                    pass
    return edges

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", "_", text)
    return text[:50]

def run_bridge(master_path: str = None):
    """Main bridge function."""
    import glob

    if master_path:
        files = [master_path]
    else:
        files = sorted(glob.glob(str(WORKSPACE / "intel_swarm/results/master_*.json")))

    if not files:
        print("No Intel Swarm master reports found")
        return

    latest = files[-1]
    ts = Path(latest).stem.replace("master_", "")
    print(f"Running ASCR bridge for: {ts}")

    with open(latest) as f:
        master = json.load(f)

    # ── 1. Extract insights and inject into ASCR leads DB ─────────────────────
    conn = sqlite3.connect(str(ASCR_DB))
    now = datetime.now().isoformat()

    # Check for existing leads from this run
    existing = conn.execute(
        "SELECT headline FROM leads WHERE ticker = ? AND timestamp > datetime('now', '-6 hours')",
        (ALERT_TICKER,)
    ).fetchall()
    existing_headlines = {r[0] for r in existing}

    added_leads = 0

    # From key_themes
    for theme in master.get("key_themes", []):
        lvl = theme.get("alert_level", "MEDIUM")
        if lvl in ("CRITICAL", "HIGH"):
            headline = f"[AUTO] {theme.get('theme', '')}: {theme.get('description', '')[:100]}"
            if headline not in existing_headlines:
                conn.execute("""
                    INSERT INTO leads (timestamp, ticker, headline, source, status, threat_score, tier_level)
                    VALUES (?, ?, ?, ?, 'pending', 1.0, ?)
                """, (now, ALERT_TICKER, headline, f"IntelSwarm/{ts}", infer_tier(lvl)))
                existing_headlines.add(headline)
                added_leads += 1

    # From alerts_summary CRITICAL/HIGH
    for lvl, items in master.get("alerts_summary", {}).items():
        if lvl in ("CRITICAL", "HIGH"):
            for item in items:
                headline = f"[AUTO] {item}"
                if headline not in existing_headlines:
                    conn.execute("""
                        INSERT INTO leads (timestamp, ticker, headline, source, status, threat_score, tier_level)
                        VALUES (?, ?, ?, ?, 'pending', 1.0, ?)
                    """, (now, ALERT_TICKER, headline, f"IntelSwarm/{ts}", infer_tier(lvl)))
                    existing_headlines.add(headline)
                    added_leads += 1

    conn.commit()
    print(f"  Leads injected: {added_leads}")

    # ── 2. Expand threat_vectors.txt ──────────────────────────────────────────
    existing_phrases = load_threat_phrases()
    new_vectors = []

    for theme in master.get("key_themes", []):
        theme_name = theme.get("theme", "")
        alert_lvl = theme.get("alert_level", "MEDIUM")
        tier = infer_tier(alert_lvl)
        category = f"tier{tier}_intel_swarm"

        # Add theme name
        phrase = slugify(theme_name).replace("_", " ")
        if phrase not in existing_phrases and len(phrase) > 4:
            new_vectors.append((phrase, category, str(tier)))
            existing_phrases.add(phrase)

        # Add key phrases from description
        for kw in theme.get("description", "").split()[:8]:
            kw_clean = re.sub(r"[^a-z0-9]", "", kw.lower())
            if kw_clean not in existing_phrases and len(kw_clean) > 4:
                new_vectors.append((kw_clean, category, str(tier)))
                existing_phrases.add(kw_clean)

    if new_vectors:
        with open(THREAT_VECTORS, "a") as f:
            f.write(f"\n# === INTEL SWARM AUTO-SYNC {ts} ===\n")
            for phrase, cat, tier in new_vectors:
                f.write(f"{phrase}\t{cat}\t{tier}\n")
        print(f"  Threat vectors added: {len(new_vectors)}")

    # ── 3. Sync edges to knowledge graph ─────────────────────────────────────
    existing_edges = load_existing_edges()
    new_edges = []

    for theme in master.get("key_themes", []):
        theme_name = theme.get("theme", "")
        node_id = f"is_{ts}_{slugify(theme_name)}"
        ticker = infer_ticker(theme_name)

        new_edges.append({
            "source": node_id,
            "target": ticker.lower(),
            "relation": "affects",
            "reason": f"Intel Swarm theme: {theme_name[:80]}",
            "tier": infer_tier(theme.get("alert_level", "MEDIUM")),
            "strength": 0.75,
            "lag_days": 0,
            "confidence": 0.75,
            "sign": "negative",
            "transmission_type": "intel_swarm",
            "edge_id": f"is_{ts}_{uuid.uuid4().hex[:8]}"
        })

    # Alpha opportunities → edges
    for a in master.get("alpha_opportunities", []):
        angle = a.get("angle", "")
        ticker = infer_ticker(angle)
        node_id = f"is_alpha_{ts}_{slugify(angle[:30])}"

        risk_map = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        risk = risk_map.get(a.get("risk", "MEDIUM"), 1)

        new_edges.append({
            "source": node_id,
            "target": ticker.lower(),
            "relation": "alpha",
            "reason": f"Alpha: {angle[:80]} | {a.get('rationale','')[:80]}",
            "tier": risk,
            "strength": 0.65,
            "lag_days": 7,
            "confidence": 0.6,
            "sign": "positive",
            "transmission_type": "alpha_signal",
            "edge_id": f"isa_{ts}_{uuid.uuid4().hex[:8]}"
        })

    added_edges = 0
    with open(EDGES_NDJSON, "a") as f:
        for edge in new_edges:
            key = (edge["source"], edge["target"], edge["relation"])
            if key not in existing_edges:
                f.write(json.dumps(edge) + "\n")
                added_edges += 1

    print(f"  Knowledge graph edges added: {added_edges}")
    print(f"\n✅ ASCR Bridge complete for {ts}")

    conn.close()

if __name__ == "__main__":
    master_path = sys.argv[1] if len(sys.argv) > 1 else None
    run_bridge(master_path)
