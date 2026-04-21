#!/usr/bin/env python3
"""
Macro-Driven Daily Market Report: Top-down analysis from global macro to individual assets.
Follows: Macro Overview → Sector Analysis → Individual Assets → Action Plan
"""

import urllib.request
import xml.etree.ElementTree as ET
import json
import sys
from datetime import datetime
import time
import re

# ========== CONFIGURATION ==========
ASSETS = {
    "GOLD": ["XAUUSD", "GLD"],
    "TECH": ["MRVL", "AMD", "NVDA", "FIG"],
    "SINGAPORE": ["S63.SI", "Z74.SI"],
    "FOREX": ["USDSGD=X", "SGDJPY=X", "SGDCNY=X", "MYRSGD=X"]
}

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
                    'source': source,
                    'symbol': symbol,
                    'title': title.strip(),
                    'link': link.strip(),
                    'published': pubdate.strip(),
                    'description': description.strip()
                })
                
                if len(articles) >= 3:
                    break
    except Exception as e:
        print(f"Error parsing RSS: {e}")
    
    return articles

# ========== ANALYSIS FUNCTIONS ==========
def analyze_macro_environment(fed_data, oil_data, forex_rates):
    """Analyze global macro environment with reality check."""
    analysis = []
    
    # Fed Policy Analysis
    cut_prob = fed_data["probabilities"].get('cut_25bp', 0) + fed_data["probabilities"].get('cut_50bp', 0)
    hike_prob = fed_data["probabilities"].get('hike_25bp', 0) + fed_data["probabilities"].get('hike_50bp', 0)
    net_dovishness = cut_prob - hike_prob
    
    analysis.append("## 🌍 **MACRO OVERVIEW**")
    analysis.append("### 🏛️ **Monetary Policy (Fed Watch):**")
    
    # Reality check: Market vs Actual Fed stance
    analysis.append(f"**Market Pricing:** {cut_prob:.1f}% cut probability")
    analysis.append(f"**Fed Rhetoric:** 'Higher for longer' (hawkish)")
    analysis.append(f"**Reality Check:** Market expecting cuts, Fed talking hikes/hold")
    analysis.append("")
    
    if net_dovishness > 20:
        analysis.append("**MARKET EXPECTATION: STRONGLY DOVISH**")
        analysis.append(f"• **Market View:** Pricing {cut_prob:.1f}% probability of cuts")
        analysis.append("• **Contradiction:** Fed says 'higher for longer', geopolitics inflationary")
        analysis.append("• **My Assessment:** Market too optimistic, risk of hawkish surprise")
        analysis.append("• **Impact:** Potential USD strength if market reprices")
    elif net_dovishness > 0:
        analysis.append("**MARKET EXPECTATION: MODERATELY DOVISH**")
        analysis.append(f"• **Market View:** {cut_prob:.1f}% cut vs {hike_prob:.1f}% hike")
        analysis.append("• **Contradiction:** Oil prices rising from Iran tensions")
        analysis.append("• **My Assessment:** Cuts delayed, possibly 2025")
        analysis.append("• **Impact:** Range-bound until clarity")
    else:
        analysis.append("**MARKET EXPECTATION: NEUTRAL/HAWKISH**")
        analysis.append(f"• **Market View:** Hike probability {hike_prob:.1f}%")
        analysis.append("• **Alignment:** Matches Fed 'higher for longer' rhetoric")
        analysis.append("• **My Assessment:** Realistic given inflationary pressures")
        analysis.append("• **Impact:** Defensive positioning warranted")
    
    analysis.append("")
    
    # Oil & Geopolitics - Critical analysis
    analysis.append("### 🛢️ **Commodities & Geopolitics (KEY DRIVER):**")
    analysis.append(f"**Crude Oil:** Brent ${oil_data['brent']} (+{oil_data['change']}%)")
    analysis.append(f"• **Primary Driver:** {oil_data['driver']}")
    analysis.append("• **Inflation Impact:** Direct + secondary effects (transport, goods)")
    analysis.append("• **Fed Dilemma:** Higher oil = stickier inflation = less room for cuts")
    analysis.append("• **My View:** Geopolitical risk premium supporting oil, inflationary")
    analysis.append("")
    
    # Forex Overview with reality check
    analysis.append("### 💱 **Global Forex Dynamics:**")
    usd_sgd = 1 / forex_rates.get('USD', 0) if forex_rates.get('USD') else 0
    analysis.append(f"**USD/SGD:** {usd_sgd:.4f}")
    
    if net_dovishness > 0:
        analysis.append("• **Market View:** USD weakness expected (pricing cuts)")
        analysis.append("• **Reality Check:** Fed may hold/hike due to oil inflation")
        analysis.append("• **Contrarian View:** USD could strengthen if cuts delayed")
        analysis.append("• **Watch:** Oil prices, Fed rhetoric vs market pricing")
    else:
        analysis.append("• **Market View:** USD strength or range-bound")
        analysis.append("• **Alignment:** Matches 'higher for longer' narrative")
        analysis.append("• **My View:** USD supported by geopolitical safe-haven flows")
        analysis.append("• **Watch:** Iran escalation, risk-off sentiment")
    
    analysis.append("")
    
    # Add critical assessment section
    analysis.append("### ⚖️ **CRITICAL ASSESSMENT:**")
    analysis.append("**Market vs Reality Gap:**")
    analysis.append("1. **Market:** Pricing rate cuts (dovish)")
    analysis.append("2. **Fed:** 'Higher for longer' rhetoric (hawkish)")
    analysis.append("3. **Geopolitics:** Iran tensions → Higher oil → Inflationary")
    analysis.append("4. **Conclusion:** Market too optimistic, risk of repricing")
    analysis.append("")
    
    return "\n".join(analysis), net_dovishness

