#!/usr/bin/env python3
"""
Lightweight RAG with flat topic files.
No compaction — each topic stays in its own markdown file.
Uses sentence-transformers and FAISS for local semantic search.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Dict
import pickle

import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

# Configuration
TOPICS_DIR = Path(__file__).parent / "memory" / "topics"
INDEX_FILE = Path(__file__).parent / "memory" / "faiss_index.bin"
METADATA_FILE = Path(__file__).parent / "memory" / "chunk_metadata.pkl"
MODEL_NAME = "all-MiniLM-L6-v2"  # Lightweight, good enough for semantic search

class FlatRAG:
    def __init__(self, rebuild=False):
        self.model = SentenceTransformer(MODEL_NAME)
        self.index = None
        self.chunks = []
        self.metadata = []  # Each entry: {"file": str, "chunk_id": int, "heading": str}
        
        if rebuild or not INDEX_FILE.exists():
            print("Building FAISS index from topic files...")
            self._build_index()
        else:
            print("Loading existing FAISS index...")
            self._load_index()
    
    def _chunk_file(self, filepath: Path) -> List[Tuple[str, Dict]]:
        """Split a markdown file into logical chunks (by heading)."""
        content = filepath.read_text(encoding="utf-8")
        chunks = []
        
        # Split by markdown headings (##, ###)
        parts = re.split(r'\n(##+ .+)', content)
        
        current_heading = "root"
        for i, part in enumerate(parts):
            if i == 0:
                # First part is content before any heading
                if part.strip():
                    chunks.append((part.strip(), {"file": filepath.name, "heading": "root"}))
            elif i % 2 == 1:
                # This is a heading
                current_heading = part.strip()
            else:
                # This is content under the previous heading
                if part.strip():
                    chunks.append((part.strip(), {"file": filepath.name, "heading": current_heading}))
        
        # If no headings, treat whole file as one chunk
        if not chunks and content.strip():
            chunks.append((content.strip(), {"file": filepath.name, "heading": "root"}))
        
        return chunks
    
    def _build_index(self):
        """Read all topic files, chunk, embed, and build FAISS index."""
        self.chunks = []
        self.metadata = []
        
        # Collect all .md files in topics directory
        topic_files = list(TOPICS_DIR.glob("*.md"))
        if not topic_files:
            raise FileNotFoundError(f"No topic files found in {TOPICS_DIR}")
        
        all_embeddings = []
        for filepath in topic_files:
            print(f"  Processing {filepath.name}...")
            file_chunks = self._chunk_file(filepath)
            for chunk_text, meta in file_chunks:
                self.chunks.append(chunk_text)
                self.metadata.append(meta)
        
        # Generate embeddings
        print(f"  Generating embeddings for {len(self.chunks)} chunks...")
        embeddings = self.model.encode(self.chunks, show_progress_bar=True)
        embeddings = np.array(embeddings).astype("float32")
        
        # Build FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)
        
        # Save index and metadata
        faiss.write_index(self.index, str(INDEX_FILE))
        with open(METADATA_FILE, "wb") as f:
            pickle.dump({"chunks": self.chunks, "metadata": self.metadata}, f)
        
        print(f"Index built with {len(self.chunks)} chunks from {len(topic_files)} files.")
    
    def _load_index(self):
        """Load existing FAISS index and metadata."""
        self.index = faiss.read_index(str(INDEX_FILE))
        with open(METADATA_FILE, "rb") as f:
            data = pickle.load(f)
            self.chunks = data["chunks"]
            self.metadata = data["metadata"]
        print(f"Loaded index with {len(self.chunks)} chunks.")
    
    def query(self, question: str, k: int = 3) -> List[Tuple[str, Dict]]:
        """Return top‑k relevant chunks with metadata."""
        query_embedding = self.model.encode([question])
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.chunks):
                results.append((
                    self.chunks[idx],
                    {**self.metadata[idx], "distance": float(dist)}
                ))
        return results
    
    def add_file(self, filepath: Path):
        """Add a new topic file to the index (incremental)."""
        print(f"Adding {filepath.name} to index...")
        file_chunks = self._chunk_file(filepath)
        
        new_chunks = []
        new_metadata = []
        new_embeddings = []
        
        for chunk_text, meta in file_chunks:
            new_chunks.append(chunk_text)
            new_metadata.append(meta)
            new_embeddings.append(self.model.encode([chunk_text])[0])
        
        # Update in‑memory structures
        self.chunks.extend(new_chunks)
        self.metadata.extend(new_metadata)
        
        # Update FAISS index
        new_embeddings = np.array(new_embeddings).astype("float32")
        self.index.add(new_embeddings)
        
        # Save updated index
        faiss.write_index(self.index, str(INDEX_FILE))
        with open(METADATA_FILE, "wb") as f:
            pickle.dump({"chunks": self.chunks, "metadata": self.metadata}, f)
        
        print(f"Added {len(new_chunks)} chunks from {filepath.name}.")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Flat‑file RAG query tool")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild index from scratch")
    parser.add_argument("--query", type=str, help="Query string")
    parser.add_argument("--k", type=int, default=3, help="Number of results")
    parser.add_argument("--add", type=str, help="Path to new topic file to add")
    args = parser.parse_args()
    
    rag = FlatRAG(rebuild=args.rebuild)
    
    if args.add:
        rag.add_file(Path(args.add))
    
    if args.query:
        print(f"\nQuery: {args.query}")
        results = rag.query(args.query, k=args.k)
        for i, (chunk, meta) in enumerate(results):
            print(f"\n--- Result {i+1} ---")
            print(f"File: {meta['file']}")
            print(f"Heading: {meta['heading']}")
            print(f"Distance: {meta['distance']:.4f}")
            print(f"Content: {chunk[:300]}...")
    
    if not args.query and not args.add:
        print("\nUsage examples:")
        print("  python rag_flat.py --query \"What forex pairs are monitored?\"")
        print("  python rag_flat.py --add memory/topics/new_topic.md")
        print("  python rag_flat.py --rebuild")

if __name__ == "__main__":
    main()