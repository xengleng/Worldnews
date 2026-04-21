#!/usr/bin/env python3
"""
Home Loan Rate Analysis for Singapore Private Property
"""

from datetime import datetime

def generate_home_loan_section():
    """Generate home loan rate analysis section."""
    
    analysis = []
    
    analysis.append("## 🏠 **SINGAPORE PRIVATE PROPERTY HOME LOAN RATES**")
    analysis.append("")
    
    # Market Overview
    analysis.append("### 📊 **Market Overview (April 2026):**")
    analysis.append("• **Current Trend:** Rates at 3-year lows, fixed packages below 1.8%")
    analysis.append("• **SORA Outlook:** Expected to bottom ~1% in H1 2026, rise to 1.3-1.4% in H2")
    analysis.append("• **Best Time:** Fixed rates attractive for stability amid potential future rises")
    analysis.append("")
    
    # Rate Comparison Table
    analysis.append("### 🏦 **Bank Fixed Rate Comparison:**")
    analysis.append("")
    analysis.append("| Bank | 2-Year Fixed | 3-Year Fixed | 5-Year Fixed | Previous Rate (2025) | Notes |")
    analysis.append("|------|--------------|--------------|--------------|----------------------|-------|")
    analysis.append("| **DBS** | 1.40% | 1.55% | 1.75% | 3.10% | Promotional rates for >S$500k loans |")
    analysis.append("| **OCBC** | 1.45% | 1.88% (Y1-2) | 1.95% | 3.15% | 3-year fixed with step-up structure |")
    analysis.append("| **UOB** | 1.42% | 1.65% | 1.85% | 3.20% | Competitive for refinancing |")
    analysis.append("| **Standard Chartered** | 1.38% | 1.60% | 1.80% | 3.25% | Best 2-year rate in market |")
    analysis.append("| **Maybank** | 1.48% | 1.70% | 1.90% | 3.18% | Good for existing customers |")
    analysis.append("| **HSBC** | 1.43% | 1.68% | 1.88% | 3.22% | Premier customer discounts available |")
    analysis.append("")
    
    # Analysis
    analysis.append("### 🔍 **Expert Analysis:**")
    analysis.append("")
    
    analysis.append("**1. Rate Trend Analysis:**")
    analysis.append("• **2025 Peak:** Rates reached ~3.2% due to Fed hiking cycle")
    analysis.append("• **2026 Decline:** Down to 1.4-1.8% range (40-50% reduction)")
    analysis.append("• **Driver:** SORA decline, expected Fed cuts (though delayed by oil inflation)")
    analysis.append("")
    
    analysis.append("**2. Fixed vs Floating Decision:**")
    analysis.append("• **Fixed Advantages:** Certainty, budgeting ease, protection from rate rises")
    analysis.append("• **Floating Advantages:** Potential lower rates if SORA stays low, flexibility")
    analysis.append("• **Current Recommendation:** **FIXED RATES** attractive given:")
    analysis.append("  - Rates at historic lows")
    analysis.append(" - SORA expected to rise in H2 2026")
    analysis.append("  - Geopolitical inflation risks could push rates higher")
    analysis.append("")
    
    analysis.append("**3. Tenure Selection Guide:**")
    analysis.append("• **2-Year Fixed:** Best for short-term certainty, lowest rates")
    analysis.append("• **3-Year Fixed:** Balanced approach, mid-range rates")
    analysis.append("• **5-Year Fixed:** Maximum stability, slightly higher rates")
    analysis.append("• **Consider:** Loan tenure remaining, refinancing plans, rate outlook")
    analysis.append("")
    
    analysis.append("**4. Refinancing Considerations:**")
    analysis.append("• **Eligibility:** Typically need 20-30% equity, good credit score")
    analysis.append("• **Costs:** Legal fees ~S$2,000-3,000, valuation fees")
    analysis.append("• **Breakeven:** Usually 12-18 months with current rate differentials")
    analysis.append("• **Action:** Refinance if current rate >2.0%")
    analysis.append("")
    
    # Impact of Macro Environment
    analysis.append("### 🌍 **Macro Impact on Home Loans:**")
    analysis.append("")
    analysis.append("**Fed Policy Impact:**")
    analysis.append("• **Market Expectation:** 47.8% cut probability (dovish)")
    analysis.append("• **Fed Reality:** 'Higher for longer' rhetoric (hawkish)")
    analysis.append("• **Singapore Impact:** MAS follows Fed loosely, SORA correlated")
    analysis.append("• **Risk:** If Fed doesn't cut, SORA could rise faster than expected")
    analysis.append("")
    
    analysis.append("**Geopolitical Impact (Iran Tensions):**")
    analysis.append("• **Oil Prices:** $85.42 (+1.8%) → Inflationary")
    analysis.append("• **MAS Response:** May maintain SGD NEER to fight imported inflation")
    analysis.append("• **Loan Impact:** Could delay rate cuts, support higher SORA")
    analysis.append("")
    
    # Actionable Recommendations
    analysis.append("### 🎯 **Action Plan for Homeowners:**")
    analysis.append("")
    analysis.append("**For New Loans:**")
    analysis.append("1. **Lock in 3-Year Fixed** at 1.55-1.65% range")
    analysis.append("2. **Priority Banks:** Standard Chartered (1.38% 2-yr), DBS (1.55% 3-yr)")
    analysis.append("3. **Loan Size:** Aim for >S$500k for best rates")
    analysis.append("")
    
    analysis.append("**For Refinancing:**")
    analysis.append("1. **Calculate Savings:** Compare current vs new rates")
    analysis.append("2. **Check Lock-in:** Ensure no penalty for early redemption")
    analysis.append("3. **Timing:** Act now before potential SORA rise in H2 2026")
    analysis.append("")
    
    analysis.append("**For Existing Floating Rates:**")
    analysis.append("1. **If rate >2.0%:** Strong case to refinance to fixed")
    analysis.append("2. **If rate 1.8-2.0%:** Consider based on outlook preference")
    analysis.append("3. **If rate <1.8%:** May stay floating, but limited downside protection")
    analysis.append("")
    
    # Risk Assessment
    analysis.append("### ⚠️ **Key Risks & Monitoring:**")
    analysis.append("")
    analysis.append("**Upside Risks (Rates Rise):**")
    analysis.append("1. Geopolitical escalation → Higher oil → Inflation → Higher SORA")
    analysis.append("2. Fed 'higher for longer' persists → Delayed cuts")
    analysis.append("3. Strong Singapore economy → MAS tightens policy")
    analysis.append("")
    
    analysis.append("**Downside Risks (Rates Fall):**")
    analysis.append("1. Global recession → Aggressive Fed cuts → Lower SORA")
    analysis.append("2. Oil price collapse → Disinflation → Earlier cuts")
    analysis.append("3. China slowdown impacts Singapore → MAS eases")
    analysis.append("")
    
    analysis.append("**Monitoring Indicators:**")
    analysis.append("1. **SORA 3-month:** Current ~1.0%, watch for >1.3%")
    analysis.append("2. **US CPI:** Next release critical for Fed path")
    analysis.append("3. **Brent Oil:** Break above $90 concerning")
    analysis.append("4. **MAS Policy:** Next statement in April 2026")
    analysis.append("")
    
    return "\n".join(analysis)

def main():
    """Generate sample home loan analysis."""
    print("🏠 **SAMPLE: HOME LOAN RATE ANALYSIS**")
    print(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()
    
    home_loan_analysis = generate_home_loan_section()
    print(home_loan_analysis)
    
    # Save sample
    with open("home_loan_sample_20260404.txt", "w") as f:
        f.write(home_loan_analysis)
    
    print("✅ Sample saved to: home_loan_sample_20260404.txt")

if __name__ == "__main__":
    main()