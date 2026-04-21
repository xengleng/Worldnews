# Flat‑File RAG Setup

Lightweight semantic search over topic‑based markdown files, avoiding compaction.

## Structure

```
memory/topics/
├── finance.md           # Stock, forex, gold, macro
├── tech.md              # Python scripts, APIs, tools
├── projects.md          # Project summaries, decisions
└── (add more as needed)
```

Each file contains markdown with headings. The RAG system chunks by heading.

## Files

- `rag_flat.py` – Main Python script (builds/loads FAISS index, queries)
- `query_rag.sh` – Bash wrapper for easy querying
- `memory/faiss_index.bin` – FAISS index (auto‑generated)
- `memory/chunk_metadata.pkl` – Chunk metadata (auto‑generated)

## Usage

### Build/Rebuild Index
```bash
python rag_flat.py --rebuild
```

### Query
```bash
python rag_flat.py --query "What forex pairs are monitored?"
# or
./query_rag.sh "What forex pairs are monitored?"
```

### Add New Topic File
```bash
python rag_flat.py --add memory/topics/new_topic.md
```

## How It Works

1. **Chunking**: Files are split by markdown headings (`##`, `###`).
2. **Embeddings**: Uses `all‑MiniLM‑L6‑v2` (sentence‑transformers) – small, fast, offline.
3. **Index**: FAISS for efficient similarity search.
4. **Metadata**: Each chunk remembers source file and heading.
5. **Incremental**: You can add new files without rebuilding the whole index.

## Maintenance

- Keep topic files focused (one topic per file).
- Use clear headings for better chunking.
- Rebuild index if you delete or heavily edit existing files.
- The index is stored in `memory/` – you can delete `.bin` and `.pkl` to force rebuild.

## Example Queries

- "What gold price is monitored?"
- "Which Python scripts exist?"
- "Tell me about FedWatch integration."
- "What Singapore stocks are tracked?"

## Integration with OpenClaw

You can call this from within OpenClaw sessions:

```python
import subprocess
result = subprocess.run(["python", "rag_flat.py", "--query", "your question"], capture_output=True, text=True)
```

Or schedule periodic updates via cron/heartbeat.

## Why Flat Files?

- **No compaction**: Each topic stays separate, easy to edit.
- **Transparent**: Everything is readable markdown.
- **Version‑friendly**: Git‑friendly plain text.
- **Lightweight**: No database server, just files + FAISS.