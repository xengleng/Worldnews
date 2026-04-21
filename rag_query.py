#!/usr/bin/env python3
"""
RAG query module for integration into other scripts.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from rag_flat import FlatRAG
except ImportError:
    # Fallback: run rag_flat.py as subprocess
    import subprocess

def query_rag(question: str, k: int = 3) -> list:
    """
    Query the flat‑file RAG and return list of (content, metadata) tuples.
    """
    try:
        # Try importing directly
        from rag_flat import FlatRAG
        rag = FlatRAG()
        return rag.query(question, k)
    except ImportError:
        # Fallback: call script via subprocess
        cmd = [sys.executable, "rag_flat.py", "--query", question]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(__file__))
        # Parse output (simplistic)
        lines = result.stdout.split("\n")
        chunks = []
        current = {}
        content = []
        for line in lines:
            if line.startswith("File:"):
                current["file"] = line.split(": ")[1]
            elif line.startswith("Heading:"):
                current["heading"] = line.split(": ")[1]
            elif line.startswith("Content:"):
                content.append(line.split(": ", 1)[1])
            elif line.startswith("--- Result"):
                if current and content:
                    chunks.append(("\n".join(content), current))
                    content = []
                    current = {}
        if current and content:
            chunks.append(("\n".join(content), current))
        return chunks

def get_insights(topic: str) -> str:
    """
    Get formatted insights for a given topic.
    Returns a markdown string suitable for inclusion in reports.
    """
    results = query_rag(topic, k=2)
    if not results:
        return ""
    
    lines = ["**📚 Knowledge Base Insights:**"]
    for i, (content, meta) in enumerate(results):
        source = f"{meta.get('file', 'unknown')} › {meta.get('heading', 'root')}"
        # Truncate content
        if len(content) > 200:
            content = content[:200] + "..."
        lines.append(f"{i+1}. {content}")
        lines.append(f"   *Source: {source}*")
        lines.append("")
    
    return "\n".join(lines)

if __name__ == "__main__":
    # Test
    if len(sys.argv) > 1:
        print(get_insights(sys.argv[1]))
    else:
        print("Usage: python rag_query.py \"your question\"")