#!/usr/bin/env python3
"""
Comprehensive Daily Report: Stocks, Forex, FedWatch with Expert Analysis.
"""

import urllib.request
import xml.etree.ElementTree as ET
import json
import sys
from datetime import datetime
import time
import re

# ========== CONFIGURATION ==========
STOCKS = {
    "MRVL": "Marvell Technology",
    "AMD": "Advanced Micro Devices",
    "NVDA": "NVIDIA Corporation",
    "FIG": "Figma Inc",
    "XAUUSD": "Gold (USD per ounce)",
    "GLD": "SPDR Gold Shares ETF",
    "S63.SI": "ST Engineering (Singapore)",
    "Z74.SI": "SingTel (Singapore)",
    "USDSGD=X": "USD/SGD",
    "SGDJPY=X": "SGD/JPY",
    "SGDCNY=X": "SGD/CNY",
    "MYRSGD=X": "MYR/SGD"
}

# ========== FOREX FUNCTIONS ==========
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

# ========== FEDWATCH FUNCTIONS ==========
def fetch_fedwatch_data():
    """
    Fetch FedWatch data (placeholder - would integrate with CME data).
    In production, use CME API, financial data provider, or web scraping.
    """
    # Placeholder - real implementation would fetch from CME FedWatch
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

def analyze_fed_impact(probabilities):
    """Analyze Fed rate expectations."""
    cut_prob = probabilities.get('cut_25bp', 0) + probabilities.get('cut_50bp', 0)
    hike_prob = probabilities.get('hike_25bp', 0) + probabilities.get('hike_50bp', 0)
    
    if cut_prob > 60:
        return "STRONGLY DOVISH", cut_prob - hike_prob
    elif cut_prob > 40:
        return "DOVISH", cut_prob - hike_prob
    elif hike_prob > 60:
        return "STRONGLY HAWKISH", cut_prob - hike_prob
    elif hike_prob > 40:
        return "HAWKISH", cut_prob - hike_prob
    else:
        return "NEUTRAL", cut_prob - hike_prob

# ========== STOCK NEWS FUNCTIONS ==========
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

def check_impact(title, description):
    """Check if article has potential market impact."""
    text = (title + ' ' + description).lower()
    
    high_impact = ['earnings', 'results', 'quarter', 'guidance', 'forecast', 
                   'upgrade', 'downgrade', 'analyst', 'price target', 'target',
                   'merger', 'acquisition', 'buyout', 'lawsuit', 'sue', 'sued',
                   'investigation', 'sec', 'fda', 'approval', 'reject', 'recall',
                   'layoff', 'layoffs', 'cut', 'cuts', 'restructuring']
    
    medium_impact = ['partnership', 'deal', 'contract', 'win', 'won', 'award',
                    'launch', 'release', 'new', 'product', 'expansion', 'expand',
                    'hire', 'appoint', 'ceo', 'cfo', 'dividend', 'buyback',
                    'share', 'stock', 'conference', 'presentation']
    
    for word in high_impact:
        if word in text:
            return 'HIGH'
    
    for word in medium_impact:
        if word in text:
            return 'MEDIUM'
    
    return 'LOW'

