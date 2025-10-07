import os
import pickle
import faiss
from src.models.embedder import Embedder
from src.extract.extract_text import extract_text  
import re

class SemanticSearcher:
    """
    Performs semantic search using a FAISS index built by SemanticIndexer.
    """

    def __init__(self, index_dir="semantic_index"):
        self.index_dir = index_dir
        self.index_path = os.path.join(index_dir, "faiss.index")
        self.meta_path = os.path.join(index_dir, "metadata.pkl")
        self.embedder = Embedder()
        self.index = None
        self.metadata = []

        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self.load_index()
        else:
            raise FileNotFoundError(
                f"No FAISS index found in '{index_dir}'. "
                f"Please run SemanticIndexer.build_index() first."
            )

    def load_index(self):
        print("[FAISS] Loading semantic index for searching...")
        self.index = faiss.read_index(self.index_path)
        with open(self.meta_path, "rb") as f:
            self.metadata = pickle.load(f)
        print(f"[FAISS] Loaded {len(self.metadata)} documents.")

    def extract_snippet(self, text, query, snippet_len=50):
        """Extract a snippet around the first occurrence of the query."""
        match = re.search(re.escape(query), text, re.IGNORECASE)
        if not match:
            return text[:snippet_len*2] + ("..." if len(text) > snippet_len*2 else "")
        start = max(match.start() - snippet_len, 0)
        end = min(match.end() + snippet_len, len(text))
        return text[start:end]

    def search(self, query, top_k=5):
        """
        Perform a semantic search for the given query string.
        Returns the top_k most similar documents with title, snippet, and scores.
        """
        query_vec = self.embedder.encode(query)
        scores, indices = self.index.search(query_vec, top_k)

        results = []
        for rank, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx == -1:
                continue

            pdf_path = self.metadata[idx]
            title = os.path.basename(pdf_path)
            full_text = extract_text(pdf_path)  # returns full PDF text
            snippet = self.extract_snippet(full_text, query)

            results.append({
                "rank": rank + 1,
                "path": pdf_path,
                "title": title,
                "content": snippet,
                "score": float(score)
            })

        return results
