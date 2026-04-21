# RAG Streamlit UI Guide

A clean web interface to query your flat‑file knowledge base.

## 🚀 Quick Start

```bash
cd ~/.openclaw/workspace
./launch_rag_ui.sh
```

Then open **http://localhost:8501** in your browser.

## 📋 Features

### 1. **Query Interface**
- Natural language search across all topic files
- Adjustable number of results (1‑10)
- Sample queries for quick testing
- Topic filtering (Finance, Tech, Projects, General)

### 2. **Results Display**
- Clean card‑based layout
- Source file and heading badges
- Semantic distance scores
- Expandable raw metadata

### 3. **Sidebar Management**
- View topic file contents
- See index statistics
- Rebuild index with one click
- Update from memory files

### 4. **System Info**
- File structure visualization
- Index status
- Last update timestamp

## 🗂️ File Structure

```
workspace/
├── rag_ui.py                 # Streamlit app
├── launch_rag_ui.sh          # Launch script
├── rag_flat.py              # RAG backend
├── rag_query.py             # Query module
├── update_rag_from_memory_v2.py # Auto‑updater
├── rag_daily_update.sh      # Daily update script
├── heartbeat_rag.py         # Heartbeat integration
└── memory/topics/           # Your knowledge base
    ├── finance.md
    ├── tech.md
    ├── projects.md
    └── general.md
```

## 🔧 Installation & Dependencies

Already installed via:
```bash
pip install streamlit sentence-transformers faiss-cpu numpy
```

If missing, run:
```bash
pip install -r requirements_streamlit.txt
```

## 🕐 Scheduled Updates

The knowledge base auto‑updates via:

1. **Cron** (daily at 2 AM) – see `crontab.rag`
2. **Heartbeat** (every 12h) – configured in `HEARTBEAT.md`

Manual update:
```bash
python update_rag_from_memory_v2.py
python rag_flat.py --rebuild
```

## 🎯 Example Queries

- "What forex pairs are monitored?"
- "Tell me about FedWatch integration"
- "What gold price is tracked?"
- "Show me home loan rates"
- "What Python scripts exist?"
- "Summarize project decisions"

## 🖥️ Running in Background

```bash
# Run in background
nohup ./launch_rag_ui.sh > rag_ui.log 2>&1 &

# Check if running
ps aux | grep streamlit

# Stop
pkill -f "streamlit run rag_ui"
```

## 🔒 Security Notes

- The UI runs locally on `localhost:8501`
- No authentication by default (local use only)
- All data stays in your workspace
- Consider adding authentication if exposing to network

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install streamlit
```

### "FAISS index not found"
```bash
python rag_flat.py --rebuild
```

### "No topic files"
```bash
python update_rag_from_memory_v2.py
```

### Streamlit crashes on launch
Check logs:
```bash
streamlit run rag_ui.py --server.port 8501 --logger.level debug
```

### Slow queries
- Reduce chunk size in `rag_flat.py`
- Use smaller embedding model
- Limit number of results

## 📈 Extending

### Add new topic files
1. Create `memory/topics/newtopic.md`
2. Add content with markdown headings
3. Rebuild index via sidebar button

### Customize UI
Edit `rag_ui.py`:
- Change colors in CSS section
- Add new sample queries
- Modify layout

### Integrate with other apps
Import `rag_query.py`:
```python
from rag_query import get_insights
insights = get_insights("your question")
```

## 📞 Support

- OpenClaw docs: https://docs.openclaw.ai
- Community: https://discord.com/invite/clawd
- Issues: https://github.com/openclaw/openclaw

---

**Enjoy your personal knowledge base!** 🧠