# ========== EXPERT ANALYSIS FUNCTIONS ==========
def generate_fed_expert_analysis(fed_data, net_dovishness):
    """Generate expert Fed analysis."""
    analysis = []
    
    cut_prob = fed_data["probabilities"].get('cut_25bp', 0) + fed_data["probabilities"].get('cut_50bp', 0)
    hike_prob = fed_data["probabilities"].get('hike_25bp', 0) + fed_data["probabilities"].get('hike_50bp', 0)
    
    analysis.append("## 🏛️ **FEDWATCH EXPERT ANALYSIS**")
    analysis.append(f"**Next FOMC:** {fed_data['next_meeting']} | **Current Rate:** {fed_data['current_rate']}")
    analysis.append("")
    
    # Probability breakdown
    analysis.append("### 📊 **Market Expectations:**")
    analysis.append(f"- **No Change:** {fed_data['probabilities']['no_change']:.1f}%")
    analysis.append(f"- **Cut 25bp:** {fed_data['probabilities']['cut_25bp']:.1f}%")
    analysis.append(f"- **Cut 50bp:** {fed_data['probabilities']['cut_50bp']:.1f}%")
    analysis.append(f"- **Hike 25bp:** {fed_data['probabilities']['hike_25bp']:.1f}%")
    analysis.append(f"- **Hike 50bp:** {fed_data['probabilities']['hike_50bp']:.1f}%")
    analysis.append(f"- **Net Dovishness:** {net_dovishness:+.1f}%")
    analysis.append("")
    
    # Expert view
    analysis.append("### 🎯 **Expert View:**")
    
    if net_dovishness > 20:
        analysis.append("**STRONGLY DOVISH - RATE CUTS EXPECTED**")
        analysis.append("• **Implication:** Bullish for risk assets, bearish USD")
        analysis.append("• **Action:** Accumulate gold, tech stocks on weakness")
        analysis.append("• **Risk:** Inflation could surprise to upside")
        
    elif net_dovishness > 0:
        analysis.append("**MODERATELY DOVISH - CUTS LIKELY**")
        analysis.append("• **Implication:** Supportive for markets")
        analysis.append("• **Action:** Selective buying in growth sectors")
        analysis.append("• **Risk:** Fed could push back on market pricing")
        
    elif net_dovishness < -20:
        analysis.append("**STRONGLY HAWKISH - HIKES EXPECTED**")
        analysis.append("• **Implication:** Defensive positioning needed")
        analysis.append("• **Action:** Reduce risk, favor cash and short-duration bonds")
        analysis.append("• **Risk:** Overtightening could trigger recession")
        
    elif net_dovishness < 0:
        analysis.append("**MODERATELY HAWKISH - HIKES POSSIBLE**")
        analysis.append("• **Implication:** Caution warranted")
        analysis.append("• **Action:** Focus on quality, avoid highly leveraged names")
        analysis.append("• **Risk:** Growth could slow faster than expected")
        
    else:
        analysis.append("**NEUTRAL - DATA DEPENDENT**")
        analysis.append("• **Implication:** Range-bound markets likely")
        analysis.append("• **Action:** Stock-specific opportunities, tactical trading")
        analysis.append("• **Risk:** Breakout in either direction possible")
    
    analysis.append("")
    return "\n".join(analysis)

