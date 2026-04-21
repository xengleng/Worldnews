#!/usr/bin/env python3
"""
Streamlit UI for querying your flat‑file RAG.
Run with: streamlit run rag_ui.py
"""

import streamlit as st
import sys
import os
from pathlib import Path
import time

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

st.set_page_config(
    page_title="RAG Query UI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #546E7A;
        margin-bottom: 2rem;
    }
    .result-card {
        background-color: #F5F7FA;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #1E88E5;
    }
    .source-badge {
        background-color: #E3F2FD;
        color: #1565C0;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.9rem;
        display: inline-block;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .distance-badge {
        background-color: #FFF3E0;
        color: #EF6C00;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        display: inline-block;
    }
    .stButton button {
        background-color: #1E88E5;
        color: white;
        font-weight: bold;
    }
    .topic-file {
        background-color: #E8F5E9;
        padding: 0.5rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🧠 RAG Query UI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Query your flat‑file knowledge base (finance, tech, projects)</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📊 System Info")
    
    # Show topic files
    topics_dir = Path(__file__).parent / "memory" / "topics"
    if topics_dir.exists():
        topic_files = list(topics_dir.glob("*.md"))
        st.write(f"**Topic files:** {len(topic_files)}")
        for tf in topic_files:
            size_kb = tf.stat().st_size / 1024
            with st.expander(f"📄 {tf.name} ({size_kb:.1f} KB)"):
                content = tf.read_text(encoding="utf-8")[:500]
                st.text(content)
                if len(content) == 500:
                    st.caption("(truncated)")
    else:
        st.warning("No topic files found. Run the update script first.")
    
    # Index stats
    index_file = Path(__file__).parent / "memory" / "faiss_index.bin"
    if index_file.exists():
        st.success("✅ FAISS index found")
        # Try to get chunk count
        try:
            import pickle
            meta_file = Path(__file__).parent / "memory" / "chunk_metadata.pkl"
            if meta_file.exists():
                with open(meta_file, "rb") as f:
                    data = pickle.load(f)
                    st.write(f"**Chunks:** {len(data.get('chunks', []))}")
        except:
            pass
    else:
        st.error("❌ No FAISS index. Run `python rag_flat.py --rebuild`")
    
    st.divider()
    
    # Actions
    st.header("⚙️ Actions")
    if st.button("🔄 Rebuild Index", use_container_width=True):
        with st.spinner("Rebuilding index..."):
            import subprocess
            result = subprocess.run(
                [sys.executable, "rag_flat.py", "--rebuild"],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(__file__)
            )
            if result.returncode == 0:
                st.success("Index rebuilt successfully!")
                st.text(result.stdout[-500:])
            else:
                st.error("Rebuild failed")
                st.text(result.stderr)
    
    if st.button("📥 Update from Memory", use_container_width=True):
        with st.spinner("Updating from memory files..."):
            import subprocess
            result = subprocess.run(
                [sys.executable, "update_rag_from_memory_v2.py"],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(__file__)
            )
            if result.returncode == 0:
                st.success("Update completed!")
                st.text(result.stdout[-500:])
            else:
                st.error("Update failed")
                st.text(result.stderr)
    
    st.divider()
    st.caption("Built with OpenClaw • Flat‑file RAG")

# Main content
col1, col2 = st.columns([3, 1])

with col1:
    # Query input
    query = st.text_input(
        "🔍 Enter your question:",
        placeholder="e.g., What forex pairs are monitored?",
        key="query_input"
    )
    
    # Query options
    col_a, col_b = st.columns(2)
    with col_a:
        k_results = st.slider("Number of results", 1, 10, 3)
    with col_b:
        show_raw = st.checkbox("Show raw metadata", value=False)
    
    # Sample queries
    st.caption("Try these:")
    sample_cols = st.columns(4)
    samples = [
        ("forex pairs", "What forex pairs are monitored?"),
        ("gold price", "What gold price is tracked?"),
        ("FedWatch", "Tell me about FedWatch integration"),
        ("home loan", "What are current home loan rates?"),
    ]
    for i, (label, sample) in enumerate(samples):
        with sample_cols[i]:
            if st.button(label, use_container_width=True):
                st.session_state.query_input = sample
                st.rerun()

with col2:
    # Topic filter
    st.write("**Filter by topic:**")
    topics = ["All", "Finance", "Tech", "Projects", "General"]
    selected_topic = st.radio(
        "Topics",
        topics,
        index=0,
        label_visibility="collapsed"
    )

# Query execution
if query:
    with st.spinner(f"Searching for '{query}'..."):
        try:
            # Import RAG module
            from rag_flat import FlatRAG
            
            # Load RAG
            rag = FlatRAG()
            
            # Query
            start_time = time.time()
            results = rag.query(query, k=k_results)
            elapsed = time.time() - start_time
            
            # Display results
            st.success(f"Found {len(results)} results in {elapsed:.2f}s")
            
            for i, (chunk, meta) in enumerate(results):
                # Apply topic filter
                file_name = meta.get("file", "")
                if selected_topic != "All":
                    topic_map = {
                        "Finance": "finance.md",
                        "Tech": "tech.md",
                        "Projects": "projects.md",
                        "General": "general.md"
                    }
                    if file_name != topic_map.get(selected_topic, ""):
                        continue
                
                with st.container():
                    st.markdown(f'<div class="result-card">', unsafe_allow_html=True)
                    
                    # Header with badges
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"### 📄 Result {i+1}")
                    with col2:
                        st.markdown(f'<div class="distance-badge">Distance: {meta.get("distance", 0):.4f}</div>', unsafe_allow_html=True)
                    
                    # Source badge
                    source = f"{file_name} › {meta.get('heading', 'root')}"
                    st.markdown(f'<div class="source-badge">{source}</div>', unsafe_allow_html=True)
                    
                    # Content
                    st.markdown("**Content:**")
                    st.write(chunk)
                    
                    if show_raw:
                        with st.expander("Raw metadata"):
                            st.json(meta)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            
            if not results:
                st.info("No results found. Try a different query or rebuild the index.")
                
        except ImportError as e:
            st.error(f"Failed to import RAG module: {e}")
            st.info("Make sure `rag_flat.py` is in the same directory and dependencies are installed.")
        except Exception as e:
            st.error(f"Query failed: {e}")
            st.code(str(e))

# Footer
st.divider()
st.markdown("### 📁 File Structure")
st.code("""
memory/topics/
├── finance.md           # Stock, forex, gold, macro
├── tech.md              # Python scripts, APIs, tools
├── projects.md          # Project summaries, decisions
└── general.md           # Other notes
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Topic Files", len(topic_files) if 'topic_files' in locals() else 0)
with col2:
    st.metric("Index", "Ready" if index_file.exists() else "Missing")
with col3:
    st.metric("Last Update", time.ctime(os.path.getmtime(index_file)) if index_file.exists() else "Never")

# Auto‑refresh note
st.caption("💡 The index updates automatically via cron/heartbeat. Use 'Rebuild Index' if you've edited topic files manually.")