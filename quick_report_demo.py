#!/usr/bin/env python3
"""
Quick demo of the 8 AM report with RAG integration.
Shows structure without fetching live data.
"""

from datetime import datetime
import sys
sys.path.append('.')

def get_rag_insights(topic: str) -> str:
    """Mock RAG insights for demo."""
    insights = {
        "Fed monetary policy macro outlook": """
**📚 Knowledge Base Insights:**
1. - Fed expectations monitoring
- Monetary policy analysis
- Macro-driven report structure
   *Source: finance.md › ## Macro & FedWatch*

2. - **Fed Sentiment:** STRONGLY DOVISH (+47.8% net dovishness)
- **Oil:** $85.42 (+1.8%) driven by Middle East tensions
- **Primary Bias:** RISK-ON
   *Source: finance.md › ### **Current Macro Assessment:***
""",
        "gold sector stocks forex": """
**📚 Knowledge Base Insights:**
1. - Gold monitoring uses XAUUSD symbol (spot gold in USD)
- GLD is SPDR Gold Shares ETF (popular gold ETF)
- Singapore stocks use .SI suffix for Singapore Exchange
   *Source: finance.md › ### **Notes:***
""",
        "investment action plan strategy": """
**📚 Knowledge Base Insights:**
1. 1. **GOLD (XAUUSD, GLD):** STRONG BUY - Target $2,300-2,400/oz
2. **USD/SGD:** BEARISH USD - Target 1.25-1.28 range
3. **TECH STOCKS:** VERY BULLISH - Focus MRVL (AI infrastructure)
   *Source: finance.md › ### **Expert Recommendations (Based on +40.8% Net Dovishness):***
"""
    }
    return insights.get(topic, "")

print(f"📊 **MACRO-DRIVEN MARKET REPORT (with Knowledge Base)**")
print(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"**Analysis Framework:** Macro → Sector → Assets → Action → Knowledge")
print()

print("## 🌍 **MACRO OVERVIEW**")
print("-" * 50)
print("**Monetary Policy (Fed):** 4.25-4.50%")
print("**Next FOMC:** 2026-04-29")
print("**Market Sentiment:** Leaning Dovish")
print("**Net Dovishness:** +13.7%")
print("**Oil (Brent):** $85.42 (+1.8%)")
print("**Driver:** Geopolitical tensions in Middle East")
print("**Trend:** Bullish")
print()

print(get_rag_insights("Fed monetary policy macro outlook"))
print()

print("## 📈 **SECTOR-BY-SECTOR ANALYSIS**")
print("-" * 50)
print()

print("**GOLD Sector:**")
print("**Outlook:** Neutral")
print(get_rag_insights("gold sector stocks forex"))
print("  • **Gold Spot (XAUUSD):** $2,150.50 (+0.8%)")
print("  • **SPDR Gold ETF (GLD):** $201.25 (+0.7%)")
print("    📰 Gold Holds Gains as Fed Dovishness Supports")
print()

print("**TECH Sector:**")
print("**Outlook:** Selective (focus on quality)")
print("  • **Marvell Tech (MRVL):** $85.40 (+1.2%)")
print("  • **NVIDIA (NVDA):** $950.75 (+0.9%)")
print("    📰 AI Chip Demand Continues to Drive Tech")
print()

print("**FOREX Sector:**")
print("**Outlook:** USD weakness expected")
print("  • **USD/SGD:** 1.3520 (-0.3%)")
print("  • **SGD/MYR:** 3.4520 (+0.1%)")
print("    📰 Asian Currencies Strengthen on Fed Outlook")
print()

print("## 🎯 **ACTION PLAN**")
print("-" * 50)
print("**Strategy:** Cautiously optimistic")
print("• **Gold:** Hold existing positions")
print("• **Tech:** Selective buying (MRVL, NVDA)")
print("• **Forex:** Range‑trade USD pairs")
print("• **Singapore Stocks:** Accumulate slowly")
print()

print(get_rag_insights("investment action plan strategy"))
print()

print("## 🧠 **KNOWLEDGE BASE SUMMARY**")
print("-" * 50)
print("**Relevant insights from your knowledge base:**")
print()
print("**FedWatch Integration:**")
print("  • Monitoring Fed expectations with expert analysis")
print("  • Integrated into daily reports with 5 sections")
print()
print("**Forex Monitoring:**")
print("  • USD/SGD, SGD/JPY, SGD/CNY, SGD/MYR pairs")
print("  • Direct SGD/MYR calculation implemented")
print()
print("**Gold Price Tracking:**")
print("  • XAUUSD (spot gold) and GLD ETF")
print("  • Part of comprehensive asset monitoring")
print()

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
print("• Use stop‑losses on tactical positions")
print("• Hedge USD exposure if heavily positioned")
print()

print("=" * 60)
print("END OF MACRO‑DRIVEN REPORT WITH KNOWLEDGE BASE")
print("=" * 60)
print()
print("💡 **Note:** Full report would include:")
print("• Live data from APIs (Yahoo Finance, ExchangeRate‑API)")
print("• Real‑time news from RSS feeds")
print("• Actual RAG queries (not mocked)")
print("• Saved to file with timestamp")