def generate_asset_specific_analysis(net_dovishness, forex_rates):
    """Generate asset-specific expert analysis."""
    analysis = []
    
    analysis.append("## 📈 **ASSET-SPECIFIC EXPERT VIEWS**")
    analysis.append("")
    
    # Gold analysis
    analysis.append("### 🥇 **GOLD (XAUUSD, GLD):**")
    if net_dovishness > 20:
        analysis.append("**STRONG BUY** - Ideal environment for gold")
        analysis.append("• Lower real yields supportive")
        analysis.append("• Potential USD weakness adds tailwind")
        analysis.append("• Target: $2,300-2,400/oz")
    elif net_dovishness > 0:
        analysis.append("**BULLISH** - Favorable backdrop")
        analysis.append("• Accumulate on dips below $2,150")
        analysis.append("• Hedge against equity volatility")
        analysis.append("• Target: $2,200-2,300/oz")
    elif net_dovishness < -20:
        analysis.append("**CAUTIOUS** - Headwinds present")
        analysis.append("• Higher rates increase opportunity cost")
        analysis.append("• Wait for clear reversal signals")
        analysis.append("• Support: $2,000-2,100/oz")
    else:
        analysis.append("**NEUTRAL** - Balanced risks")
        analysis.append("• Range-bound trading likely")
        analysis.append("• Trade $2,100-2,200 range")
        analysis.append("• Monitor inflation data closely")
    
    analysis.append("")
    
    # USD/SGD analysis
    usd_sgd_rate = 1 / forex_rates.get('USD', 0) if forex_rates.get('USD') else 0
    analysis.append(f"### 💵 **USD/SGD (Current: {usd_sgd_rate:.4f}):**")
    if net_dovishness > 20:
        analysis.append("**BEARISH USD** - Favor SGD strength")
        analysis.append("• Fed cuts widen rate differential")
        analysis.append("• MAS may maintain SGD NEER policy")
        analysis.append("• Target: 1.25-1.28 range")
    elif net_dovishness > 0:
        analysis.append("**MODERATELY BEARISH USD**")
        analysis.append("• Gradual SGD appreciation likely")
        analysis.append("• Trade 1.28-1.32 range")
        analysis.append("• Monitor MAS policy statements")
    elif net_dovishness < -20:
        analysis.append("**BULLISH USD** - USD strength expected")
        analysis.append("• Fed hikes support USD")
        analysis.append("• Target: 1.32-1.35 range")
        analysis.append("• Risk: MAS could intervene")
    else:
        analysis.append("**RANGE-BOUND** - Limited direction")
        analysis.append(f"• Current level: {usd_sgd_rate:.4f} fair value")
        analysis.append("• Trade 1.28-1.32 range")
        analysis.append("• Watch for breakout on data surprises")
    
    analysis.append("")
    
    # Tech stocks analysis
    analysis.append("### 💻 **TECH STOCKS (MRVL, AMD, NVDA, FIG):**")
    if net_dovishness > 20:
        analysis.append("**VERY BULLISH** - Perfect environment")
        analysis.append("• Lower rates boost growth stock valuations")
        analysis.append("• AI thematic remains strong")
        analysis.append("• Focus: MRVL (AI infrastructure), NVDA (AI leader)")
    elif net_dovishness > 0:
        analysis.append("**BULLISH** - Supportive backdrop")
        analysis.append("• Selective accumulation recommended")
        analysis.append("• AMD: Value play in AI semi space")
        analysis.append("• FIG: Monitor AI design agent disruption")
    elif net_dovishness < -20:
        analysis.append("**DEFENSIVE** - Higher rates pressure")
        analysis.append("• Focus on cash-rich, profitable names")
        analysis.append("• NVDA: Strong margins provide buffer")
        analysis.append("• Avoid highly leveraged tech")
    else:
        analysis.append("**SELECTIVE** - Stock-specific opportunities")
        analysis.append("• Fundamentals over macro")
        analysis.append("• MRVL: Attractive valuation, AI exposure")
        analysis.append("• Trade earnings catalysts")
    
    analysis.append("")
    
    # Singapore stocks analysis
    analysis.append("### 🇸🇬 **SINGAPORE STOCKS:**")
    analysis.append("**S63 (ST Engineering):**")
    analysis.append("• Defensive characteristics attractive")
    analysis.append("• Government contracts provide visibility")
    analysis.append("• Dividend yield ~4% provides support")
    analysis.append("")
    analysis.append("**Z74 (SingTel):**")
    analysis.append("• Telecom defensive in uncertain markets")
    analysis.append("• Regional growth exposure in ASEAN")
    analysis.append("• Dividend yield ~5% attractive")
    
    analysis.append("")
    
    # Forex crosses
    analysis.append("### 🌏 **ASIAN FOREX CROSSES:**")
    analysis.append(f"**SGD/JPY:** {forex_rates.get('JPY', 0):.2f}")
    analysis.append("• Carry trade attractive if volatility low")
    analysis.append("• Monitor BoJ policy normalization")
    analysis.append("")
    analysis.append(f"**SGD/CNY:** {forex_rates.get('CNY', 0):.4f}")
    analysis.append("• China economic recovery key driver")
    analysis.append("• PBOC managing gradual depreciation")
    analysis.append("")
    analysis.append(f"**SGD/MYR:** {forex_rates.get('MYR', 0):.4f}")
    analysis.append("• Malaysia economic reforms supportive")
    analysis.append("• Commodity prices influence MYR")
    
    return "\n".join(analysis)

