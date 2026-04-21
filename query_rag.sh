#!/bin/bash
# Simple wrapper to query the flat‑file RAG

cd "$(dirname "$0")"

if [ $# -eq 0 ]; then
    echo "Usage: $0 \"your question\""
    echo "Example: $0 \"What gold price is monitored?\""
    exit 1
fi

python rag_flat.py --query "$*"