def analyze_sector(net_dovishness, sector_name, symbols):
    """Analyze sector based on macro environment."""
    analysis = []
    
    analysis.append(f"## 📊 **{sector_name.upper()} SECTOR ANALYSIS**")
    
    if sector_name == "GOLD":
        if net_dovishness > 20:
            analysis.append("**OUTLOOK: CAUTIOUSLY BULLISH (WITH REALITY CHECK)**")
            analysis.append("• **Market Expectation:** Lower rates = bullish gold")
            analysis.append("• **Reality Check:** Fed may not cut due to oil inflation")
            analysis.append("• **Geopolitical Catalyst:** Iran tensions = safe-haven demand")
            analysis.append("• **Key Risk:** If cuts delayed, gold could struggle")
            analysis.append("• **Action:** Accumulate slowly, hedge with tactical stops")
        elif net_dovishness > 0:
            analysis.append("**OUTLOOK: NEUTRAL WITH GEOPOLITICAL SUPPORT**")
            analysis.append("• **Market View:** Moderately favorable for gold")
            analysis.append("• **Reality:** Oil inflation limits Fed's dovish options")
            analysis.append("• **Geopolitical:** Middle East tensions support gold")
            analysis.append("• **Risk:** Strong USD if risk-off flows dominate")
            analysis.append("• **Action:** Trade range with geopolitical premium")
        else:
            analysis.append("**OUTLOOK: DEFENSIVE/SAFE-HAVEN**")
            analysis.append("• **Market View:** Higher rates pressure gold")
            analysis.append("• **Geopolitical Reality:** Iran war risk supports gold")
            analysis.append("• **Dual Role:** Inflation hedge + safe-haven")
            analysis.append("• **Risk:** Sustained USD strength")
            analysis.append("• **Action:** Hold as portfolio insurance, not for returns")
    
    elif sector_name == "TECH":
        if net_dovishness > 20:
            analysis.append("**OUTLOOK: VERY BULLISH**")
            analysis.append("• **Why:** Lower rates boost growth stock valuations")
            analysis.append("• **Catalyst:** AI investment cycle accelerating")
            analysis.append("• **Risk:** Valuation excesses, regulatory scrutiny")
            analysis.append("• **Action:** Focus on AI infrastructure leaders (MRVL, NVDA)")
        elif net_dovishness > 0:
            analysis.append("**OUTLOOK: BULLISH**")
            analysis.append("• **Why:** Supportive but selective environment")
            analysis.append("• **Catalyst:** Earnings growth, market share gains")
            analysis.append("• **Risk:** Higher rates could pressure multiples")
            analysis.append("• **Action:** Selective accumulation, favor cash-rich companies")
        else:
            analysis.append("**OUTLOOK: DEFENSIVE**")
            analysis.append("• **Why:** Higher rates pressure growth valuations")
            analysis.append("• **Catalyst:** Strong balance sheets, market dominance")
            analysis.append("• **Risk:** Multiple compression, growth slowdown")
            analysis.append("• **Action:** Focus on profitability, avoid highly leveraged")
    
    elif sector_name == "SINGAPORE":
        analysis.append("**OUTLOOK: DEFENSIVE/STABLE**")
        analysis.append("• **Why:** Singapore market offers stability in uncertainty")
        analysis.append("• **Catalyst:** Government-linked companies provide visibility")
        analysis.append("• **Risk:** Regional economic slowdown, property market")
        analysis.append("• **Action:** Hold for dividends, defensive positioning")
    
    elif sector_name == "FOREX":
        analysis.append("**OUTLOOK: MACRO-DRIVEN**")
        analysis.append("• **Why:** Forex moves on rate differentials, risk sentiment")
        analysis.append("• **Catalyst:** Fed vs other central bank policy divergence")
        analysis.append("• **Risk:** Geopolitical events, sudden risk-off flows")
        analysis.append("• **Action:** Trade ranges, hedge USD exposure if bearish")
    
    analysis.append("")
    analysis.append("**Individual Assets:**")
    
    return "\n".join(analysis)

