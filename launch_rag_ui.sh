#!/bin/bash
# Launch the Streamlit RAG UI

cd "$(dirname "$0")"

echo "🧠 Starting RAG Query UI..."
echo "Open http://localhost:8501 in your browser"
echo "Press Ctrl+C to stop"

streamlit run rag_ui.py