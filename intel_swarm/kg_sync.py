#!/usr/bin/env python3
"""
Intel Swarm → ASCR Knowledge Graph Sync
Reads Intel Swarm master reports and adds new nodes/edges to ASCR's knowledge graph.
Run after each Intel Swarm synthesis.
"""
import sys
import json
import uuid
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/yeoel/.openclaw/workspace")
KG_DIR = Path("/home/yeoel/openclaw_radar/data")
EDGES_NDJSON = KG_DIR / "edges.ndjson"
EDGES_GRAPH_V2 = KG_DIR / "edges_graph_v2.json"

# ─── Load existing edges ────────────────────────────────────────────────────────
def load_existing():
    existing_ndjson = set()
    if EDGES_NDJSON.exists():
        with open(EDGES_NDJSON) as f:
            for line in f:
                try:
                    e = json.loads(line)
                    existing_ndjson.add((e.get("source",""), e.get("target",""), e.get("relation","")))
                except:
                    pass
    
    with open(EDGES_GRAPH_V2) as f:
        g = json.load(f)
    existing_node_ids = {n["id"] for n in g["nodes"]}
    existing_graph_edges = set()
    for e in g["edges"]:
        existing_graph_edges.add((e.get("source",""), e.get("target",""), e.get("relation","")))
    
    return existing_ndjson, existing_node_ids, existing_graph_edges, g


def slugify(text: str) -> str:
    """Convert text to valid node ID slug."""
    import re
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", "_", text)
    return text[:60]


def build_edges_from_master(master: dict, ts: str) -> tuple[list, list]:
    """Extract nodes and edges from Intel Swarm master report."""
    nodes = []
    edges = []
    
    theme = master.get("crisis_line", "")
    if theme:
        node_id = slugify(theme[:40])
        nodes.append({
            "id": f"is_{ts}_{node_id}",
            "label": f"IS: {theme[:50]}",
            "type": "event",
            "category": "intel_swarm",
            "raw_names": [theme.lower()],
            "asset_type": "index",
            "ticker": "WM_GLOBAL",
            "source": "intel_swarm"
        })
        edges.append({
            "source": f"is_{ts}_{node_id}",
            "target": "wm_global",
            "relation": "maps_to",
            "reason": f"Intel Swarm crisis line: {theme[:60]}",
            "tier": 0,
            "strength": 0.9,
            "lag_days": 0,
            "confidence": 0.85,
            "sign": "negative",
            "transmission_type": "intel_swarm",
            "edge_id": f"is_{ts}_{uuid.uuid4().hex[:8]}"
        })
    
    for i, t in enumerate(master.get("key_themes", [])):
        theme_name = t.get("theme", "")
        if not theme_name:
            continue
        node_id = slugify(theme_name)
        node = {
            "id": f"is_{ts}_{node_id}",
            "label": f"IS: {theme_name[:50]}",
            "type": "event",
            "category": "intel_swarm",
            "raw_names": [theme_name.lower(), t.get("description","")[:200].lower()],
            "asset_type": "index",
            "ticker": "WM_GLOBAL",
            "source": "intel_swarm"
        }
        nodes.append(node)
        
        # Map to relevant asset classes based on keywords
        asset_map = {
            "oil": "OIH", "energy": "OIH", "fuel": "OIH", "gas": "UNG",
            "military": "ITA", "defense": "ITA", "war": "ITA",
            "flood": "IACL", "climate": "IACL", "wildfire": "IACL", "hurricane": "IACL",
            "silver": "SLV", "gold": "GLD", "precious": "GLD",
            "sp500": "SPY", "equities": "SPY", "nasdaq": "QQQ", "market": "SPY",
            "credit": "LQD", "bonds": "AGG", "dollar": "UUP",
            "shipping": "GDX", "tanker": "GDX", "freight": "GDX",
            "chip": "SMH", "semiconductor": "SMH", "tech": "QQQ",
            "ai": "ARKK", "data center": "ARKK",
            "fertilizer": "DJP", "agriculture": "DJP", "food": "DJP",
        }
        
        target = None
        for kw, ticker in asset_map.items():
            if kw in theme_name.lower() or kw in t.get("description","").lower():
                target = ticker
                break
        
        if not target:
            target = "SPY"  # Default fallback
        
        edges.append({
            "source": f"is_{ts}_{node_id}",
            "target": target.lower(),
            "relation": "affects",
            "reason": f"Intel Swarm theme: {theme_name[:80]}",
            "tier": 1,
            "strength": 0.7,
            "lag_days": 0,
            "confidence": 0.7,
            "sign": "negative",
            "transmission_type": "intel_swarm",
            "edge_id": f"is_{ts}_{uuid.uuid4().hex[:8]}"
        })
    
    # Alpha opportunities → trading signals
    for i, a in enumerate(master.get("alpha_opportunities", [])):
        angle = a.get("angle", "")
        if not angle:
            continue
        node_id = slugify(angle[:40])
        nodes.append({
            "id": f"is_alpha_{ts}_{node_id}",
            "label": f"IS Alpha: {angle[:50]}",
            "type": "signal",
            "category": "alpha",
            "raw_names": [angle.lower(), a.get("rationale","")[:200].lower()],
            "asset_type": "strategy",
            "ticker": "WM_GLOBAL",
            "source": "intel_swarm"
        })
        
        risk = a.get("risk", "MEDIUM")
        risk_map = {"HIGH": "short", "MEDIUM": "long", "LOW": "long"}
        action = risk_map.get(risk, "long")
        
        # Infer target asset from angle keywords
        target = "SPY"
        for kw, ticker in {
            "silver": "SLV", "gold": "GLD", "oil": "OIH", "energy": "OIH",
            "volatility": "VIXY", "vix": "VIXY", "put": "SPY", "call": "SPY",
            "short": "SH", "long": "SPY", "cybersecurity": "CIBR",
            "defense": "ITA", "military": "ITA",
        }.items():
            if kw in angle.lower():
                target = ticker
                break
        
        edges.append({
            "source": f"is_alpha_{ts}_{node_id}",
            "target": target.lower(),
            "relation": action,
            "reason": f"Alpha: {angle[:80]} | Rationale: {a.get('rationale','')[:80]} | Risk: {risk}",
            "tier": 1 if risk == "HIGH" else 2,
            "strength": 0.65,
            "lag_days": 7,
            "confidence": 0.6,
            "sign": "positive" if action == "long" else "negative",
            "transmission_type": "alpha_signal",
            "edge_id": f"is_a_{ts}_{uuid.uuid4().hex[:8]}"
        })
    
    return nodes, edges