def analyze_individual_asset(symbol, name, articles, net_dovishness, sector, forex_rates):
    """Analyze individual asset with specific recommendations."""
    analysis = []
    
    analysis.append(f"### **{symbol} - {name}**")
    
    # Current news context
    if articles:
        main_article = articles[0]
        analysis.append(f"**Latest:** {main_article['title']}")
        analysis.append(f"**Source:** {main_article['source']}")
    else:
        analysis.append("**Latest:** No significant recent news")
    
    # Expert view based on symbol
    if symbol == "XAUUSD":
        analysis.append("**My View:** Direct exposure to gold price")
        analysis.append("• **Why track:** Pure gold play, no ETF fees")
        analysis.append("• **Current driver:** Fed policy expectations")
        if net_dovishness > 20:
            analysis.append("• **Action:** BUY - Accumulate for $2,300+ target")
        else:
            analysis.append("• **Action:** HOLD - Wait for clearer Fed direction")
    
    elif symbol == "GLD":
        analysis.append("**My View:** Gold ETF for easy exposure")
        analysis.append("• **Why track:** Liquidity, no storage concerns")
        analysis.append("• **Current driver:** Same as gold + ETF flows")
        if net_dovishness > 20:
            analysis.append("• **Action:** BUY - Use for core gold position")
        else:
            analysis.append("• **Action:** HOLD/SMALL BUY - Dollar-cost average")
    
    elif symbol == "MRVL":
        analysis.append("**My View:** AI infrastructure play")
        analysis.append("• **Why track:** Data center networking, AI chip connectivity")
        analysis.append("• **Current driver:** AI investment cycle, Nvidia partnership")
        if net_dovishness > 0:
            analysis.append("• **Action:** BUY - Core AI infrastructure holding")
        else:
            analysis.append("• **Action:** HOLD - Strong business but watch valuations")
    
    elif symbol == "AMD":
        analysis.append("**My View:** AI challenger to Nvidia")
        analysis.append("• **Why track:** GPU competition, data center growth")
        analysis.append("• **Current driver:** AI chip demand, market share gains")
        analysis.append("• **Action:** BUY - Diversify AI exposure, valuation reasonable")
    
    elif symbol == "NVDA":
        analysis.append("**My View:** AI market leader")
        analysis.append("• **Why track:** Dominant position, pricing power")
        analysis.append("• **Current driver:** Unprecedented AI demand")
        analysis.append("• **Action:** HOLD/BUY ON WEAKNESS - Expensive but dominant")
    
    elif symbol == "FIG":
        analysis.append("**My View:** Design software with AI disruption risk")
        analysis.append("• **Why track:** Market leader facing AI competition")
        analysis.append("• **Current driver:** AI design agents challenging growth")
        analysis.append("• **Action:** CAUTIOUS/HOLD - Monitor AI disruption closely")
    
    elif symbol == "S63.SI":
        analysis.append("**My View:** Singapore defense/engineering stalwart")
        analysis.append("• **Why track:** Government contracts, stability")
        analysis.append("• **Current driver:** Defense spending, infrastructure")
        analysis.append("• **Action:** HOLD - Defensive, dividend income")
    
    elif symbol == "Z74.SI":
        analysis.append("**My View:** Singapore telecom with regional exposure")
        analysis.append("• **Why track:** Dividend yield, ASEAN growth")
        analysis.append("• **Current driver:** 5G rollout, digital services")
        analysis.append("• **Action:** HOLD - For dividend income, defensive")
    
    elif symbol == "USDSGD=X":
        usd_sgd = 1 / forex_rates.get('USD', 0) if forex_rates.get('USD') else 0
        analysis.append(f"**My View:** USD/SGD at {usd_sgd:.4f}")
        analysis.append("• **Why track:** US-Singapore rate differential")
        analysis.append("• **Current driver:** Fed vs MAS policy")
        if net_dovishness > 20:
            analysis.append(f"• **Action:** SELL USD/BUY SGD - Target 1.25-1.28")
        else:
            analysis.append(f"• **Action:** RANGE TRADE - 1.28-1.32")
    
    elif symbol == "SGDJPY=X":
        sgd_jpy = forex_rates.get('JPY', 0)
        analysis.append(f"**My View:** SGD/JPY at {sgd_jpy:.2f}")
        analysis.append("• **Why track:** Carry trade, Asia risk sentiment")
        analysis.append("• **Current driver:** BoJ policy normalization")
        analysis.append("• **Action:** MONITOR - Watch for BoJ policy shifts")
    
    elif symbol == "SGDCNY=X":
        sgd_cny = forex_rates.get('CNY', 0)
        analysis.append(f"**My View:** SGD/CNY at {sgd_cny:.4f}")
        analysis.append("• **Why track:** China economic recovery")
        analysis.append("• **Current driver:** PBOC policy, China growth")
        analysis.append("• **Action:** MONITOR - China data critical")
    
    elif symbol == "MYRSGD=X":
        sgd_myr = forex_rates.get('MYR', 0)
        analysis.append(f"**My View:** SGD/MYR at {sgd_myr:.4f} (1 SGD = {sgd_myr:.4f} MYR)")
        analysis.append("• **Why track:** Malaysia economic reforms")
        analysis.append("• **Current driver:** Commodity prices, reforms")
        analysis.append("• **Action:** HOLD - Long-term SGD strength likely")
    
    analysis.append("")
    return "\n".join(analysis)

