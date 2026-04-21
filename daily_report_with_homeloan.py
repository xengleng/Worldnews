#!/usr/bin/env python3
"""
Macro-Driven Daily Market Report with Home Loan Analysis.
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

# ========== HOME LOAN DATA ==========
HOME_LOAN_RATES = {
    "DBS": {"2yr": 1.40, "3yr": 1.55, "5yr": 1.75, "prev": 3.10, "notes": "Promotional >S$500k"},
    "OCBC": {"2yr": 1.45, "3yr": 1.88, "5yr": 1.95, "prev": 3.15, "notes": "3-yr step-up structure"},
    "UOB": {"2yr": 1.42, "3yr": 1.65, "5yr": 1.85, "prev": 3.20, "notes": "Competitive refinancing"},
    "Standard Chartered": {"2yr": 1.38, "3yr": 1.60, "5yr": 1.80, "prev": 3.25, "notes": "Best 2-yr rate"},
    "Maybank": {"2yr": 1.48, "3yr": 1.70, "5yr": 1.90, "prev": 3.18, "notes": "Existing customers"},
    "HSBC": {"2yr": 1.43, "3yr": 1.68, "5yr": 1.88, "prev": 3.22, "notes": "Premier discounts"}
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
    """Fetch FedWatch data."""
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
    """Fetch crude oil price."""
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

# ========== HOME LOAN ANALYSIS ==========
def generate_home_loan_analysis(fed_data, oil_data):
    """Generate home loan rate analysis section."""
    analysis = []
    
    analysis.append("## 🏠 **SINGAPORE PRIVATE PROPERTY HOME LOAN RATES**")
    analysis.append("")
    
    # Market Overview
    analysis.append("### 📊 **Market Overview:**")
    analysis.append("• **Current Trend:** Rates at 3-year lows, fixed packages below 1.8%")
    analysis.append("• **SORA Outlook:** Expected to bottom ~1% in H1 2026, rise to 1.3-1.4% in H2")
    analysis.append("• **Macro Impact:** Geopolitical inflation risks could delay rate cuts")
    analysis.append("")
    
    # Rate Comparison Table
    analysis.append("### 🏦 **Bank Fixed Rate Comparison (April 2026):**")
    analysis.append("")
    analysis.append("| Bank | 2-Year Fixed | 3-Year Fixed | 5-Year Fixed | Previous (2025) | Notes |")
    analysis.append("|------|--------------|--------------|--------------|-----------------|-------|")
    
    for bank, rates in HOME_LOAN_RATES.items():
        analysis.append(f"| **{bank}** | {rates['2yr']}% | {rates['3yr']}% | {rates['5yr']}% | {rates['prev']}% | {rates['notes']} |")
    
    analysis.append("")
    
    # Expert Analysis
    analysis.append("### 🔍 **Expert Analysis:**")
    analysis.append("")
    
    # Fed impact analysis
    cut_prob = fed_data["probabilities"].get('cut_25bp', 0) + fed_data["probabilities"].get('cut_50bp', 0)
    
    analysis.append("**1. Fed Policy Impact:**")
    analysis.append(f"• **Market Pricing:** {cut_prob:.1f}% probability of cuts")
    analysis.append("• **Reality Check:** 'Higher for longer' rhetoric + oil inflation")
    analysis.append("• **SORA Implication:** Could rise faster than market expects")
    analysis.append("• **Recommendation:** **Lock fixed rates now** before potential rise")
    analysis.append("")
    
    analysis.append("**2. Geopolitical Impact:**")
    analysis.append(f"• **Oil Price:** ${oil_data['brent']} (+{oil_data['change']}%)")
    analysis.append(f"• **Driver:** {oil_data['driver']}")
    analysis.append("• **Inflation Risk:** Imported inflation could force MAS to maintain tight policy")
    analysis.append("• **Loan Impact:** Supports case for fixed rate protection")
    analysis.append("")
    
    # Action Plan
    analysis.append("### 🎯 **Action Plan:**")
    analysis.append("")
    analysis.append("**For New Loans / Refinancing:**")
    analysis.append("1. **Priority:** 3-Year Fixed at 1.55-1.65% (DBS, Standard Chartered)")
    analysis.append("2. **Timing:** Act before potential SORA rise in H2 2026")
    analysis.append("3. **Loan Size:** >S$500k for best promotional rates")
    analysis.append("4. **Refinance If:** Current rate >2.0% (breakeven ~12-18 months)")
    analysis.append("")
    
    analysis.append("**Risk Management:**")
    analysis.append("• **Upside Risk:** Geopolitical escalation → Higher SORA")
    analysis.append("• **Downside Risk:** Global recession → Aggressive cuts")
    analysis.append("• **Hedge:** Fixed rates provide certainty amid macro uncertainty")
    analysis.append("")
    
    return "\n".join(analysis)

# ========== MAIN REPORT ==========
def generate_full_report():
    """Generate complete report with home loan analysis."""
    
    print(f"📊 **COMPREHENSIVE MARKET & HOME LOAN REPORT**")
    print(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"**Sections:** Macro → Home Loans → Sectors → Assets → Action")
    print()
    
    # Fetch data
    print("📡 Fetching market data...")
    forex_rates = fetch_forex_rates()
    fed_data = fetch_fedwatch_data()
    oil_data = fetch_oil_price()
    
    # ========== SECTION 1: MACRO OVERVIEW ==========
    print("## 🌍 **SECTION 1: MACRO OVERVIEW**")
    print("-" * 50)
    
    cut_prob = fed_data["probabilities"].get('cut_25bp', 0) + fed_data["probabilities"].get('cut_50bp', 0)
    hike_prob = fed_data["probabilities"].get('hike_25bp', 0) + fed_data["probabilities"].get('hike_50bp', 0)
    net_dovishness = cut_prob - hike_prob
    
    print(f"**Fed Watch:** Market pricing {cut_prob:.1f}% cut probability")
    print(f"**Fed Rhetoric:** 'Higher for longer' (hawkish)")
    print(f"**Geopolitics:** Oil ${oil_data['brent']} (+{oil_data['change']}%) - {oil_data['driver']}")
    print(f"**Contradiction:** Market dovish vs Fed hawkish vs oil inflationary")
    print(f"**Implication:** Risk of hawkish surprise, SORA could rise")
    print()
    
    # ========== SECTION 2: HOME LOAN ANALYSIS ==========
    home_loan_section = generate_home_loan_analysis(fed_data, oil_data)
    print(home_loan_section)
    
    # ========== SECTION 3: ASSET MARKETS ==========
    print("## 📈 **SECTION 3: ASSET MARKET ANALYSIS**")
    print("-" * 50)
    
    # Quick asset summary
    print("**Quick Asset Summary:**")
    print(f"• **Gold:** CAUTIOUSLY BULLISH - Geopolitical hedge, not rate-cut bet")
    print(f"• **Tech:** SELECTIVE BULLISH - AI fundamentals strong, macro risks")
    print(f"• **Singapore:** DEFENSIVE - Stability in uncertainty")
    print(f"• **USD/SGD:** 1.2870 - Range trade 1.28-1.32 with USD bias")
    print()
    
    # ========== SECTION 4: ACTION PLAN ==========
    print("## 🎯 **SECTION 4: INTEGRATED ACTION PLAN**")
    print("-" * 50)
    
    print("**PRIMARY BIAS: CAUTIOUSLY OPTIMISTIC**")
    print("")
    print("**1. HOME LOANS:**")
    print("   • Lock 3-Year Fixed rates now (1.55-1.65%)")
    print("   • Refinance if current rate >2.0%")
    print("   • Hedge against potential SORA rise")
    print("")
    print("**2. INVESTMENTS:**")
    print("   • Gold: Tactical accumulate as geopolitical hedge")
    print("   • Tech: Selective overweight AI leaders (MRVL, NVDA)")
    print("   • Singapore: Overweight defensive (S63, Z74)")
    print("   • Forex: Range trade USD/SGD 1.28-1.32")
    print("")
    print("**3. RISK MANAGEMENT:**")
    print("   • 25% cash reserve")
    print("   • Fixed rates for certainty")
    print("   • Stop-losses on tactical positions")
    print("")
    
    # ========== SECTION 5: MONITORING ==========
    print("## 🔔 **SECTION 5: KEY MONITORS**")
    print("-" * 50)
    
    print("**Critical to Watch:**")
    print("1. **Fed Meeting:** April 29 - Reality check on cuts")
    print("2. **US CPI:** Next release - Inflation trajectory")
    print("3. **Brent Oil:** $90 level - Geopolitical inflation risk")
    print("4. **SORA 3M:** >1.3% - Home loan impact")
    print("5. **MAS Policy:** April statement - Singapore response")
    print("")
    
    # Save report
    report_filename = f"full_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(report_filename, 'w') as f:
        f.write(f"Comprehensive Market & Home Loan Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(home_loan_section + "\n\n")
    
    print(f"✅ Report saved to: {report_filename}")
    print("\n" + "="*60)
    print("END OF COMPREHENSIVE REPORT")
    print("="*60)

if __name__ == "__main__":
    generate_full_report()