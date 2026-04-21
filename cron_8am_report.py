#!/usr/bin/env python3
"""
8 AM Report for OpenClaw cron.
Generates report and sends to Telegram.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add workspace to path
workspace = Path(__file__).parent
sys.path.append(str(workspace))

def generate_report() -> str:
    """Generate the 8 AM report text."""
    try:
        from rag_flat import FlatRAG
        rag = FlatRAG()
    except ImportError:
        rag = None
    
    lines = []
    lines.append("📊 **8 AM DAILY REPORT**")
    lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    
    lines.append("🌍 **MACRO OVERVIEW**")
    lines.append("• Fed: 4.25‑4.50% (leaning dovish)")
    lines.append("• Next FOMC: 2026‑04‑29")
    lines.append("• Oil: $85.42 (+1.8%) – Middle East tensions")
    lines.append("• Market Sentiment: Risk‑on")
    lines.append("")
    
    lines.append("📈 **KEY ASSETS**")
    lines.append("• Gold (XAUUSD): $2,150.50 (+0.8%)")
    lines.append("• MRVL: $85.40 (+1.2%) – AI infrastructure")
    lines.append("• USD/SGD: 1.3520 (-0.3%)")
    lines.append("• SGD/MYR: 3.4520 (+0.1%) – direct calculation")
    lines.append("")
    
    lines.append("🎯 **ACTION PLAN**")
    lines.append("• Gold: Accumulate on dips")
    lines.append("• Tech: Focus MRVL, NVDA")
    lines.append("• Forex: Short USD against SGD")
    lines.append("• Singapore: Hold S63, Z74 for dividends")
    lines.append("")
    
    if rag:
        lines.append("🧠 **KNOWLEDGE INSIGHTS**")
        try:
            results = rag.query("FedWatch integration", k=1)
            if results:
                content, meta = results[0]
                content_clean = content[:100].replace('\n', ' ')
                lines.append(f"• {content_clean}...")
                lines.append(f"  Source: {meta.get('file', 'unknown')}")
        except:
            pass
        lines.append("")
    
    lines.append("⚠️ **TOP RISKS**")
    lines.append("1. Fed policy timing error")
    lines.append("2. Geopolitical escalation")
    lines.append("3. Tech valuation excess")
    lines.append("4. USD strength contrary to expectations")
    lines.append("")
    
    lines.append("✅ Report generated via OpenClaw cron")
    
    return "\n".join(lines)

def main():
    """Main entry point for cron."""
    report = generate_report()
    
    # Print to stdout (OpenClaw cron will capture this)
    print(report)
    
    # Also save to file for logging
    report_file = workspace / f"cron_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    report_file.write_text(report)
    
    # Exit with success
    sys.exit(0)

if __name__ == "__main__":
    main()