def generate_action_plan(net_dovishness):
    """Generate overall action plan."""
    plan = []
    
    plan.append("## 🎯 **OVERALL ACTION PLAN**")
    plan.append("")
    
    if net_dovishness > 20:
        plan.append("**PRIMARY BIAS: CAUTIOUSLY OPTIMISTIC (WITH REALITY CHECK)**")
        plan.append("")
        plan.append("1. **GOLD:** TACTICAL ACCUMULATE - Geopolitical hedge, not rate-cut bet")
        plan.append("2. **TECH:** SELECTIVE OVERWEIGHT - Focus on AI fundamentals, not macro")
        plan.append("3. **USD/SGD:** RANGE TRADE WITH USD BIAS - 1.28-1.32, not 1.25-1.28")
        plan.append("4. **SINGAPORE STOCKS:** OVERWEIGHT DEFENSIVE - Stability in uncertainty")
        plan.append("5. **RISK MANAGEMENT:** 25% cash + HEDGES - Prepare for hawkish surprise")
        
    elif net_dovishness > 0:
        plan.append("**PRIMARY BIAS: MODERATELY RISK-ON**")
        plan.append("")
        plan.append("1. **GOLD:** SELECTIVE BUYING - Below $2,150")
        plan.append("2. **TECH:** SELECTIVE - Focus on value (AMD, MRVL)")
        plan.append("3. **USD/SGD:** RANGE TRADE - 1.28-1.32")
        plan.append("4. **SINGAPORE STOCKS:** HOLD - Defensive allocation")
        plan.append("5. **RISK MANAGEMENT:** 25% cash")
        
    else:
        plan.append("**PRIMARY BIAS: DEFENSIVE**")
        plan.append("")
        plan.append("1. **GOLD:** CAUTIOUS - Trade range $2,000-2,200")
        plan.append("2. **TECH:** UNDERWEIGHT - Focus on quality (NVDA cash-rich)")
        plan.append("3. **USD/SGD:** RANGE/HAVEN - 1.28-1.35")
        plan.append("4. **SINGAPORE STOCKS:** OVERWEIGHT - For stability")
        plan.append("5. **RISK MANAGEMENT:** 30% cash, reduce leverage")
    
    plan.append("")
    plan.append("**KEY MONITORS:**")
    plan.append("1. Fed meeting minutes (April 29)")
    plan.append("2. US inflation data (next release)")
    plan.append("3. China economic indicators")
    plan.append("4. Tech earnings season")
    plan.append("5. Geopolitical developments")
    
    return "\n".join(plan)

