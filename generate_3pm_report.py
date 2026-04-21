#!/usr/bin/env python3
"""
Generate a Bloomberg-style WorldMonitor news update for 3 PM SGT.
"""

import json
from datetime import datetime
from pathlib import Path

def generate_report():
    # Find the latest data file
    data_dir = Path("/home/yeoel/.openclaw/workspace")
    data_files = list(data_dir.glob("bloomberg_data_*.json"))
    if not data_files:
        return "No data files found"
    
    latest_file = max(data_files, key=lambda x: x.stat().st_mtime)
    
    # Load the data
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    # Get current time for the report
    now = datetime.now().strftime("%Y-%m-%d %H:%M SGT")
    
    # Count alert levels
    alert_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    categories = {}
    
    for article in data.get("categorized_articles", []):
        alert_name = article.get("alert_info", {}).get("name", "LOW")
        alert_counts[alert_name] = alert_counts.get(alert_name, 0) + 1
        
        category = article.get("bloomberg_category", "UNCATEGORIZED")
        subcategory = article.get("bloomberg_subcategory", "GENERAL")
        
        if category not in categories:
            categories[category] = {}
        if subcategory not in categories[category]:
            categories[category][subcategory] = []
        
        categories[category][subcategory].append(article)
    
    # Generate the report
    report = []
    report.append("📈 **BLOOMBERG-STYLE NEWS CATEGORIZATION**")
    report.append(f"Time: {now}")
    report.append(f"Articles Analyzed: {data.get('articles_analyzed', 0)}")
    report.append("")
    
    # Alert Summary
    report.append("🚨 **ALERT SUMMARY**")
    report.append("")
    
    if alert_counts["CRITICAL"] > 0:
        report.append("🔴 **CRITICAL ALERTS** ({})".format(alert_counts["CRITICAL"]))
        report.append("   Market-moving event, immediate attention required")
        for article in data.get("categorized_articles", []):
            if article.get("alert_info", {}).get("name") == "CRITICAL":
                report.append("   • {}".format(article["title"]))
                report.append("     [{} → {}]".format(
                    article.get("bloomberg_category", "UNKNOWN"),
                    article.get("bloomberg_subcategory", "GENERAL")
                ))
                report.append("     Source: {}".format(article.get("source", "Unknown")))
        report.append("")
    
    if alert_counts["HIGH"] > 0:
        report.append("🟠 **HIGH ALERTS** ({})".format(alert_counts["HIGH"]))
        report.append("   Significant event, consider action")
        for article in data.get("categorized_articles", []):
            if article.get("alert_info", {}).get("name") == "HIGH":
                report.append("   • {}".format(article["title"]))
                report.append("     [{} → {}]".format(
                    article.get("bloomberg_category", "UNKNOWN"),
                    article.get("bloomberg_subcategory", "GENERAL")
                ))
                report.append("     Source: {}".format(article.get("source", "Unknown")))
        report.append("")
    
    if alert_counts["MEDIUM"] > 0:
        report.append("🟡 **MEDIUM ALERTS** ({})".format(alert_counts["MEDIUM"]))
        report.append("   Notable development, monitor closely")
        for article in data.get("categorized_articles", []):
            if article.get("alert_info", {}).get("name") == "MEDIUM":
                report.append("   • {}".format(article["title"]))
                report.append("     [{} → {}]".format(
                    article.get("bloomberg_category", "UNKNOWN"),
                    article.get("bloomberg_subcategory", "GENERAL")
                ))
                report.append("     Source: {}".format(article.get("source", "Unknown")))
        report.append("")
    
    if alert_counts["LOW"] > 0:
        report.append("🟢 **LOW ALERTS** ({})".format(alert_counts["LOW"]))
        report.append("   Routine update, no immediate action needed")
        for article in data.get("categorized_articles", []):
            if article.get("alert_info", {}).get("name") == "LOW":
                report.append("   • {}".format(article["title"]))
                report.append("     [{} → {}]".format(
                    article.get("bloomberg_category", "UNKNOWN"),
                    article.get("bloomberg_subcategory", "GENERAL")
                ))
                report.append("     Source: {}".format(article.get("source", "Unknown")))
        report.append("")
    
    # Categorized News
    report.append("📊 **CATEGORIZED NEWS**")
    report.append("")
    
    for category, subcats in sorted(categories.items()):
        report.append("**{}** ({})".format(category, sum(len(articles) for articles in subcats.values())))
        for subcategory, articles in sorted(subcats.items()):
            report.append("   └─ {} ({})".format(subcategory, len(articles)))
            for article in articles:
                alert_emoji = article.get("alert_info", {}).get("color", "🟢")
                report.append("      • {} {}".format(alert_emoji, article["title"]))
                report.append("        Source: {}".format(article.get("source", "Unknown")))
                # Truncate summary if too long
                summary = article.get("summary", "")
                if len(summary) > 150:
                    summary = summary[:147] + "..."
                if summary:
                    report.append("        {}".format(summary))
        report.append("")
    
    # Summary Statistics
    report.append("📈 **SUMMARY STATISTICS**")
    report.append("")
    report.append("Total Articles: {}".format(data.get("articles_analyzed", 0)))
    total = data.get("articles_analyzed", 1)
    report.append("🔴 CRITICAL: {} ({:.1%})".format(alert_counts["CRITICAL"], alert_counts["CRITICAL"]/total))
    report.append("🟠 HIGH: {} ({:.1%})".format(alert_counts["HIGH"], alert_counts["HIGH"]/total))
    report.append("🟡 MEDIUM: {} ({:.1%})".format(alert_counts["MEDIUM"], alert_counts["MEDIUM"]/total))
    report.append("🟢 LOW: {} ({:.1%})".format(alert_counts["LOW"], alert_counts["LOW"]/total))
    report.append("")
    
    # Footer
    report.append("---")
    report.append("📰 **Source:** WorldMonitor News Aggregator")
    report.append("🎯 **Categorization:** Bloomberg-style with alert levels")
    report.append("⏰ **Next Update:** Every 6 hours (9 AM, 3 PM, 9 PM, 3 AM SGT)")
    report.append("")
    
    # Article Links
    report.append("🔗 **ALL ARTICLE LINKS:**")
    report.append("")
    for i, article in enumerate(data.get("categorized_articles", []), 1):
        alert_emoji = article.get("alert_info", {}).get("color", "🟢")
        report.append("{}. {} {}".format(i, alert_emoji, article["title"]))
        report.append("   {}".format(article["link"]))
    
    return "\n".join(report)

if __name__ == "__main__":
    report = generate_report()
    print(report)
    
    # Also save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = f"/home/yeoel/.openclaw/workspace/bloomberg_report_3pm_{timestamp}.txt"
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"\nReport saved to: {output_file}")