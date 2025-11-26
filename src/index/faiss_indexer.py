# src/index/faiss_indexer.py
import faiss
import numpy as np
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import os
import json  # <-- 1. Make sure json is imported
from pathlib import Path  # <-- 2. Make sure pathlib is imported
from src.utils.text_cleaner import clean_text_start

class FAISSIndexer:
    """
    A self-contained FAISS indexer that handles embedding generation,
    advanced index configuration, storage, and searching.
    """
    def __init__(
            self,
            embedding_model_name: str = "all-MiniLM-L6-v2",
            index_config: Optional[Dict] = None,
    ):
        print(f"Loading embedding model: {embedding_model_name}")
        self.model = SentenceTransformer(embedding_model_name)
        self.dim = self.model.get_sentence_embedding_dimension()

        self.metadata: List[Dict] = []

        if index_config is None:
            self.config = {"index_type": "flat_l2"}
        else:
            self.config = index_config

        self.index = self._build_index()
        self.is_trained = False

    def _build_index(self):
        """Builds a FAISS index based on the config."""
        index_type = self.config.get("index_type", "flat_l2").lower()

        if index_type == "flat_l2":
            print(f"Building IndexFlatL2 (dim={self.dim})")
            return faiss.IndexFlatL2(self.dim)

        elif index_type == "ivfpq":
            nlist = self.config.get("nlist", 100)
            m = self.config.get("m", 8)
            bits = self.config.get("bits", 8)

            print(f"Building IndexIVFPQ (nlist={nlist}, m={m}, bits={bits})")
            quantizer = faiss.IndexFlatL2(self.dim)
            index = faiss.IndexIVFPQ(quantizer, self.dim, nlist, m, bits)
            return index

        else:
            raise ValueError(f"Unknown index_type: {index_type}")

    def _embed(self, texts: List[str]) -> np.ndarray:
        """Helper to create and normalize embeddings."""
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return np.array(embeddings).astype('float32')

    def add_chunks(self, chunks: List[Dict]):
        """
        Embeds and adds text chunks to the index.
        chunks: List of dicts, each must have 'heading' and 'text'.
        """
        if not chunks:
            return

        texts = [chunk["text"] for chunk in chunks]
        print(f"Generating {len(texts)} embeddings...")
        embeddings = self._embed(texts)

        if self.config.get("index_type") == "ivfpq" and not self.is_trained:
            print(f"Training IVFPQ index on {len(embeddings)} vectors...")
            self.index.train(embeddings)
            self.is_trained = True
            print("Training complete.")

        print("Adding embeddings to index...")
        self.index.add(embeddings)
        self.metadata.extend(chunks)

    # src/index/faiss_indexer.py
    # ... (all other code is the same) ...

    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Embeds a query string and returns top_k results.
        """
        if self.index.ntotal == 0:
            return [] # Index is empty

        query_emb = self._embed([query])
        distances, indices = self.index.search(query_emb, top_k)

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx == -1: # -1 means no result (e.g., in IVFPQ)
                continue
            if idx < len(self.metadata):

                # Get the full chunk data from our metadata store
                chunk_data = self.metadata[idx]

                heading = clean_text_start(chunk_data.get("heading", "No Heading"))
                text = clean_text_start(chunk_data.get("text", ""))

                results.append({
                    "heading": heading,
                    "text": text,
                    "distance": float(dist),

                    # This maps your extractor's keys to the frontend's keys
                    "file_name": chunk_data.get("source_file", "Unknown File"),
                    "page_number": chunk_data.get("page_number", 1)
                })
        return results

    # --- 3. THE FIX IS HERE ---
    def save(self, file_path: Path): # Change type hint to Path
        """Saves the index and metadata."""
        # Cast the Path object to a string for the C++ bindings
        index_file_str = str(file_path)
        # Use pathlib's clean way to get the metadata file path
        meta_file_path = file_path.with_suffix(".meta.json")

        print(f"Saving FAISS index to {index_file_str}")
        faiss.write_index(self.index, index_file_str) # Use the string

        print(f"Saving metadata to {meta_file_path}")
        with open(meta_file_path, "w") as f:
            json.dump({
                "metadata": self.metadata,
                "config": self.config,
                "dim": self.dim,
                "is_trained": self.is_trained,
            }, f)

    # --- 4. AND HERE ---
    def load(self, file_path: Path): # Change type hint to Path
        """Loads an index and its metadata."""
        # Cast the Path object to a string for the C++ bindings
        index_file_str = str(file_path)
        # Use pathlib's clean way to get the metadata file path
        meta_file_path = file_path.with_suffix(".meta.json")

        if not os.path.exists(index_file_str) or not os.path.exists(meta_file_path):
            raise FileNotFoundError(f"Cannot find index files: {index_file_str} or {meta_file_path}")

        print(f"Loading FAISS index from {index_file_str}")
        self.index = faiss.read_index(index_file_str) # Use the string

        print(f"Loading metadata from {meta_file_path}")
        with open(meta_file_path, "r") as f:
            data = json.load(f)

        self.metadata = data["metadata"]
        self.config = data["config"]
        self.dim = data["dim"]
        self.is_trained = data["is_trained"]

        if self.dim != self.model.get_sentence_embedding_dimension():
            raise ValueError(
                f"Model dim ({self.model.get_sentence_embedding_dimension()}) "
                f"does not match loaded index dim ({self.dim})"
            )
        print("Index and metadata loaded successfully.")