# ========== MAIN REPORT FUNCTION ==========
def generate_macro_driven_report():
    """Generate macro-driven report."""
    
    print(f"📊 **MACRO-DRIVEN MARKET REPORT**")
    print(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"**Analysis Framework:** Macro → Sector → Assets → Action")
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
    
    # ========== SECTION 4: RISK ASSESSMENT ==========
    print("## ⚠️ **RISK ASSESSMENT**")
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
    report_filename = f"macro_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(report_filename, 'w') as f:
        f.write(f"Macro-Driven Market Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(macro_analysis + "\n\n")
        f.write(action_plan + "\n\n")
        
        # Save individual asset analysis
        f.write("INDIVIDUAL ASSET ANALYSIS:\n")
        for symbol, articles in all_articles.items():
            if articles:
                f.write(f"{symbol}: {articles[0]['title'][:100]}...\n")
    
    print(f"✅ Report saved to: {report_filename}")
    print("\n" + "="*60)
    print("END OF MACRO-DRIVEN REPORT")
    print("="*60)

# ========== MAIN EXECUTION ==========
if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Macro-Driven Market Report")
        print("Usage: python3 daily_report_macro_driven.py")
        print()
        print("Analysis Flow:")
        print("1. Macro Overview (Fed, Oil, Forex)")
        print("2. Sector Analysis (Gold, Tech, Singapore, Forex)")
        print("3. Individual Assets (12 tracked symbols)")
        print("4. Action Plan (Specific recommendations)")
        print("5. Risk Assessment (Top risks & mitigation)")
        sys.exit(0)
    
    generate_macro_driven_report()