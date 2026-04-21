import json

ts = '20260414_0701'
SGT = "2026-04-14 03:01 PM SGT"
UTC = "2026-04-14 07:01 UTC"

domains = {}
for d in ['geopolitics', 'finance', 'climate']:
    with open(f'/home/yeoel/.openclaw/workspace/intel_swarm/results/{d}_{ts}.json') as f:
        domains[d] = json.load(f)

all_insights = []
for d, data in domains.items():
    for i in data.get('insights', []):
        i['domain'] = d
        all_insights.append(i)

alerts = {'critical': [], 'high': [], 'medium': [], 'low': []}
for i in all_insights:
    lvl = i.get('alert_level', 'LOW').lower()
    if lvl in alerts:
        alerts[lvl].append(i['headline'])

level_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
top = sorted(all_insights, key=lambda x: level_order.index(x.get('alert_level', 'LOW')))[:20]

patterns = list(set(sum([d.get('patterns', []) for d in domains.values()], [])))
blinds = list(set(sum([d.get('blind_spots', []) for d in domains.values()], [])))

alpha = [
    {"angle": "Singapore STI Haven Flows", "rationale": "City-state benefiting from safe-haven capital flight amid Iran war uncertainty", "timeframe": "SHORT", "risk": "LOW"},
    {"angle": "Climate Insurance Withdrawal", "rationale": "Insurance companies retreating from high-risk zones — systemic financial risk not yet priced", "timeframe": "MEDIUM", "risk": "HIGH"},
]

key_themes = []
for t in top[:5]:
    key_themes.append({
        "theme": t['headline'][:80],
        "description": t.get('summary', '')[:200],
        "supporting_evidence": [t.get('source_names', [''])[0] if t.get('source_names') else ''],
        "confidence": t.get('alert_level', 'MEDIUM')
    })

master = {
    "report_type": "MASTER_INTELLIGENCE_REPORT",
    "timestamp": ts,
    "sgt_time": SGT,
    "utc_time": UTC,
    "executive_summary": f"Intelligence summary for {SGT}. Key developments: {top[0]['headline'] if top else 'See full report'}.",
    "key_themes": key_themes,
    "alpha_opportunities": alpha,
    "cross_domain_patterns": patterns[:5],
    "blind_spots": blinds[:5],
    "reference_index": [],
    "alerts_summary": alerts
}

out_path = f'/home/yeoel/.openclaw/workspace/intel_swarm/results/master_{ts}.json'
with open(out_path, 'w') as f:
    json.dump(master, f, indent=2)

print(f"Master: {len(alerts['critical'])} CRIT, {len(alerts['high'])} HIGH, {len(alerts['medium'])} MED, {len(alerts['low'])} LOW")