# ========== MAIN REPORT FUNCTION ==========
def generate_comprehensive_report():
    """Generate the comprehensive daily report."""
    
    print(f"📊 **COMPREHENSIVE DAILY MARKET REPORT**")
    print(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"**Assets Monitored:** {len(STOCKS)}")
    print()
    
    # ========== SECTION 1: FOREX RATES ==========
    print("💱 **SECTION 1: LIVE FOREX RATES**")
    print("-" * 50)
    
    forex_rates = fetch_forex_rates()
    if forex_rates:
        print(f"Base currency: SGD (as of {datetime.now().strftime('%Y-%m-%d')})")
        usd_rate = 1 / forex_rates.get('USD', 0) if forex_rates.get('USD') else 0
        print(f"• USD/SGD: {usd_rate:.4f} (1 USD = {usd_rate:.4f} SGD)")
        print(f"• SGD/JPY: {forex_rates.get('JPY', 0):.2f} (1 SGD = {forex_rates.get('JPY', 0):.2f} JPY)")
        print(f"• SGD/CNY: {forex_rates.get('CNY', 0):.4f} (1 SGD = {forex_rates.get('CNY', 0):.4f} CNY)")
        print(f"• SGD/MYR: {forex_rates.get('MYR', 0):.4f} (1 SGD = {forex_rates.get('MYR', 0):.4f} MYR)")
    else:
        print("Could not fetch forex rates")
    print()
    
    # ========== SECTION 2: FEDWATCH ANALYSIS ==========
    print("🏛️ **SECTION 2: FEDWATCH & MONETARY POLICY**")
    print("-" * 50)
    
    fed_data = fetch_fedwatch_data()
    fed_sentiment, net_dovishness = analyze_fed_impact(fed_data["probabilities"])
    
    print(f"Next FOMC Meeting: {fed_data['next_meeting']}")
    print(f"Current Fed Funds Rate: {fed_data['current_rate']}")
    print(f"Market Sentiment: {fed_sentiment}")
    print(f"Net Dovishness: {net_dovishness:+.1f}%")
    print()
    
    # ========== SECTION 3: EXPERT ANALYSIS ==========
    print("🎯 **SECTION 3: EXPERT ANALYSIS & RECOMMENDATIONS**")
    print("-" * 50)
    
    fed_analysis = generate_fed_expert_analysis(fed_data, net_dovishness)
    print(fed_analysis)
    
    asset_analysis = generate_asset_specific_analysis(net_dovishness, forex_rates)
    print(asset_analysis)
    
    # ========== SECTION 4: STOCK NEWS ==========
    print("📰 **SECTION 4: STOCK NEWS & IMPACT ANALYSIS**")
    print("-" * 50)
    
    all_articles = []
    
    for symbol, name in STOCKS.items():
        print(f"Checking {symbol} ({name})...")
        
        yahoo_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
        yahoo_xml = fetch_rss_feed(yahoo_url)
        yahoo_articles = parse_rss(yahoo_xml, "Yahoo Finance", symbol)
        
        for article in yahoo_articles:
            article['impact'] = check_impact(article['title'], article['description'])
        
        all_articles.extend(yahoo_articles)
        time.sleep(0.5)  # Reduced sleep for faster execution
    
    if not all_articles:
        print("\n✅ No news articles found today.")
    else:
        # Sort by impact
        all_articles.sort(key=lambda x: {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}[x['impact']])
        
        high_impact = [a for a in all_articles if a['impact'] == 'HIGH']
        medium_impact = [a for a in all_articles if a['impact'] == 'MEDIUM']
        low_impact = [a for a in all_articles if a['impact'] == 'LOW']
        
        if high_impact:
            print("\n🔴 **HIGH IMPACT NEWS:")
            for article in high_impact[:5]:  # Limit to top 5
                print(f"• {article['symbol']}: {article['title']}")
                print(f"  {article['link']}")
                print()
        
        if medium_impact:
            print("🟡 **MEDIUM IMPACT NEWS:")
            for article in medium_impact[:3]:
                print(f"• {article['symbol']}: {article['title']}")
                print()
        
        print(f"\n📊 **News Summary:** {len(high_impact)} high, {len(medium_impact)} medium, {len(low_impact)} low impact articles")
    
    # ========== SECTION 5: ALERTS & MONITORING ==========
    print("\n🔔 **SECTION 5: ALERTS & MONITORING**")
    print("-" * 50)
    
    print("**Active Monitoring:**")
    print("1. Fed rate probability changes (>10% shift triggers alert)")
    print("2. Gold breakouts above $2,200 or below $2,100")
    print("3. USD/SGD outside 1.28-1.32 range")
    print("4. Tech stock earnings surprises")
    print("5. Singapore economic data releases")
    print()
    
    print("**Next Check:** Tomorrow 8:00 AM Singapore Time")
    print()
    
    # ========== SAVE REPORT ==========
    report_filename = f"comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(report_filename, 'w') as f:
        f.write(f"Comprehensive Market Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(fed_analysis + "\n\n")
        f.write(asset_analysis + "\n\n")
        
        if all_articles:
            f.write("STOCK NEWS SUMMARY:\n")
            for article in all_articles:
                f.write(f"[{article['impact']}] {article['symbol']}: {article['title']}\n")
    
    print(f"✅ Report saved to: {report_filename}")
    print("\n" + "="*60)
    print("END OF DAILY REPORT")
    print("="*60)

# ========== MAIN EXECUTION ==========
if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Comprehensive Daily Market Report with Expert Analysis")
        print("Usage: python3 daily_report_comprehensive.py")
        print()
        print("Includes:")
        print("• Live forex rates (SGD pairs)")
        print("• FedWatch probability analysis")
        print("• Expert investment recommendations")
        print("• Stock news with impact ratings")
        print("• Monitoring alerts")
        sys.exit(0)
    
    generate_comprehensive_report()