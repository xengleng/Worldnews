#!/usr/bin/env python3
"""
Macro-Driven Daily Market Report with RAG Knowledge Base integration.
Adds relevant insights from your flat‑file knowledge base.
"""

import urllib.request
import xml.etree.ElementTree as ET
import json
import sys
from datetime import datetime
import time
import re
import subprocess
import os

# ========== CONFIGURATION ==========
ASSETS = {
    "GOLD": ["XAUUSD", "GLD"],
    "TECH": ["MRVL", "AMD", "NVDA", "FIG"],
    "SINGAPORE": ["S63.SI", "Z74.SI"],
    "FOREX": ["USDSGD=X", "SGDJPY=X", "SGDCNY=X", "MYRSGD=X"]
}

# ========== RAG INTEGRATION ==========
def get_rag_insights(topic: str) -> str:
    """
    Query the flat‑file RAG for insights on a topic.
    Returns formatted markdown string.
    """
    try:
        # Try to import directly
        sys.path.append(os.path.dirname(__file__))
        from rag_query import get_insights
        return get_insights(topic)
    except ImportError:
        # Fallback: run rag_query.py as subprocess
        cmd = [sys.executable, "rag_query.py", topic]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(__file__))
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        return ""

# ========== DATA FETCHING FUNCTIONS ==========
def fetch_forex_rates():
    """Fetch current forex rates for SGD pairs."""
    try:
        url = "https://api.exchangerate-api.com/v4/latest/SGD"
        headers = {'User-Agent': 'Mozilla/5.0 (OpenClaw Market Monitor)'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('rates', {})
    except Exception as e:
        print(f"Error fetching forex rates: {e}")
        return {}

def fetch_fedwatch_data():
    """Fetch FedWatch data (placeholder - would integrate with CME data)."""
    return {
        "next_meeting": "2026-04-29",
        "current_rate": "4.25-4.50%",
        "probabilities": {
            "no_change": 45.2,
            "cut_25bp": 32.1,
            "cut_50bp": 15.7,
            "hike_25bp": 5.3,
            "hike_50bp": 1.7
        },
        "trend": "leaning_dovish",
        "last_updated": datetime.now().isoformat()
    }

def fetch_oil_price():
    """Fetch crude oil price (placeholder)."""
    # In production: Fetch from API (Brent, WTI)
    return {
        "brent": 85.42,
        "wti": 82.15,
        "change": +1.8,
        "driver": "Geopolitical tensions in Middle East",
        "trend": "Bullish"
    }

def fetch_rss_feed(url):
    """Fetch and parse RSS feed."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (OpenClaw Market Monitor)'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_rss(xml_content, source, symbol):
    """Parse RSS XML and extract articles."""
    articles = []
    if not xml_content:
        return articles
    
    try:
        xml_content = re.sub(r'xmlns="[^"]+"', '', xml_content)
        xml_content = re.sub(r'xmlns:[^=]+="[^"]+"', '', xml_content)
        root = ET.fromstring(xml_content)
        
        for item in root.findall('.//item'):
            title_elem = item.find('title')
            link_elem = item.find('link')
            pubdate_elem = item.find('pubDate') or item.find('date')
            desc_elem = item.find('description')
            
            if title_elem is not None and link_elem is not None:
                title = title_elem.text or ''
                link = link_elem.text or ''
                pubdate = pubdate_elem.text if pubdate_elem is not None else ''
                description = desc_elem.text if desc_elem is not None else ''
                
                description = re.sub(r'<[^>]+>', '', description)
                description = description[:200] + '...' if len(description) > 200 else description
                
                articles.append({
                    'title': title,
                    'link': link,
                    'pubdate': pubdate,
                    'description': description,
                    'source': source,
                    'symbol': symbol
                })
    except Exception as e:
        print(f"Error parsing RSS: {e}")
    
    return articles

# ========== ANALYSIS FUNCTIONS ==========
def analyze_macro_environment(fed_data, oil_data, forex_rates):
    """Analyze macro environment."""
    net_dovishness = 0.0
    
    # Calculate net dovishness from Fed probabilities
    prob = fed_data.get("probabilities", {})
    net_dovishness = (
        prob.get("cut_25bp", 0) * 0.25 +
        prob.get("cut_50bp", 0) * 0.5 -
        prob.get("hike_25bp", 0) * 0.25 -
        prob.get("hike_50bp", 0) * 0.5
    )
    
    analysis = []
    analysis.append("## 🌍 **MACRO OVERVIEW**")
    analysis.append("-" * 50)
    analysis.append(f"**Monetary Policy (Fed):** {fed_data.get('current_rate', 'N/A')}")
    analysis.append(f"**Next FOMC:** {fed_data.get('next_meeting', 'N/A')}")
    analysis.append(f"**Market Sentiment:** {fed_data.get('trend', 'N/A').replace('_', ' ').title()}")
    analysis.append(f"**Net Dovishness:** {net_dovishness:+.1f}%")
    analysis.append(f"**Oil (Brent):** ${oil_data.get('brent', 0):.2f} ({oil_data.get('change', 0):+.1f}%)")
    analysis.append(f"**Driver:** {oil_data.get('driver', 'N/A')}")
    analysis.append(f"**Trend:** {oil_data.get('trend', 'N/A')}")
    analysis.append("")
    
    # Add RAG insights for macro
    rag_macro = get_rag_insights("Fed monetary policy macro outlook")
    if rag_macro:
        analysis.append(rag_macro)
    
    return "\n".join(analysis), net_dovishness

def analyze_sector(net_dovishness, sector_name, symbols):
    """Analyze a sector."""
    analysis = []
    
    # Sector‑specific logic
    if sector_name == "GOLD":
        if net_dovishness > 20:
            outlook = "Bullish (dovish Fed supports gold)"
        elif net_dovishness < -10:
            outlook = "Cautious (hawkish Fed pressures gold)"
        else:
            outlook = "Neutral"
    elif sector_name == "TECH":
        if net_dovishness > 15:
            outlook = "Bullish (lower rates boost growth stocks)"
        else:
            outlook = "Selective (focus on quality)"
    elif sector_name == "SINGAPORE":
        outlook = "Stable (defensive, dividend focus)"
    elif sector_name == "FOREX":
        if net_dovishness > 20:
            outlook = "USD weakness expected"
        else:
            outlook = "Range‑bound"
    else:
        outlook = "Neutral"
    
    analysis.append(f"**Outlook:** {outlook}")
    
    # Add RAG insights for this sector
    rag_sector = get_rag_insights(f"{sector_name} sector stocks forex")
    if rag_sector:
        analysis.append("")
        analysis.append(rag_sector)
    
    return "\n".join(analysis)

def analyze_individual_asset(symbol, name, articles, net_dovishness, sector_name, forex_rates):
    """Analyze an individual asset."""
    analysis = []
    
    # Placeholder price/change
    price = 100.0
    change = 0.5
    
    analysis.append(f"  • **{name} ({symbol}):** ${price:.2f} ({change:+.1f}%)")
    
    # News snippet
    if articles:
        latest = articles[0]
        analysis.append(f"    📰 {latest['title'][:80]}...")
    
    # Forex‑specific logic
    if "SGD" in symbol:
        if "USD" in symbol:
            rate = forex_rates.get("USD", 1.0)
            analysis.append(f"    💱 Rate: {rate:.4f}")
        elif "JPY" in symbol:
            rate = forex_rates.get("JPY", 1.0)
            analysis.append(f"    💱 Rate: {rate:.4f}")
        elif "CNY" in symbol:
            rate = forex_rates.get("CNY", 1.0)
            analysis.append(f"    💱 Rate: {rate:.4f}")
        elif "MYR" in symbol:
            rate = forex_rates.get("MYR", 1.0)
            analysis.append(f"    💱 Rate: {rate:.4f}")
    
    return "\n".join(analysis)

def generate_action_plan(net_dovishness):
    """Generate action plan based on macro outlook."""
    plan = []
    plan.append("## 🎯 **ACTION PLAN**")
    plan.append("-" * 50)
    
    if net_dovishness > 20:
        plan.append("**Strategy:** Risk‑on, add exposure")
        plan.append("• **Gold:** Accumulate on dips")
        plan.append("• **Tech:** Favor growth names")
        plan.append("• **Forex:** Short USD against SGD/JPY")
        plan.append("• **Singapore Stocks:** Hold for dividends")
    elif net_dovishness > 0:
        plan.append("**Strategy:** Cautiously optimistic")
        plan.append("• **Gold:** Hold existing positions")
        plan.append("• **Tech:** Selective buying")
        plan.append("• **Forex:** Range‑trade USD pairs")
        plan.append("• **Singapore Stocks:** Accumulate slowly")
    elif net_dovishness < -10:
        plan.append("**Strategy:** Defensive, reduce risk")
        plan.append("• **Gold:** Lighten positions")
        plan.append("• **Tech:** Take profits")
        plan.append("• **Forex:** Long USD, short risk currencies")
        plan.append("• **Singapore Stocks:** Hold defensives")
    else:
        plan.append("**Strategy:** Neutral, wait for clarity")
        plan.append("• Maintain current allocations")
        plan.append("• Keep cash for opportunities")
        plan.append("• Review in 1‑2 weeks")
    
    # Add RAG insights for action planning
    rag_action = get_rag_insights("investment action plan strategy")
    if rag_action:
        plan.append("")
        plan.append(rag_action)
    
    return "\n".join(plan)

# ========== MAIN REPORT FUNCTION ==========
def generate_macro_driven_report():
    """Generate macro-driven report with RAG insights."""
    
    print(f"📊 **MACRO-DRIVEN MARKET REPORT (with Knowledge Base)**")
    print(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"**Analysis Framework:** Macro → Sector → Assets → Action → Knowledge")
    print()
    
    # Fetch all data
    print("📡 Fetching market data...")
    forex_rates = fetch_forex_rates()
    fed_data = fetch_fedwatch_data()
    oil_data = fetch_oil_price()
    
    # ========== SECTION 1: MACRO OVERVIEW ==========
    macro_analysis, net_dovishness = analyze_macro_environment(fed_data, oil_data, forex_rates)
    print(macro_analysis)
    
    # ========== SECTION 2: SECTOR ANALYSIS ==========
    print("## 📈 **SECTOR-BY-SECTOR ANALYSIS**")
    print("-" * 50)
    
    all_articles = {}
    
    for sector_name, symbols in ASSETS.items():
        print(f"\n**{sector_name} Sector:**")
        sector_analysis = analyze_sector(net_dovishness, sector_name, symbols)
        print(sector_analysis)
        
        # Fetch news for each symbol in sector
        for symbol in symbols:
            name = {
                "XAUUSD": "Gold Spot", "GLD": "SPDR Gold ETF",
                "MRVL": "Marvell Tech", "AMD": "Advanced Micro Devices",
                "NVDA": "NVIDIA", "FIG": "Figma Inc",
                "S63.SI": "ST Engineering", "Z74.SI": "SingTel",
                "USDSGD=X": "USD/SGD", "SGDJPY=X": "SGD/JPY",
                "SGDCNY=X": "SGD/CNY", "MYRSGD=X": "SGD/MYR"
            }.get(symbol, symbol)
            
            yahoo_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
            yahoo_xml = fetch_rss_feed(yahoo_url)
            articles = parse_rss(yahoo_xml, "Yahoo Finance", symbol)
            all_articles[symbol] = articles
            
            # Analyze individual asset
            asset_analysis = analyze_individual_asset(symbol, name, articles, net_dovishness, sector_name, forex_rates)
            print(asset_analysis)
            
            time.sleep(0.3)  # Rate limiting
    
    # ========== SECTION 3: ACTION PLAN ==========
    action_plan = generate_action_plan(net_dovishness)
    print(action_plan)
    
    # ========== SECTION 4: KNOWLEDGE BASE SUMMARY ==========
    print("## 🧠 **KNOWLEDGE BASE SUMMARY**")
    print("-" * 50)
    print("**Relevant insights from your knowledge base:**")
    
    # Query RAG for key topics
    topics = ["FedWatch integration", "forex monitoring", "gold price", "Singapore stocks", "home loan rates"]
    for topic in topics:
        insights = get_rag_insights(topic)
        if insights:
            print(f"\n**{topic.title()}:**")
            # Just show first insight
            lines = insights.split("\n")
            for line in lines[:4]:
                if line.strip():
                    print(f"  {line}")
    
    # ========== SECTION 5: RISK ASSESSMENT ==========
    print("\n## ⚠️ **RISK ASSESSMENT**")
    print("-" * 50)
    print("**Top 5 Risks:**")
    print("1. **Fed Policy Error:** Cutting too soon (inflation) or too late (recession)")
    print("2. **Geopolitical Escalation:** Middle East tensions impacting oil")
    print("3. **China Slowdown:** Affecting Asian currencies and regional growth")
    print("4. **Tech Valuation Excess:** AI bubble concerns")
    print("5. **USD Strength:** Contrary to dovish expectations")
    print()
    
    print("**Risk Mitigation:**")
    print("• Maintain cash reserves for opportunities")
    print("• Diversify across sectors and geographies")
    print("• Use stop-losses on tactical positions")
    print("• Hedge USD exposure if heavily positioned")
    print()
    
    # ========== SAVE REPORT ==========
    report_filename = f"macro_report_with_rag_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(report_filename, 'w') as f:
        f.write(f"Macro-Driven Market Report with RAG - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(macro_analysis + "\n\n")
        f.write(action_plan + "\n\n")
        
        # Save knowledge base insights
        f.write("KNOWLEDGE BASE INSIGHTS:\n")
        for topic in topics:
            insights = get_rag_insights(topic)
            if insights:
                f.write(f"{topic}: {insights[:200]}...\n")
    
    print(f"✅ Report saved to: {report_filename}")
    print("\n" + "="*60)
    print("END OF MACRO-DRIVEN REPORT WITH KNOWLEDGE BASE")
    print("="*60)

# ========== MAIN EXECUTION ==========
if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Macro-Driven Market Report with RAG Knowledge Base")
        print("Usage: python3 daily_report_with_rag.py")
        print()
        print("Integrates your flat‑file knowledge base (finance, tech, projects)")
        print("into the market analysis for contextual insights.")
        sys.exit(0)
    
    generate_macro_driven_report()