#!/usr/bin/env python3
"""
Scan daily memory files and extract new content into topic files.
Run this periodically (e.g., via heartbeat) to keep RAG up‑to‑date.
"""

import re
from pathlib import Path
from datetime import datetime, timedelta

MEMORY_DIR = Path(__file__).parent / "memory"
TOPICS_DIR = MEMORY_DIR / "topics"

# Topic mapping: keywords → topic file
TOPIC_RULES = [
    (["stock", "forex", "gold", "fed", "macro", "currency", "sgd", "myr"], "finance.md"),
    (["python", "script", "api", "tool", "setup", "config", "openclaw"], "tech.md"),
    (["project", "decision", "evolution", "report", "monitoring", "system"], "projects.md"),
]

def classify_text(text: str) -> str:
    """Return which topic file this text belongs to."""
    text_lower = text.lower()
    for keywords, topic_file in TOPIC_RULES:
        if any(kw in text_lower for kw in keywords):
            return topic_file
    return "general.md"

def extract_sections(content: str):
    """Extract meaningful sections from a memory file."""
    # Remove metadata header (lines until first ## or blank line after header)
    lines = content.split("\n")
    in_body = False
    body_lines = []
    
    for line in lines:
        if line.startswith("##"):
            in_body = True
        if in_body:
            body_lines.append(line)
    
    body = "\n".join(body_lines)
    if not body.strip():
        body = content  # fallback
    
    # Split by headings
    sections = re.split(r'\n(##+ .+)', body)
    sections = [s.strip() for s in sections if s.strip()]
    return sections

def update_topics():
    """Read recent memory files and update topic files."""
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    memory_files = []
    for f in MEMORY_DIR.glob("*.md"):
        if f.name.startswith("20") and f.name.endswith(".md"):
            # Try to parse date from filename
            try:
                date_str = f.name[:10]  # YYYY-MM-DD
                file_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if file_date >= yesterday:
                    memory_files.append(f)
            except:
                pass
    
    print(f"Found {len(memory_files)} recent memory files.")
    
    updates = {}
    for mf in memory_files:
        content = mf.read_text(encoding="utf-8")
        sections = extract_sections(content)
        for section in sections:
            topic_file = classify_text(section)
            updates.setdefault(topic_file, []).append(section)
    
    for topic_file, sections in updates.items():
        path = TOPICS_DIR / topic_file
        if not path.exists():
            path.write_text("# " + topic_file.replace(".md", "").title() + "\n\n")
        
        existing = path.read_text(encoding="utf-8")
        # Avoid duplicate sections (simple check)
        new_sections = []
        for sec in sections:
            if sec not in existing:
                new_sections.append(sec)
        
        if new_sections:
            with open(path, "a", encoding="utf-8") as f:
                f.write("\n\n## From " + datetime.now().strftime("%Y-%m-%d") + "\n")
                for sec in new_sections:
                    f.write("\n" + sec + "\n")
            print(f"  Added {len(new_sections)} sections to {topic_file}")
    
    if updates:
        print("\nRun `python rag_flat.py --rebuild` to update the index.")
    else:
        print("No new content found.")

if __name__ == "__main__":
    update_topics()