def sync_knowledge_graph(master_path: str = None):
    """Main sync function — reads latest Intel Swarm master and updates KG."""
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
    
    print(f"Syncing knowledge graph with Intel Swarm report: {ts}")
    
    with open(latest) as f:
        master = json.load(f)
    
    existing_ndjson, existing_node_ids, existing_graph_edges, g = load_existing()
    
    new_nodes, new_edges = build_edges_from_master(master, ts)
    
    added_nodes = 0
    added_edges_ndjson = 0
    added_edges_graph = 0
    
    # Add nodes to graph_v2
    for node in new_nodes:
        if node["id"] not in existing_node_ids:
            g["nodes"].append(node)
            added_nodes += 1
    
    # Add edges to ndjson
    with open(EDGES_NDJSON, "a") as f:
        for edge in new_edges:
            key = (edge["source"], edge["target"], edge["relation"])
            if key not in existing_ndjson:
                f.write(json.dumps(edge) + "\n")
                added_edges_ndjson += 1
    
    # Add edges to graph_v2
    for edge in new_edges:
        key = (edge["source"], edge["target"], edge["relation"])
        if key not in existing_graph_edges:
            g["edges"].append({
                "id": edge.get("edge_id", str(uuid.uuid4())),
                "source": edge["source"],
                "target": edge["target"],
                "relation": edge["relation"],
                "legacy_relation": edge["relation"],
                "legacy_tier": edge.get("tier", 1),
                "strength": edge.get("strength", 0.7),
                "lag_days": edge.get("lag_days", 0),
                "confidence": edge.get("confidence", 0.7),
                "sign": edge.get("sign", "positive"),
                "transmission_type": edge.get("transmission_type", "direct"),
                "reason": edge.get("reason", ""),
                "source_db": "intel_swarm_sync"
            })
            added_edges_graph += 1
    
    # Save graph_v2
    with open(EDGES_GRAPH_V2, "w") as f:
        json.dump(g, f, indent=2)
    
    print(f"  Nodes added: {added_nodes}")
    print(f"  Edges added (ndjson): {added_edges_ndjson}")
    print(f"  Edges added (graph_v2): {added_edges_graph}")
    print(f"  Total nodes: {len(g['nodes'])}")
    
    # Count ndjson lines
    with open(EDGES_NDJSON) as f:
        total_edges = sum(1 for _ in f)
    print(f"  Total edges (ndjson): {total_edges}")


if __name__ == "__main__":
    master_path = sys.argv[1] if len(sys.argv) > 1 else None
    sync_knowledge_graph(master_path)
