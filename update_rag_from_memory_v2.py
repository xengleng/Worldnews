#!/usr/bin/env python3
"""
Scan daily memory files and extract new content into topic files.
Improved extraction to skip metadata and short sections.
"""

import re
from pathlib import Path
from datetime import datetime, timedelta

MEMORY_DIR = Path(__file__).parent / "memory"
TOPICS_DIR = MEMORY_DIR / "topics"

# Topic mapping: keywords → topic file
TOPIC_RULES = [
    (["stock", "forex", "gold", "fed", "macro", "currency", "sgd", "myr", "loan", "mortgage", "rate"], "finance.md"),
    (["python", "script", "api", "tool", "setup", "config", "openclaw", "rag", "faiss", "embedding"], "tech.md"),
    (["project", "decision", "evolution", "report", "monitoring", "system", "structure", "summary"], "projects.md"),
]

def classify_text(text: str) -> str:
    """Return which topic file this text belongs to."""
    text_lower = text.lower()
    for keywords, topic_file in TOPIC_RULES:
        if any(kw in text_lower for kw in keywords):
            return topic_file
    return None  # Skip if no match

def extract_sections(content: str):
    """Extract meaningful sections from a memory file."""
    # Skip metadata header (lines before first meaningful heading)
    lines = content.split("\n")
    start = 0
    for i, line in enumerate(lines):
        if line.startswith("## Conversation") or line.startswith("## ✅") or \
           (line.startswith("##") and not line.startswith("## Session:")):
            start = i
            break
    
    body = "\n".join(lines[start:])
    if not body.strip():
        return []
    
    # Split by headings, keep heading with its content
    parts = re.split(r'(\n##+ .+)', body)
    sections = []
    current = ""
    for part in parts:
        if part.startswith("\n##"):
            if current.strip():
                sections.append(current.strip())
            current = part.strip()
        else:
            current += "\n" + part.strip()
    if current.strip():
        sections.append(current.strip())
    
    # Filter out very short or generic sections
    filtered = []
    for sec in sections:
        lines = sec.split("\n")
        if len(lines) >= 2 and len(sec) > 150:
            filtered.append(sec)
    return filtered

def update_topics():
    """Read recent memory files and update topic files."""
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    memory_files = []
    for f in MEMORY_DIR.glob("*.md"):
        if f.name.startswith("20") and f.name.endswith(".md"):
            try:
                date_str = f.name[:10]
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
            if topic_file:
                updates.setdefault(topic_file, []).append(section)
    
    for topic_file, sections in updates.items():
        path = TOPICS_DIR / topic_file
        if not path.exists():
            path.write_text("# " + topic_file.replace(".md", "").title() + "\n\n")
        
        existing = path.read_text(encoding="utf-8")
        # Avoid duplicate sections (simple check)
        new_sections = []
        for sec in sections:
            # Check if similar content already exists (by first 50 chars)
            first_lines = "\n".join(sec.split("\n")[:3])
            if first_lines not in existing:
                new_sections.append(sec)
        
        if new_sections:
            with open(path, "a", encoding="utf-8") as f:
                f.write("\n\n## From " + mf.name[:10] + "\n")
                for sec in new_sections:
                    f.write("\n" + sec + "\n")
            print(f"  Added {len(new_sections)} sections to {topic_file}")
    
    if updates:
        print("\nRun `python rag_flat.py --rebuild` to update the index.")
    else:
        print("No new content found.")

if __name__ == "__main__":
    update_topics()